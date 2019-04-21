# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, Http404
from background_task import background
from background_task.models import Task
from background_task.models_completed import CompletedTask
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.conf import settings
from core.models import *
import pdb
import datetime
import requests
from itertools import chain
import json
import os
import base64
# from Crypto.Cipher import AES
#import requests
import ast
import random
import pyPdf
import re
import xlsxwriter
import unidecode
from dbfpy import dbf
import wget
from IPython import embed
from core.extraction import extraction
from core.utils import utils
from core.download import download
import traceback
import subprocess


def getPDFContent(path):
    content = ""
    try:
        retcode = subprocess.check_output("ruby pdf_reader.rb '" + path + "'", shell=True)
        print retcode
    except OSError as e:
        print("Execution failed:", e)
    content = retcode
    # Collapse whitespace
    text = content.decode('utf-8')
    text = text.split("Boletin Oficial de Mineria")[::-1][0]
    return text

def getPDFContent2(path):
    content = ""
    # Load PDF into pyPDF
    pdf = pyPdf.PdfFileReader(file(path, "rb"))
    # Iterate pages
    for i in range(0, pdf.getNumPages()):
        # Extract text from page and add to content
        for line in pdf.getPage(i).extractText().splitlines():
            content += unidecode.unidecode(line) + " \n"
    # Collapse whitespace
    text = content
    return text

def login_user(request):
    template_name = 'login.html'
    logout(request)
    data = {}
    username = password = ''
    if request.POST:
        username = request.POST['Username']
        password = request.POST['Password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse_lazy('index'))
#            else :
#                messages.warning(request, ('Usuario inactivo!'))
#        else :
#            messages.error(request, ('Usuario no existe!'))
        data["no_login"] = "ok"
    return render(request, template_name, data)


@login_required(login_url='/')
def index(request):
    template_name = 'index.html'
    data = {}
    return render(request, template_name, data)

@background(schedule=5)
def crear_pdf_de_boletin(request):
    cve_downloaded = 0
    response = {}
    tipos = ["PEDIMENTOS MINEROS","MANIFESTACIONES MINERAS","SOLICITUDES DE MENSURA","EXTRACTOS ARTICULO 83","CITACIONES A JUNTA Y ASAMBLEA", "EXTRACTOS DE SENTENCIA DE EXPLORACION","EXTRACTOS DE SENTENCIA DE EXPLOTACION","PRORROGAS CONCESION DE EXPLORACION","RENUNCIAS DE CONCESION MINERA","ACUERDOS JUNTA DE ACCIONISTAS","NOMINAS DE CONCESIONES MINERAS PARA REMATE","NOMINA BENEFICIADOS PATENTE REBAJADA","NOMINA DE CONCESIONES ART. 90","VIGENCIA INSCRIPCION ACTAS DE MENSURA","OTRAS PUBLICACIONES","EXTRACTOS DE SENTENCIA DE EXPLORACION"]
    print request
    os.system('wget -U "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4" ' + request["archivo"])
    name = request["archivo"].split("/")[::-1]
    archivo=str(name[0])
    text = getPDFContent(archivo)
    for x in tipos:
        if x in text:
            text = text.replace(x,"SEPARADOR DE TIPOS DE MINERIA "+x+"TERMINO SEPARADOR")
    datos = text.split("SEPARADOR DE TIPOS DE MINERIA ")
    datos.pop(0)
    codigo_diario = request["archivo"].split("/")
    format_fecha = codigo_diario[4] + "/" + codigo_diario[5] + "/" + codigo_diario[6]
    diario = Diario.objects.filter(codigo=name[0].split(".pdf")[0],fecha=format_fecha)[0]
    region = ''
    concesion = ''
    concesiona = ''
    try:
        for y in datos:
            tipo = y.split("TERMINO SEPARADOR")[0]

            ###### WORKING ON ITERATE BY REGION #######
            for inx, reg_block in enumerate(y.split('REGIÓN '.decode('utf-8'))):
                if inx == 0:
                    pass
                else:
                    current_region = reg_block.split('Provincia')[0]
                    current_region = current_region.split('\n')[0]
                    codigo_region = current_region
                    current_prov = current_region.replace("\n", "")
                    region_to_compare = current_region.replace("\n", "").lower()
                    for region in utils.regions():
                        if region['nombre'].lower().decode("raw_unicode_escape") in region_to_compare:
                            codigo_region = region['codigo']
                            
                    reg_block.replace('Provincia de ', 'Provincia de xProv')

                    ###### WORKING ON ITERATE BY PROVINCE #######
                    for inx2, reg_prov in enumerate(reg_block.split('Provincia de ')):
                        if inx2 == 0:
                            pass
                        else:
                            current_prov = reg_prov.split('xProv')[0].split('\n')[0]
                            current_prov = current_prov.replace("\n", "")

                            for x in reg_prov.split(")"):
                                if "CVE:" in x:
                                    ######### MUST: improve extraction of cve concesion and else,
                                    ######### when it is in the first row of new page
                                    try:
                                        print "NEW CVE"
                                        temp_x = x
                                        if current_prov in x:
                                            x = temp_x.split(current_prov)[1].split("(")[1].replace(" ","")
                                            cve = x.split("CVE:")[1]
                                            concesion = temp_x.split(current_prov)[1].split('(')[0].split('/')[0]
                                            concesiona = temp_x.split(current_prov)[1].split('(')[0].split('/')[1]
                                        else:
                                            if "sitio web www.diarioficial.cl" in x:
                                                x = temp_x.split('sitio web www.diarioficial.cl')[1].split("(")[1].replace(" ","")
                                                cve = x.split("CVE:")[1]
                                                concesion = temp_x.split('sitio web www.diarioficial.cl')[1].split('(')[0].split('/')[0]
                                                concesiona = temp_x.split('sitio web www.diarioficial.cl')[1].split('(')[0].split('/')[1]
                                            else:
                                                x = x.split("CVE:")[1].split("(")[0].replace(" ","")
                                                cve = x.split("CVE:")[0]
                                                concesion = temp_x.split('(')[0].split('/')[0]
                                                concesiona = temp_x.split('(')[0].split('/')[1]

                                        concesion = concesion.split("\n")
                                        concesion = concesion[len(concesion) - 1]
                                        concesion = concesion.replace("\n", "").strip()
                                        concesiona = concesiona.replace("\n", "").strip()
                                        os.system('wget -U "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4" ' + "http://www.diariooficial.interior.gob.cl/publicaciones/"+ str(name[4]) +"/" +str(name[3]) +"/" + str(name[2]) + "/" + name[0].split(".pdf")[0] + "/07/" + str(cve) + ".pdf")
                                        url = "http://www.diariooficial.interior.gob.cl/publicaciones/"+ str(name[4]) +"/" +str(name[3]) +"/" + str(name[2]) + "/" + name[0].split(".pdf")[0] + "/07/" + str(cve) + ".pdf"
                                        aux = Registro_Mineria.objects.create(region=codigo_region,provincia=current_prov,concesion=concesion,concesiona=concesiona,diario=diario,tipo_tramite=tipo,url=url,cve=cve,texto=getPDFContent(str(cve)+".pdf"))
                                        aux.save()
                                        cve_downloaded+=1
                                        os.system('rm ' + cve+".pdf")
                                        os.system('rm ' + cve+".txt")

                                        print "END OF CVE SUCESSFULLY"
                                    except Exception as e:
                                        print 'Error raised: %s  (%s)' % (e.message, type(e))
                                        print "END OF CVE WITH ERROR: " + cve
                                        trace_back = traceback.format_exc()
                                        message = str(e)+ " " + str(trace_back)
                                        print message
                                        os.system('rm ' + cve+".pdf")
                                        os.system('rm ' + cve+".txt")
                                        pass
                ###### STOP WORKING ON ITERATE BY PROVINCE #######
        ###### STOP WORKING ON ITERATE BY REGION #######
    except Exception as e:
        trace_back = traceback.format_exc()
        message = str(e)+ " " + str(trace_back)
        print message      

    os.system('rm ' + name[0])
    os.system('rm ' + name[0].split('.')[0] +".txt")
    data = {}
    data["total_cve"] = str(cve_downloaded)
    data["numero_registro"] = "1"

@login_required(login_url='/')
def descargar_boletin(request):
    template_name = 'Historic_Data.html'
    data = {}
    name = request.POST["archivo"].split("/")[::-1]
    codigo_diario = request.POST["archivo"].split("/")
    format_fecha = codigo_diario[4] + "/" + codigo_diario[5] + "/" + codigo_diario[6]
    diario, created = Diario.objects.get_or_create(codigo=name[0].split(".pdf")[0],fecha=format_fecha)
    if created:
        crear_pdf_de_boletin(request.POST)
        data["alert"] = "Se esta descargando la informacion del CVE"
        return render(request, template_name, data)
    else:
        data["alert"] = "El diario ya ha sido descargado con anterioridad."
        return render(request, template_name, data)
        

def Historic_Data(request):
    template_name = "Historic_Data.html"
    data = {}
    dailys = Diario.objects.all()
    data["diario"] = dailys
    # data["total_diarios"] = len(dailys)
    if request.POST:
        diario = Diario.objects.get(pk=request.POST["fecha"])
        solicitudes = diario.registro_mineria_set.all()
        data["solicitudes"] = solicitudes
        data["fecha"] = diario.pk
        data["total_diarios"] = len(solicitudes)
    return render(request, template_name, data)

@background(schedule=5)
def scrap_data(request):
    print "Running background proccess"
    codes = []
    diario = Diario.objects.get(pk=int(request["pk_diario_2"]))
    f_boletin = diario.fecha
    boletin = diario.codigo
    for x in diario.registro_mineria_set.all():
        x.f_boletin = f_boletin
        x.boletin = boletin
        patron = re.compile("[1-9]\.\d\d\d[.,]\d\d\d[^-]")
        patron2 = re.compile("[1-9]\d\d\d\d\d\d[^-]")
        if patron.search(x.texto):
            x.nortepi = patron.search(x.texto).group()
            x.nortepi = x.nortepi[:len(x.nortepi) - 1]
            x.nortepi = x.nortepi.replace(".","")
            x.nortepi = x.nortepi.replace(",","").upper()
        elif patron2.search(x.texto):
            x.nortepi = patron2.search(x.texto).group()
            x.nortepi = x.nortepi[:len(x.nortepi) - 1]
            x.nortepi = x.nortepi.replace(".","")
            x.nortepi = x.nortepi.replace(",","").upper()
        else:
            x.nortepi = "No se detecta nortepi"
        patron = re.compile("[^d.]\d\d\d[.,]\d\d\d[^d]")
        patron2 = re.compile("[^d.]\d\d\d\d\d\d[^d]")
        if patron.search(x.texto):
            x.estepi = patron.search(x.texto).group()
            x.estepi = x.estepi[:len(x.estepi) - 1]
            x.estepi = x.estepi.replace(".","")
            x.estepi = x.estepi[1:]
            x.estepi = x.estepi.replace(",","").upper()
        elif patron2.search(x.texto):
            x.estepi = patron2.search(x.texto).group()
            x.estepi = x.estepi[:len(x.estepi) - 1]
            x.estepi = x.estepi.replace(".","")
            x.estepi = x.estepi[1:]
            x.estepi = x.estepi.replace(",","").upper()
        else:
            x.COORE_APRO = "No se detecta estepi"
        x.cpu = "0"
        x.save()
        if x.tipo_tramite=="EXTRACTOS DE SENTENCIA DE EXPLORACION" or x.tipo_tramite=="EXTRACTOS DE SENTENCIA DE EXPLOTACION":
            extraction.extraerConcesiones(x)
        if x.tipo_tramite=="PEDIMENTOS MINEROS":
            extraction.extraerPedimentos(x)
        if x.tipo_tramite=="MANIFESTACIONES MINERAS":
            extraction.extraerManifestaciones(x)
        if x.tipo_tramite=="SOLICITUDES DE MENSURA":
            extraction.extraerMensuras(x)
    print "Run background proccess end"

def Obtener_Datos_General(request):
    print "Starting to loocking for data"
    template_name = "Historic_Data.html"
    scrap_data(request.POST)
    data = {}
    data["alert"] = "Se esta extrayendo la informacion de los CVE. Este proceso podria tardar un momento."
    data["diario"] = Diario.objects.all()
    return render(request, template_name, data)

def get_datos(request):
    response = {}
    registro = Registro_Mineria.objects.get(pk=int(request.POST["pk"]))
    response["BOLETIN"] = registro.boletin
    response["F_BOLETIN"] = registro.f_boletin
    response["TIPO_CONCE"] = registro.tipo_conce
    response["CONCESION"] = registro.concesion
    response["CONCESIONA"] = registro.concesiona
    response["REPRESENTA"] = registro.representa
    response["DIRECCION"] = registro.direccion
    response["ROLMINERO"] = registro.rolminero
    response["F_SENTENC1"] = registro.f_sentenc1
    response["F_SENTENC2"] = registro.f_sentenc2
    response["F_PUBEXT"] = registro.f_pubext
    response["F_INSCMIN"] = registro.f_inscmin
    response["FOJAS"] = registro.fojas
    response["NUMERO"] = registro.numero
    response["YEAR"] = registro.year
    response["CIUDAD"] = registro.ciudad
    response["JUZGADO"] = registro.juzgado
    response["ROLJUZ"] = registro.roljuz
    response["IND_METAL"] = registro.ind_metal
    response["REGION"] = registro.region
    response["PROVINCIA"] = registro.provincia
    response["COMUNA"] = registro.comuna
    response["LUGAR"] = registro.lugar
    response["TIPO_UTM"] = registro.tipo_utm
    response["NORTEPI"] = registro.nortepi
    response["ESTEPI"] = registro.estepi
    response["VERTICES"] = registro.vertices
    response["HA_PERT"] = registro.ha_pert
    response["HECTAREAS"] = registro.hectareas
    response["OBSER"] = registro.obser
    response["DATUM"] = registro.datum
    response["F_PRESTRIB"] = registro.f_prestrib
    response["ARCHIVO"] = registro.archivo
    response["CORTE"] = registro.corte
    response["HUSO"] = registro.huso
    response["EDITOR"] = registro.editor
    response["CVE"] = registro.cve
    response["TIPO_TRAMITE"] = registro.tipo_tramite
    response["N_SCARASUP"] = registro.n_scarasup
    response["E_OCARASUP"] = registro.e_ocarasup
    response["F_PRESENTA"] = registro.f_presenta
    response["F_RESOLUCI"] = registro.f_resoluci
    response["F_INSCRIBE"] = registro.f_inscribe
    response["CARTAIGM"] = registro.cartaigm
    response["PED_ASOC"] = registro.ped_asoc
    response["FECHAPED"] = registro.fechaped
    response["ROLPED"] = registro.rolped
    response["TIPOCOORD"] = registro.tipocoord
    response["NORTE"] = registro.norte
    response["MTSN"] = registro.mtsn
    response["SUR"] = registro.sur
    response["MTSS"] = registro.mtss
    response["ESTE"] = registro.este
    response["MTSE"] = registro.mtse
    response["OESTE"] = registro.oeste
    response["MTSO"] = registro.mtso
    response["F_SOLICITA"] = registro.f_solicita
    response["F_PRESMAN"] = registro.f_presman
    response["F_MENSURA"] = registro.f_mensura
    response["N1"] = registro.n1
    response["HA1"] = registro.ha1
    response["N_S1"] = registro.n_s1
    response["E_O1"] = registro.e_o1
    response["N2"] = registro.n2
    response["HA2"] = registro.ha2
    response["N_S2"] = registro.n_s2
    response["E_O2"] = registro.e_o2
    response["N3"] = registro.n3
    response["HA3"] = registro.ha3
    response["N_S3"] = registro.n_s3
    response["E_O3"] = registro.e_o3
    response["N4"] = registro.n4
    response["HA4"] = registro.ha4
    response["N_S4"] = registro.n_s4
    response["E_O4"] = registro.e_o4
    response["IND_VIGE"] = registro.ind_vige
    response["RAZON"] = registro.razon
    response["PERITO"] = registro.perito
    response["OPOSICION"] = registro.oposicion
    response["CPU"] = registro.cpu
    return HttpResponse(
        json.dumps(response),
        content_type="application/json"
        )

def actualizar_datos(request):
    registro = Registro_Mineria.objects.get(pk=request.POST["pk"])
    registro.boletin = request.POST["BOLETIN"]
    registro.f_boletin = request.POST["F_BOLETIN"]
    registro.tipo_conce = request.POST["TIPO_CONCE"]
    registro.concesion = request.POST["CONCESION"]
    registro.concesiona = request.POST["CONCESIONA"]
    registro.representa = request.POST["REPRESENTA"]
    registro.direccion = request.POST["DIRECCION"]
    registro.rolminero = request.POST["ROLMINERO"]
    registro.f_sentenc1 = request.POST["F_SENTENC1"]
    registro.f_sentenc2 = request.POST["F_SENTENC2"]
    registro.f_pubext = request.POST["F_PUBEXT"]
    registro.f_inscmin = request.POST["F_INSCMIN"]
    registro.fojas = request.POST["FOJAS"]
    registro.numero = request.POST["NUMERO"]
    registro.year = request.POST["YEAR"]
    registro.ciudad = request.POST["CIUDAD"]
    registro.juzgado = request.POST["JUZGADO"]
    registro.roljuz = request.POST["ROLJUZ"]
    registro.ind_metal = request.POST["IND_METAL"]
    registro.region = request.POST["REGION"]
    registro.provincia = request.POST["PROVINCIA"]
    registro.comuna = request.POST["COMUNA"]
    registro.lugar = request.POST["LUGAR"]
    registro.tipo_utm = request.POST["TIPO_UTM"]
    registro.nortepi = request.POST["NORTEPI"]
    registro.estepi = request.POST["ESTEPI"]
    registro.vertices = request.POST["VERTICES"]
    registro.ha_pert = request.POST["HA_PERT"]
    registro.hectareas = request.POST["HECTAREAS"]
    registro.obser = request.POST["OBSER"]
    registro.datum = request.POST["DATUM"]
    registro.f_prestrib = request.POST["F_PRESTRIB"]
    registro.archivo = request.POST["ARCHIVO"]
    registro.corte = request.POST["CORTE"]
    registro.huso = request.POST["HUSO"]
    registro.editor = request.POST["EDITOR"]
    registro.cve = request.POST["CVE"]
    registro.tipo_tramite = request.POST["TIPO_TRAMITE"]
    registro.n_scarasup = request.POST["N_SCARASUP"]
    registro.e_ocarasup = request.POST["E_OCARASUP"]
    registro.f_presenta = request.POST["F_PRESENTA"]
    registro.f_resoluci = request.POST["F_RESOLUCI"]
    registro.f_inscribe = request.POST["F_INSCRIBE"]
    registro.cartaigm = request.POST["CARTAIGM"]
    registro.ped_asoc = request.POST["PED_ASOC"]
    registro.fechaped = request.POST["FECHAPED"]
    registro.rolped = request.POST["ROLPED"]
    registro.tipocoord = request.POST["TIPOCOORD"]
    registro.norte = request.POST["NORTE"]
    registro.mtsn = request.POST["MTSN"]
    registro.sur = request.POST["SUR"]
    registro.mtss = request.POST["MTSS"]
    registro.este = request.POST["ESTE"]
    registro.mtse = request.POST["MTSE"]
    registro.oeste = request.POST["OESTE"]
    registro.mtso = request.POST["MTSO"]
    registro.f_solicita = request.POST["F_SOLICITA"]
    registro.f_presman = request.POST["F_PRESMAN"]
    registro.f_mensura = request.POST["F_MENSURA"]
    registro.n1 = request.POST["N1"]
    registro.ha1 = request.POST["HA1"]
    registro.n_s1 = request.POST["N_S1"]
    registro.e_o1 = request.POST["E_O1"]
    registro.n2 = request.POST["N2"]
    registro.ha2 = request.POST["HA2"]
    registro.n_s2 = request.POST["N_S2"]
    registro.e_o2 = request.POST["E_O2"]
    registro.n3 = request.POST["N3"]
    registro.ha3 = request.POST["HA3"]
    registro.n_s3 = request.POST["N_S3"]
    registro.e_o3 = request.POST["E_O3"]
    registro.n4 = request.POST["N4"]
    registro.ha4 = request.POST["HA4"]
    registro.n_s4 = request.POST["N_S4"]
    registro.e_o4 = request.POST["E_O4"]
    registro.ind_vige = request.POST["IND_VIGE"]
    registro.razon = request.POST["RAZON"]
    registro.perito = request.POST["PERITO"]
    registro.oposicion = request.POST["OPOSICION"]
    registro.cpu = "1"
    registro.save()
    response = {}
    return HttpResponse(
        json.dumps(response),
        content_type="application/json"
        )

def ingresar_vertices(request):
    registro = Registro_Mineria.objects.get(pk=int(request.POST["pk"]))
    cont = 0
    buscar = registro.texto
    patron = re.compile("[1-9]\.\d\d\d[.,]\d\d\d[^-]")
    patron2 = re.compile("[1-9]\d\d\d\d\d\d[^-]")
    nortes = []
    if patron.search(buscar):
        coordenadas = patron.findall(buscar)
        for x in range(1,len(coordenadas)):
            test = coordenadas[x]
            eliminacion = test
            test = test[:len(test) - 1]
            test = test.replace(".","")
            test = test.replace(",","").upper()
            buscar = buscar.replace(eliminacion,"")
            nortes.append(test)
    elif patron2.search(buscar):
        coordenadas = patron2.findall(buscar)
        for x in range(1,len(coordenadas)):
            test = coordenadas[x]
            eliminacion = test
            test = test[:len(test) - 1]
            test = test.replace(".","")
            test = test.replace(",","").upper()
            buscar = buscar.replace(eliminacion,"")
            nortes.append(test)

    patron = re.compile("[^d.]\d\d\d[.,]\d\d\d[^d]")
    patron2 = re.compile("[^d.]\d\d\d\d\d\d[^d]")
    estes = []
    if patron.search(buscar):
        coordenadas = patron.findall(buscar)
        for x in range(1,len(coordenadas)):
            test = coordenadas[x]
            eliminacion = test
            test = test[:len(test) - 1]
            test = test.replace(".","")
            test = test[1:]
            test = test.replace(",","").upper()
            buscar = buscar.replace(eliminacion,"")
            estes.append(test)
    elif patron2.search(buscar):
        coordenadas = patron2.findall(buscar)
        for x in range(1,len(coordenadas)):
            test = coordenadas[x]
            eliminacion = test
            test = test[:len(test) - 1]
            test = test.replace(".","")
            test = test[1:]
            test = test.replace(",","").upper()
            buscar = buscar.replace(eliminacion,"")
            estes.append(test)

    linderos = []
    patron3 = re.compile("[VPL]\s?\d")
    if patron3.search(buscar):
        linderos = patron3.findall(buscar)
    response = {}
    if len(registro.vertice_set.all())==0:
        try:
            for x in range(len(nortes)):
                try:
                    vertice = Vertice.objects.create(registro_mineria=registro,
                                                     boletin=registro.boletin,
                                                     f_boletin=registro.f_boletin,
                                                     concesion=registro.concesion,
                                                     region=registro.region,
                                                     roljuz=registro.roljuz,
                                                     ident_lind=linderos[x],
                                                     coordnorte=nortes[x],
                                                     coordeste=estes[x])
                    vertice.save()
                    cont+=1
                except:
                    print "Vertice no creado"
        except:
            print "Vertice no creado"
        response["ok"] = cont
        registro.vertices = str(cont)
        registro.save()
    else:
        response["ok"] = -1
    return HttpResponse(
        json.dumps(response),
        content_type="application/json"
        )

def type_matches():
    return {
        'Vertices Conceciones': ["EXTRACTOS DE SENTENCIA DE EXPLORACION","EXTRACTOS DE SENTENCIA DE EXPLOTACION"],
        'Conceciones': ["EXTRACTOS DE SENTENCIA DE EXPLORACION","EXTRACTOS DE SENTENCIA DE EXPLOTACION"],
        'Manifestaciones': "MANIFESTACIONES MINERAS",
        'Pedimentos': "PEDIMENTOS MINEROS",
        'Vertices Mensura': "SOLICITUDES DE MENSURA",
        'Mensura': "SOLICITUDES DE MENSURA"
    }

def download_tramite(request):
    template_name = 'reporte_registros.html'
    data = {}
    data["diario"] = Diario.objects.all()
    #tipo_reporte = type_matches(request.POST[""])
    if request.POST:
        if request.POST['type'] == 'pedimentos':
            response = download.download_pedi(request)
        if request.POST['type'] == 'ver_concesiones':
            response = download.download_ver_conce(request)
        if request.POST['type'] == 'concesiones':
            response = download.download_conce(request)
        if request.POST['type'] == 'manifestaciones':
            response = download.download_manifes(request)
        if request.POST['type'] == 'ver_mensuras':
            response = download.download_ver_mensu(request)
        if request.POST['type'] == 'mensuras':
            response = download.download_mensu(request)
        return response
    
    return render(request, template_name, data)

def get_notifications(request):
    return HttpResponse(
                json.dumps({
                    "result": True,
                    "download_completed": len(CompletedTask.objects.filter(task_name="core.views.crear_pdf_de_boletin")),
                    "download_running": len(Task.objects.filter(task_name="core.views.crear_pdf_de_boletin")),
                    "extract_completed": len(CompletedTask.objects.filter(task_name="core.views.scrap_data")),
                    "extract_running": len(Task.objects.filter(task_name="core.views.scrap_data")),
                }),
                content_type="application/json")
