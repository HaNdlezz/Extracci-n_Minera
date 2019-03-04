# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, Http404
from background_task import background
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


def getPDFContent(path):
    content = ""
    # Load PDF into pyPDF
    pdf = pyPdf.PdfFileReader(file(path, "rb"))
    # Iterate pages
    for i in range(0, pdf.getNumPages()):
        # Extract text from page and add to content
        content += unidecode.unidecode(pdf.getPage(i).extractText()) + "\n"
    # Collapse whitespace
    text = content
    text = text.split("Boletin Oficial de Mineria")[::-1][0]
    return text

def getPDFContent2(path):
    content = ""
    # Load PDF into pyPDF
    pdf = pyPdf.PdfFileReader(file(path, "rb"))
    # Iterate pages
    for i in range(0, pdf.getNumPages()):
        # Extract text from page and add to content
        content += unidecode.unidecode(pdf.getPage(i).extractText()) + "\n"
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
    print "ARCHIVO",type(archivo)
    text = getPDFContent(archivo)
    for x in tipos:
        if x in text:
            text = text.replace(x,"SEPARADOR DE TIPOS DE MINERIA "+x+"TERMINO SEPARADOR")
    datos = text.split("SEPARADOR DE TIPOS DE MINERIA ")
    datos.pop(0)
    codigo_diario = request["archivo"].split("/")
    format_fecha = codigo_diario[4] + "/" + codigo_diario[5] + "/" + codigo_diario[6]
    diario = Diario.objects.create(codigo=name[0].split(".pdf")[0],fecha=format_fecha)
    diario.save()
    for y in datos:
        tipo = y.split("TERMINO SEPARADOR")[0]
        for x in y.split("("):
#            print x.split("TERMINO SEPARADOR")[0]
            if "CVE" in x:
                    try:
                        x = x.split("CVE:")[1].split(")")[0].replace(" ","")
                        os.system('wget -U "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4" ' + "http://www.diariooficial.interior.gob.cl/publicaciones/"+ str(name[4]) +"/" +str(name[3]) +"/" + str(name[2]) + "/" + name[0].split(".pdf")[0] + "/07/" + str(x.split("CVE:")[0]) + ".pdf")
                        url = "http://www.diariooficial.interior.gob.cl/publicaciones/"+ str(name[4]) +"/" +str(name[3]) +"/" + str(name[2]) + "/" + name[0].split(".pdf")[0] + "/07/" + str(x.split("CVE:")[0]) + ".pdf"
                        aux = Registro_Mineria.objects.create(diario=diario,tipo_tramite=tipo,url=url,cve=x.split("CVE:")[0],texto=getPDFContent2(str(x.split("CVE:")[0])+".pdf"))
                        aux.save()
                        cve_downloaded+=1
                        os.system('rm ' + x.split("CVE:")[0]+".pdf")
                    except:
                        pass
#    pedimentos = text.split("MANIFESTACIONES MINERAS")[0]
#    text = text.split("MANIFESTACIONES MINERAS")[1]
#    pedimentos = pedimentos.split("(")
#    pedimentos_final = []
#    for x in pedimentos:
#        if "CVE" in x:
#            x = x.split("CVE:")[1].split(")")[0].replace(" ","")
#            pedimentos_final.append(x)
    os.system('rm ' + name[0])
    data = {}
    data["total_cve"] = str(cve_downloaded)
    data["numero_registro"] = "1"

@login_required(login_url='/')
def descargar_boletin(request):
    template_name = 'Historic_Data.html'
    crear_pdf_de_boletin(request.POST)
    data = {}
    data["alert"] = "Se esta descargando la informacion del CVE"
    return render(request, template_name, data)

#    return HttpResponse(
#        json.dumps(response),
#        content_type="application/json"
#        )
def Historic_Data(request):
    template_name = "Historic_Data.html"
    data = {}
    data["diario"] = Diario.objects.all()
    if request.POST:
        diario = Diario.objects.get(pk=request.POST["fecha"])
        data["solicitudes"] = diario.registro_mineria_set.all()
        data["fecha"] = diario.pk
    return render(request, template_name, data)

def extraerConcesiones(concesion):
    if "EXPLORACION" in concesion.tipo_tramite:
        concesion.tipo_conce = "PEDIMENTO"
    if "EXPLOTACION" in concesion.tipo_tramite:
        concesion.tipo_conce = "MANIFESTACION"
    patron = re.compile("Huso\s\d\d|HUSO\s\d\d|huso\s\d\d")
    if patron.search(concesion.texto):
        concesion.huso = patron.search(concesion.texto).group().split(" ")[-1]
    else:
        concesion.huso = "No se detecta Huso"
    patron = re.compile("datum\sWGS\s\d\d|datum\sWGS\s\d\d\d\d|Datum\sWGS\s\d\d|Datum\sWGS\s\d\d\d\d|Datum\sWGS\s\d\d\d\d|DATUM\sWGS\s\d\d|DATUM\sWGS\s\d\d\d\d|datum\s\d\d|datum\s\d\d\d\d|Datum\s\d\d|Datum\s\d\d\d\d|DATUM\s\d\d|DATUM\s\d\d\d\d")
    patron2 = re.compile("DATUM\sWGS\d\d|DATUM\sWGS\d\d\d\d|Datum\sWGS\d\d|Datum\sWGS\d\d\d\d|datum\sWGS\d\d|datum\sWGS\d\d\d\d")
    if patron.search(concesion.texto):
        datum = patron.search(concesion.texto).group()
        datum = datum.split(" ")
        datum = datum[-1]
    elif patron2.search(concesion.texto):
        datum = patron2.search(concesion.texto).group()
        datum = datum.split("WGS")
        datum = datum[-1]
    else:
        datum = "No se detecta Datum"
    if str(datum) == "84":
        datum = "WGS84"
    elif str(datum) == "56":
        datum = "PSAD56"
    elif str(datum) == "69":
        datum = "SAD69"
    else:
        print ""
    patron = re.compile("La Canoa 1956|LA CANOA 1956|la canoa 1956")
    if patron.search(concesion.texto):
        datum = "PSAD56"
    concesion.datum = datum
    concesion.tipo_utm = "M"
    patron = re.compile("[aA-zZ][-][0-9]{1,4}[-][0-9]{1,4}")
    if patron.search(concesion.texto):
        concesion.roljuz = patron.search(concesion.texto).group()
        concesion.year = patron.search(concesion.texto).group().split("-")[-1]
    patron = re.compile("[0-9]{1,2}\s[dD-eE]{2}\s[aA-zZ]{4,9}\s[dD-lL]{2,3}\s([aA-oO]{3}\s)?[0-9]{4}")
    n_fechas = 5
    fechas = []
    aux_text = concesion.texto
    while(n_fechas != 0):
        if patron.search(aux_text):
            fecha = patron.search(aux_text).group()
            fechas.append(fecha)
            aux_text = aux_text.replace(fecha, " ")
        n_fechas-=1
    fecha_equivalencia = {"enero":"01","febrero":"02","marzo":"03","abril":"04","mayo":"05","junio":"06","julio":"07","agosto":"08","septiembre":"09","octubre":"10","noviembre":"11","diciembre":"12"}
    if len(fechas) >= 2:
        date_target = fechas[1].split(" ")
        dia=date_target[0]
        mes=fecha_equivalencia[date_target[2].lower()]
        anio=date_target[-1]
        concesion.f_sentenc1 = anio+"/"+mes+"/"+dia
    patron = re.compile("(fojas|FOJAS|Fojas)\s[0-9]{1,2}(.?)[0-9]{1,3}")
    if patron.search(concesion.texto):
        concesion.fojas = patron.search(concesion.texto).group().replace(".","").split(" ")[1]
        aux_text = concesion.texto.split(patron.search(concesion.texto).group())[1]
        if "vta" in aux_text or "Vta" in aux_text or "Vuelta" in aux_text or "vuelta" in aux_text or "VTA" in aux_text or "VUELTA" in aux_text:
            concesion.fojas = concesion.fojas+" "+"VTA"
        patron = re.compile("(numero|Numero|NUMERO|)\s[0-9]{1,2}(.?)[0-9]{1,3}")
        if patron.search(aux_text):
            concesion.numero = patron.search(aux_text).group().replace(".","").split(" ")[1]
    patron = re.compile("[0-9]{1,2}(.?)[0-9]{1,3}\s(hectareas|Hectareas|HECTAREAS)")
    if patron.search(concesion.texto):
        concesion.hectareas = patron.search(concesion.texto).group().replace(".","").split(" ")[0]
    concesion.obser = "(CVE "+concesion.cve+")"
    if concesion.vertices is None:
        concesion.vertices = 0
    if concesion.hectareas is None:
        concesion.hectareas = 0
    if concesion.nortepi is None:
        concesion.nortepi = 0
    if concesion.estepi is None:
        concesion.estepi = 0
    concesion.save()
    print concesion

def extraerManifestaciones(manifestacion):
    manifestacion.tipo_utm = "M"
    patron = re.compile("Huso\s\d\d|HUSO\s\d\d|huso\s\d\d")
    if patron.search(manifestacion.texto):
        manifestacion.huso = patron.search(manifestacion.texto).group().split(" ")[-1]
    else:
        manifestacion.huso = "No se detecta Huso"
    patron = re.compile("[0-9]{1,2}(.?)[0-9]{1,3}\s(hectareas|Hectareas|HECTAREAS)")
    if patron.search(manifestacion.texto):
        manifestacion.hectareas = patron.search(manifestacion.texto).group().replace(".","").split(" ")[0]
    patron = re.compile("[aA-zZ][-][0-9]{1,4}[-][0-9]{1,4}")
    if patron.search(manifestacion.texto):
        manifestacion.roljuz = patron.search(manifestacion.texto).group()
        manifestacion.year = patron.search(manifestacion.texto).group().split("-")[-1]
    patron = re.compile("(fojas|FOJAS|Fojas)\s[0-9]{1,2}(.?)[0-9]{1,3}")
    if patron.search(manifestacion.texto):
        manifestacion.fojas = patron.search(manifestacion.texto).group().replace(".","").split(" ")[1]
        aux_text = manifestacion.texto.split(patron.search(manifestacion.texto).group())[1]
        if "vta" in aux_text or "Vta" in aux_text or "Vuelta" in aux_text or "vuelta" in aux_text or "VTA" in aux_text or "VUELTA" in aux_text:
            manifestacion.fojas = manifestacion.fojas+" "+"VTA"
        patron = re.compile("(numero|Numero|NUMERO|)\s[0-9]{1,2}(.?)[0-9]{1,3}")
        if patron.search(aux_text):
            manifestacion.numero = patron.search(aux_text).group().replace(".","").split(" ")[1]
    manifestacion.obser = "(CVE "+manifestacion.cve+")"
    patron = re.compile("datum\sWGS\s\d\d|datum\sWGS\s\d\d\d\d|Datum\sWGS\s\d\d|Datum\sWGS\s\d\d\d\d|Datum\sWGS\s\d\d\d\d|DATUM\sWGS\s\d\d|DATUM\sWGS\s\d\d\d\d|datum\s\d\d|datum\s\d\d\d\d|Datum\s\d\d|Datum\s\d\d\d\d|DATUM\s\d\d|DATUM\s\d\d\d\d")
    patron2 = re.compile("DATUM\sWGS\d\d|DATUM\sWGS\d\d\d\d|Datum\sWGS\d\d|Datum\sWGS\d\d\d\d|datum\sWGS\d\d|datum\sWGS\d\d\d\d")
    if patron.search(manifestacion.texto):
        datum = patron.search(manifestacion.texto).group()
        datum = datum.split(" ")
        datum = datum[-1]
    elif patron2.search(manifestacion.texto):
        datum = patron2.search(manifestacion.texto).group()
        datum = datum.split("WGS")
        datum = datum[-1]
    else:
        datum = "No se detecta Datum"
    if str(datum) == "84":
        datum = "WGS84"
    elif str(datum) == "56":
        datum = "PSAD56"
    elif str(datum) == "69":
        datum = "SAD69"
    else:
        print ""
    patron = re.compile("La Canoa 1956|LA CANOA 1956|la canoa 1956")
    if patron.search(manifestacion.texto):
        datum = "PSAD56"
    manifestacion.datum = datum
    manifestacion.save()
    print manifestacion

def extraerPedimentos(pedimento):
    pedimento.tipo_utm = "M"
    patron = re.compile("Huso\s\d\d|HUSO\s\d\d|huso\s\d\d")
    if patron.search(pedimento.texto):
        pedimento.huso = patron.search(pedimento.texto).group().split(" ")[-1]
    else:
        pedimento.huso = "No se detecta Huso"
    patron = re.compile("[0-9]{1,2}(.?)[0-9]{1,3}\s(hectareas|Hectareas|HECTAREAS)")
    if patron.search(pedimento.texto):
        pedimento.hectareas = patron.search(pedimento.texto).group().replace(".","").split(" ")[0]
    patron = re.compile("[aA-zZ][-][0-9]{1,4}[-][0-9]{1,4}")
    if patron.search(pedimento.texto):
        pedimento.roljuz = patron.search(pedimento.texto).group()
        pedimento.year = patron.search(pedimento.texto).group().split("-")[-1]
    patron = re.compile("[0-9]{1,2}\s[dD-eE]{2}\s[aA-zZ]{4,9}\s[dD-lL]{2,3}\s([aA-oO]{3}\s)?[0-9]{4}")
    n_fechas = 5
    fechas = []
    aux_text = pedimento.texto
    while(n_fechas != 0):
        if patron.search(aux_text):
            fecha = patron.search(aux_text).group()
            fechas.append(fecha)
            aux_text = aux_text.replace(fecha, " ")
        n_fechas-=1
    fecha_equivalencia = {"enero":"01","febrero":"02","marzo":"03","abril":"04","mayo":"05","junio":"06","julio":"07","agosto":"08","septiembre":"09","octubre":"10","noviembre":"11","diciembre":"12"}
    if len(fechas) >= 2:
        date_target = fechas[2].split(" ")
        dia=date_target[0]
        mes=fecha_equivalencia[date_target[2].lower()]
        anio=date_target[-1]
        pedimento.f_presenta = anio+"/"+mes+"/"+dia
    patron = re.compile("(fojas|FOJAS|Fojas)\s[0-9]{1,2}(.?)[0-9]{1,3}")
    if patron.search(pedimento.texto):
        pedimento.fojas = patron.search(pedimento.texto).group().replace(".","").split(" ")[1]
        aux_text = pedimento.texto.split(patron.search(pedimento.texto).group())[1]
        if "vta" in aux_text or "Vta" in aux_text or "Vuelta" in aux_text or "vuelta" in aux_text or "VTA" in aux_text or "VUELTA" in aux_text:
            pedimento.fojas = pedimento.fojas+" "+"VTA"
        patron = re.compile("(numero|Numero|NUMERO|)\s[0-9]{1,2}(.?)[0-9]{1,3}")
        if patron.search(aux_text):
            pedimento.numero = patron.search(aux_text).group().replace(".","").split(" ")[1]
    pedimento.obser = "(CVE "+pedimento.cve+")"
    patron = re.compile("datum\sWGS\s\d\d|datum\sWGS\s\d\d\d\d|Datum\sWGS\s\d\d|Datum\sWGS\s\d\d\d\d|Datum\sWGS\s\d\d\d\d|DATUM\sWGS\s\d\d|DATUM\sWGS\s\d\d\d\d|datum\s\d\d|datum\s\d\d\d\d|Datum\s\d\d|Datum\s\d\d\d\d|DATUM\s\d\d|DATUM\s\d\d\d\d")
    patron2 = re.compile("DATUM\sWGS\d\d|DATUM\sWGS\d\d\d\d|Datum\sWGS\d\d|Datum\sWGS\d\d\d\d|datum\sWGS\d\d|datum\sWGS\d\d\d\d")
    if patron.search(pedimento.texto):
        datum = patron.search(pedimento.texto).group()
        datum = datum.split(" ")
        datum = datum[-1]
    elif patron2.search(pedimento.texto):
        datum = patron2.search(pedimento.texto).group()
        datum = datum.split("WGS")
        datum = datum[-1]
    else:
        datum = "No se detecta Datum"
    if str(datum) == "84":
        datum = "WGS84"
    elif str(datum) == "56":
        datum = "PSAD56"
    elif str(datum) == "69":
        datum = "SAD69"
    else:
        print ""
    patron = re.compile("La Canoa 1956|LA CANOA 1956|la canoa 1956")
    if patron.search(pedimento.texto):
        datum = "PSAD56"
    pedimento.datum = datum
    pedimento.save()
    print pedimento

def extraerMensuras(mensura):
    patron = re.compile("[aA-zZ][-][0-9]{1,4}[-][0-9]{1,4}")
    if patron.search(mensura.texto):
        mensura.roljuz = patron.search(mensura.texto).group()
        mensura.year = patron.search(mensura.texto).group().split("-")[-1]
    mensura.tipo_utm = "M"
    patron = re.compile("[0-9]{1,2}(.?)[0-9]{1,3}\s(hectareas|Hectareas|HECTAREAS)")
    if patron.search(mensura.texto):
        mensura.hectareas = patron.search(mensura.texto).group().replace(".","").split(" ")[0]
    patron = re.compile("datum\sWGS\s\d\d|datum\sWGS\s\d\d\d\d|Datum\sWGS\s\d\d|Datum\sWGS\s\d\d\d\d|Datum\sWGS\s\d\d\d\d|DATUM\sWGS\s\d\d|DATUM\sWGS\s\d\d\d\d|datum\s\d\d|datum\s\d\d\d\d|Datum\s\d\d|Datum\s\d\d\d\d|DATUM\s\d\d|DATUM\s\d\d\d\d")
    patron2 = re.compile("DATUM\sWGS\d\d|DATUM\sWGS\d\d\d\d|Datum\sWGS\d\d|Datum\sWGS\d\d\d\d|datum\sWGS\d\d|datum\sWGS\d\d\d\d")
    if patron.search(mensura.texto):
        datum = patron.search(mensura.texto).group()
        datum = datum.split(" ")
        datum = datum[-1]
    elif patron2.search(mensura.texto):
        datum = patron2.search(mensura.texto).group()
        datum = datum.split("WGS")
        datum = datum[-1]
    else:
        datum = "No se detecta Datum"
    if str(datum) == "84":
        datum = "WGS84"
    elif str(datum) == "56":
        datum = "PSAD56"
    elif str(datum) == "69":
        datum = "SAD69"
    else:
        print ""
    patron = re.compile("La Canoa 1956|LA CANOA 1956|la canoa 1956")
    if patron.search(mensura.texto):
        datum = "PSAD56"
    mensura.datum = datum
    patron = re.compile("Huso\s\d\d|HUSO\s\d\d|huso\s\d\d")
    if patron.search(mensura.texto):
        mensura.huso = patron.search(mensura.texto).group().split(" ")[-1]
    else:
        mensura.huso = "No se detecta Huso"

    print mensura

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
        x.save()
        if x.tipo_tramite=="EXTRACTOS DE SENTENCIA DE EXPLORACION" or x.tipo_tramite=="EXTRACTOS DE SENTENCIA DE EXPLOTACION":
            extraerConcesiones(x)
        if x.tipo_tramite=="PEDIMENTOS MINEROS":
            extraerPedimentos(x)
        if x.tipo_tramite=="MANIFESTACIONES MINERAS":
            extraerManifestaciones(x)
        if x.tipo_tramite=="SOLICITUDES DE MENSURA":
            extraerMensuras(x)
    print "Run background proccess end"

def Obtener_Datos_General(request):
    print "Starting to loocking for data"
    template_name = "Historic_Data.html"
    scrap_data(request.POST)
    data = {}
    data["alert"] = "Se esta extrayendo la informacion de los CVE. Este proceso podria tardar un momento."
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

def excel_registros(request):
    template_name = 'reporte_registros.html'
    data = {}
    data["diario"] = Diario.objects.all()
    if request.POST:
        data = {}
        workbook = xlsxwriter.Workbook('Static/registros.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, 'BOLETIN')
        worksheet.write(0, 1, 'F_BOLETIN')
        worksheet.write(0, 2, 'TIPO_CONCE')
        worksheet.write(0, 3, 'CONCESION')
        worksheet.write(0, 4, 'CONCESIONA')
        worksheet.write(0, 5, 'REPRESENTA')
        worksheet.write(0, 6, 'DIRECCION')
        worksheet.write(0, 7, 'ROLMINERO')
        worksheet.write(0, 8, 'F_SENTENC1')
        worksheet.write(0, 9, 'F_SENTENC2')
        worksheet.write(0, 10, 'F_PUBEXT')
        worksheet.write(0, 11, 'F_INSCMIN')
        worksheet.write(0, 12, 'FOJAS')
        worksheet.write(0, 13, 'NUMERO')
        worksheet.write(0, 14, 'YEAR')
        worksheet.write(0, 15, 'CIUDAD')
        worksheet.write(0, 16, 'JUZGADO')
        worksheet.write(0, 17, 'ROLJUZ')
        worksheet.write(0, 18, 'IND_METAL')
        worksheet.write(0, 19, 'REGION')
        worksheet.write(0, 20, 'PROVINCIA')
        worksheet.write(0, 21, 'COMUNA')
        worksheet.write(0, 22, 'LUGAR')
        worksheet.write(0, 23, 'TIPO_UTM')
        worksheet.write(0, 24, 'NORTEPI')
        worksheet.write(0, 25, 'ESTEPI')
        worksheet.write(0, 26, 'VERTICES')
        worksheet.write(0, 27, 'HA_PERT')
        worksheet.write(0, 28, 'HECTAREAS')
        worksheet.write(0, 29, 'OBSER')
        worksheet.write(0, 30, 'DATUM')
        worksheet.write(0, 31, 'F_PRESTRIB')
        worksheet.write(0, 32, 'ARCHIVO')
        worksheet.write(0, 33, 'CORTE')
        worksheet.write(0, 34, 'HUSO')
        worksheet.write(0, 35, 'EDITOR')
        cont2=1
        cont = 1
        for x in Registro_Mineria.objects.all():
            if True:
                nulo = len(str(x.concesion))
            else:
                nulo = len(str(unidecode.unidecode(x.concesion)))
                #try:
            if x.tipo_tramite == "EXTRACTOS DE SENTENCIA DE EXPLORACION" or x.tipo_tramite == "EXTRACTOS DE SENTENCIA DE EXPLOTACION":
                fechaFormato = str(x.f_boletin).split("/")
                fechaFormato =fechaFormato[2]+"/"+fechaFormato[1]+"/"+fechaFormato[0]
                worksheet.write(cont, 0, x.boletin)
                worksheet.write(cont, 1, fechaFormato)
                worksheet.write(cont, 2, x.tipo_conce)
                worksheet.write(cont, 3, x.concesion)
                worksheet.write(cont, 4, x.concesiona)
                worksheet.write(cont, 5, x.representa)
                worksheet.write(cont, 6, x.direccion)
                worksheet.write(cont, 7, x.rolminero)
                worksheet.write(cont, 8, x.f_sentenc1)
                worksheet.write(cont, 9, x.f_sentenc2)
                worksheet.write(cont, 10, x.f_pubext)
                worksheet.write(cont, 11, x.f_inscmin)
                worksheet.write(cont, 12, x.fojas)
                worksheet.write(cont, 13, x.numero)
                worksheet.write(cont, 14, x.year)
                worksheet.write(cont, 15, x.ciudad)
                worksheet.write(cont, 16, x.juzgado)
                worksheet.write(cont, 17, x.roljuz)
                worksheet.write(cont, 18, x.ind_metal)
                worksheet.write(cont, 19, x.region)
                worksheet.write(cont, 20, x.provincia)
                worksheet.write(cont, 21, x.comuna)
                worksheet.write(cont, 22, x.lugar)
                worksheet.write(cont, 23, x.tipo_utm)
                worksheet.write(cont, 24, x.nortepi)
                worksheet.write(cont, 25, x.estepi)
                worksheet.write(cont, 26, x.vertices)
                worksheet.write(cont, 27, x.ha_pert)
                worksheet.write(cont, 28, x.hectareas)
                worksheet.write(cont, 29, x.obser)
                worksheet.write(cont, 30, x.datum)
                worksheet.write(cont, 31, x.f_prestrib)
                worksheet.write(cont, 32, x.archivo)
                worksheet.write(cont, 33, x.corte)
                worksheet.write(cont, 34, x.huso)
                worksheet.write(cont, 35, x.editor)
                cont += 1
        workbook.close()
        return render(request, template_name, data)
    return render(request, template_name, data)

def excel_vertices(request):
    template_name = 'reporte_vertices.html'
    data = {}
    if request.POST:
        response = {}
        # workbook = xlsxwriter.Workbook('Static/vertices.xlsx')
        # worksheet = workbook.add_worksheet()
        # worksheet.write(0, 0, 'BOLETIN')
        # worksheet.write(0, 1, 'F_BOLETIN')
        # worksheet.write(0, 2, 'CONCESION')
        # worksheet.write(0, 3, 'REGION')
        # worksheet.write(0, 4, 'ROLJUZ')
        # worksheet.write(0, 5, 'IDENT_LIND')
        # worksheet.write(0, 6, 'COORDNORTE')
        # worksheet.write(0, 7, 'COORDESTE')
        # cont = 1
        # for x in Vertice.objects.all():
        #     worksheet.write(cont, 0, x.boletin)
        #     fechaFormato = str(x.f_boletin).split("/")
        #     fechaFormato =fechaFormato[2]+"/"+fechaFormato[1]+"/"+fechaFormato[0]
        #     worksheet.write(cont, 1, fechaFormato)
        #     worksheet.write(cont, 2, x.concesion)
        #     worksheet.write(cont, 3, x.region)
        #     worksheet.write(cont, 4, x.roljuz)
        #     worksheet.write(cont, 5, x.ident_lind)
        #     worksheet.write(cont, 6, x.coordnorte)
        #     worksheet.write(cont, 7, x.coordeste)
        #     cont += 1
        # workbook.close()
        db = dbf.Dbf("Static/test.dbf", new=True)
        db.addField(
            ("BOLETIN", "C", 80),
            ("F_BOLETIN", "C", 80),
            ("CONCESION", "C", 80),
            ("REGION", "C", 80),
            ("ROLJUZ", "C", 80),
            ("IDENT_LIND", "C", 80),
            ("COORDNORTE", "C", 80),
            ("COORDESTE", "C", 80),
        )
        cont = 0
        for x in Vertice.objects.all():
            rec = db.newRecord()
            rec["BOLETIN"] = unidecode.unidecode(x.boletin)
            fechaFormato = str(x.f_boletin).split("/")
            fechaFormato = fechaFormato[2]+"/"+fechaFormato[1]+"/"+fechaFormato[0]
            rec["F_BOLETIN"] = unidecode.unidecode(fechaFormato)
            try:
                rec["CONCESION"] = unidecode.unidecode(x.concesion)
            except:
                rec["CONCESION"] = ""
            try:
                rec["REGION"] = unidecode.unidecode(x.region)
            except:
                rec["REGION"] = ""
            try:
                rec["ROLJUZ"] = unidecode.unidecode(x.roljuz)
            except:
                rec["ROLJUZ"] = ""
            try:
                rec["IDENT_LIND"] = unidecode.unidecode(x.ident_lind)
            except:
                rec["IDENT_LIND"] = ""
            try:
                rec["COORDNORTE"] = unidecode.unidecode(x.coordnorte)
            except:
                rec["COORDNORTE"] = ""
            rec.store()
            cont += 1
        db.close()
        data = {}
        return render(request, template_name, data)
    return render(request, template_name, data)

def type_matches():
    return {
        'Vertices Conceciones': ["EXTRACTOS DE SENTENCIA DE EXPLORACION","EXTRACTOS DE SENTENCIA DE EXPLOTACION"],
        'Conceciones': ["EXTRACTOS DE SENTENCIA DE EXPLORACION","EXTRACTOS DE SENTENCIA DE EXPLOTACION"],
        'Manifestaciones': "MANIFESTACIONES MINERAS",
        'Pedimentos': "PEDIMENTOS MINEROS",
        'Vertices Mensura': "SOLICITUDES DE MENSURA",
        'Mensura': "SOLICITUDES DE MENSURA"
    }

def download(request):
    # template_name = 'reporte_registros.html'
    data = {}
    #tipo_reporte = type_matches(request.POST[""])

    if request.POST['type'] == 'pedimentos':
        response = download_pedi(request)
    if request.POST['type'] == 'ver_concesiones':
        response = download_ver_conce(request) # TODO his own method filtering for those who have vertex
    if request.POST['type'] == 'concesiones':
        response = download_conce(request)
    if request.POST['type'] == 'manifestaciones':
        response = download_manifes(request)
    if request.POST['type'] == 'ver_mensuras':
        response = download_ver_mensu(request) # TODO his own method filtering for those who have vertex
    if request.POST['type'] == 'mensuras':
        response = download_mensu(request)
    return response
    # return render(request, template_name, data)


#Function for create dbf of Pedimentos
def download_pedi(request):
    da = {}
    file_name = "pedi " + str(datetime.datetime.now()) + ".dbf"
    db = dbf.Dbf("Static/" + file_name, new=True)
    db.addField(
        #Add headers to dbf file
        ("BOLETIN", "C", 6),
        ("F_BOLETIN", "D", 8),
        ("CONCESION", "C", 60),
        ("CONCESIONA", "C", 60),
        ("REPRESENTA", "C", 60),
        ("DIRECCION", "C", 100),
        ("REGION", "C", 2),
        ("PROVINCIA", "C", 15),
        ("COMUNA", "C", 20),
        ("LUGAR", "C", 50),
        ("TIPO_UTM", "C", 1),
        ("NORTEPI", "N", 11,2),
        ("ESTEPI", "N", 11,2),
        ("HUSO", "N", 2),
        ("N_SCARASUP", "N", 8),
        ("E_OCARASUP", "N", 8),
        ("IND_METAL", "C", 1),
        ("HECTAREAS", "N", 8),
        ("HA_PERT", "C", 6),
        ("JUZGADO", "C", 35),
        ("ROLJUZ", "C", 15),
        ("F_PRESENTA", "D", 8),
        ("F_RESOLUCI", "D", 8),
        ("F_INSCRIBE", "D", 8),
        ("FOJAS", "C", 10),
        ("NUMERO", "C", 6),
        ("YEAR", "C", 4),
        ("CIUDAD", "C", 15),
        ("CARTAIGM", "C", 6),
        ("OBSER", "C", 55),
        ("DATUM", "C", 6),
        ("F_PRESTRIB", "D", 8),
        ("ARCHIVO", "C", 100),
        ("CORTE", "C", 10),
        ("EDITOR", "C", 11),
    )


    ## fill DBF with some records
    if int(request.POST["fecha"]) != 0:
        diario = Diario.objects.get(pk=int(request.POST["fecha"]))#filter "diario" for date add: tipo_tramite for pedimentos
        solicitudes = diario.registro_mineria_set.all()#get register for specific "diario"
    else:
        solicitudes = Registro_Mineria.objects.all()#Get all register in case that the user wish generate a dbf with all register without care the date
    for solicitud in solicitudes:
        if solicitud.tipo_tramite == "PEDIMENTOS MINEROS":
            response = db.newRecord()
            print solicitud.boletin
            #the text after of solicitud. is the attributes
            # response["FDIAR_APRO"] = solicitud.FDIAR_APRO#.strftime("%Y-%M-%D")
            response["BOLETIN"] = solicitud.boletin or ''
            response["F_BOLETIN"] = '' if solicitud.f_boletin is None or len(solicitud.f_boletin)==0 else (datetime.datetime.strptime(solicitud.f_boletin, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["CONCESION"] = '' if solicitud.concesion is None else solicitud.concesion
            response["CONCESIONA"] = '' if solicitud.concesiona is None else solicitud.concesiona
            response["REPRESENTA"] = '' if solicitud.representa is None else solicitud.representa
            response["DIRECCION"] = '' if solicitud.direccion is None else solicitud.direccion
            response["REGION"] = solicitud.region or ''
            response["PROVINCIA"] = '' if solicitud.provincia is None else solicitud.provincia
            response["COMUNA"] = '' if solicitud.comuna is None else solicitud.comuna
            response["LUGAR"] = '' if solicitud.lugar is None else solicitud.lugar
            response["TIPO_UTM"] = solicitud.tipo_utm or ''
            nortepi = 0
            if solicitud.nortepi is not None:
                nortepi = float(solicitud.nortepi)
            response["NORTEPI"] = nortepi or 0
            estepi = 0
            if solicitud.estepi is not None:
                estepi = float(solicitud.estepi)
            response["ESTEPI"] = estepi or 0
            huso = 0
            if solicitud.huso != "No se detecta Huso" and solicitud.huso is not None:
                huso = float(solicitud.huso)
            response["HUSO"] = huso or 0
            n_scarasup = 0
            if solicitud.n_scarasup is not None:
                n_scarasup = float(solicitud.n_scarasup)
            response["N_SCARASUP"] = n_scarasup or 0
            e_ocarasup = 0
            if solicitud.e_ocarasup is not None:
                e_ocarasup = float(solicitud.e_ocarasup)
            response["E_OCARASUP"] = e_ocarasup or 0
            response["IND_METAL"] = '' if solicitud.ind_metal is None else solicitud.ind_metal
            hectareas = 0
            if solicitud.hectareas is not None:
                hectareas = float(solicitud.hectareas)
            response["HECTAREAS"] = hectareas or 0
            response["HA_PERT"] = '' if solicitud.ha_pert is None else solicitud.ha_pert
            response["JUZGADO"] = '' if solicitud.juzgado is None else solicitud.juzgado
            response["ROLJUZ"] = '' if solicitud.roljuz is None else solicitud.roljuz
            response["F_PRESENTA"] = '' if solicitud.f_presenta is None or len(solicitud.f_presenta)==0 else (datetime.datetime.strptime(solicitud.f_presenta, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_RESOLUCI"] = '' if solicitud.f_resoluci is None or len(solicitud.f_resoluci)==0 else (datetime.datetime.strptime(solicitud.f_resoluci, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_INSCRIBE"] = '' if solicitud.f_inscribe is None or len(solicitud.f_inscribe)==0 else (datetime.datetime.strptime(solicitud.f_inscribe, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["FOJAS"] = '' if solicitud.fojas is None else solicitud.fojas
            response["NUMERO"] = '' if solicitud.numero is None else solicitud.numero
            response["YEAR"] = '' if solicitud.year is None else solicitud.year
            response["CIUDAD"] = '' if solicitud.ciudad is None else solicitud.ciudad
            response["CARTAIGM"] = '' if solicitud.cartaigm is None else solicitud.cartaigm
            response["OBSER"] = '' if solicitud.obser is None else solicitud.obser
            response["DATUM"] = '' if solicitud.datum is None else solicitud.datum
            response["F_PRESTRIB"] = '' if solicitud.f_prestrib is None or len(solicitud.f_prestrib)==0 else (datetime.datetime.strptime(solicitud.f_prestrib, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["ARCHIVO"] = '' if solicitud.archivo is None else solicitud.archivo
            response["CORTE"] = '' if solicitud.corte is None else solicitud.corte
            response["EDITOR"] = '' if solicitud.editor is None else solicitud.editor
            # response["CPU"] = solicitud.cpu or ''
            response.store()
    db.close()
    # pdb.set_trace()
    file_path = os.path.join(settings.BASE_DIR, "Static/" + file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-dbase")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            os.remove(file_path)
            return response
    raise Http404






#Function for create dbf of Manifestaciones
def download_manifes(request):
    da = {}
    file_name = "manifes " + str(datetime.datetime.now()) + ".dbf"
    db = dbf.Dbf("Static/" + file_name, new=True)
    db.addField(
        #Add headers to dbf file
        ("BOLETIN", "C", 6),
        ("F_BOLETIN", "D", 8),
        ("CONCESION", "C", 60),
        ("CONCESIONA", "C", 60),
        ("REPRESENTA", "C", 60),
        ("DIRECCION", "C", 100),
        ("REGION", "C", 2),
        ("PROVINCIA", "C", 15),
        ("COMUNA", "C", 20),
        ("LUGAR", "C", 50),
        ("TIPO_UTM", "C", 1),
        ("NORTEPI", "N", 11,2),
        ("ESTEPI", "N", 11,2),
        ("HUSO", "N", 2),
        ("N_SCARASUP", "N", 8),
        ("E_OCARASUP", "N", 8),
        ("HECTAREAS", "N", 8),
        ("HA_PERT", "C", 6),
        ("JUZGADO", "C", 35),
        ("ROLJUZ", "C", 15),
        ("F_PRESENTA", "D", 8),
        ("F_RESOLUCI", "D", 8),
        ("F_INSCRIBE", "D", 8),
        ("FOJAS", "C", 10),
        ("NUMERO", "C", 6),
        ("YEAR", "C", 4),
        ("CIUDAD", "C", 15),
        ("CARTAIGM", "C", 6),
        ("OBSER", "C", 55),
        ("PED_ASOC", "C", 50),
        ("FECHAPED", "D", 8),
        ("ROLPED", "C", 10),
        ("TIPOCOORD", "C", 1),
        ("NORTE", "C", 45),
        ("MTSN", "C", 6),
        ("SUR", "C", 45),
        ("MTSS", "C", 6),
        ("ESTE", "C", 45),
        ("MTSE", "C", 6),
        ("OESTE", "C", 45),
        ("MTSO", "C", 6),
        ("F_PRESTRIB", "D", 8),
        ("DATUM", "C", 6),
        ("ARCHIVO", "C", 100),
        ("CORTE", "C", 10),
        ("EDITOR", "C", 11),
        #("CPU", "C", 80),
    )

    ## fill DBF with some records
    if int(request.POST["fecha"]) != 0:
        diario = Diario.objects.get(pk=int(request.POST["fecha"]))#filter "diario" for date add: tipo_tramite for pedimentos
        solicitudes = diario.registro_mineria_set.all()#get register for specific "diario"
    else:
        solicitudes = Registro_Mineria.objects.all()#Get all register in case that the user wish generate a dbf with all register without care the date
    for solicitud in solicitudes:
        if solicitud.tipo_tramite == "MANIFESTACIONES MINERAS":
            response = db.newRecord()
            #the text after of solicitud. is the attributes
            # response["FDIAR_APRO"] = solicitud.FDIAR_APRO#.strftime("%Y-%M-%D")
            response["BOLETIN"] = solicitud.boletin or ''
            response["F_BOLETIN"] = '' if solicitud.f_boletin is None or len(solicitud.f_boletin)==0 else (datetime.datetime.strptime(solicitud.f_boletin, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["CONCESION"] = '' if solicitud.concesion is None else solicitud.concesion
            response["CONCESIONA"] = '' if solicitud.concesiona is None else solicitud.concesiona
            response["REPRESENTA"] = '' if solicitud.representa is None else solicitud.representa
            response["DIRECCION"] = '' if solicitud.direccion is None else solicitud.direccion
            response["REGION"] = solicitud.region or ''
            response["PROVINCIA"] = '' if solicitud.provincia is None else solicitud.provincia
            response["COMUNA"] = '' if solicitud.comuna is None else solicitud.comuna
            response["LUGAR"] = '' if solicitud.comuna is None else solicitud.comuna
            response["TIPO_UTM"] = solicitud.tipo_utm or ''
            nortepi = 0
            if solicitud.nortepi is not None:
                nortepi = float(solicitud.nortepi)
            response["NORTEPI"] = nortepi or 0
            estepi = 0
            if solicitud.estepi is not None:
                estepi = float(solicitud.estepi)
            response["ESTEPI"] = estepi or 0
            huso = 0
            if solicitud.huso != "No se detecta Huso" and solicitud.huso is not None:
                huso = float(solicitud.huso)
            response["HUSO"] = huso or 0
            n_scarasup = 0
            if solicitud.n_scarasup is not None and len(solicitud.n_scarasup) > 0:
                n_scarasup = float(solicitud.n_scarasup)
            response["N_SCARASUP"] = n_scarasup or 0
            e_ocarasup = 0
            if solicitud.e_ocarasup is not None and len(solicitud.e_ocarasup) > 0:
                e_ocarasup = float(solicitud.e_ocarasup)
            response["E_OCARASUP"] = e_ocarasup or 0
            hectareas = 0
            if solicitud.hectareas is not None:
                hectareas = float(solicitud.hectareas)
            response["HECTAREAS"] = hectareas or 0
            response["HA_PERT"] = '' if solicitud.ha_pert is None else solicitud.ha_pert
            response["JUZGADO"] = '' if solicitud.juzgado is None else solicitud.juzgado
            response["ROLJUZ"] = '' if solicitud.roljuz is None else solicitud.roljuz
            response["F_PRESENTA"] = '' if solicitud.f_presenta is None or len(solicitud.f_presenta)==0 else (datetime.datetime.strptime(solicitud.f_presenta, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_RESOLUCI"] = '' if solicitud.f_resoluci is None or len(solicitud.f_resoluci)==0 else (datetime.datetime.strptime(solicitud.f_resoluci, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_INSCRIBE"] = '' if solicitud.f_resoluci is None or len(solicitud.f_resoluci)==0 else (datetime.datetime.strptime(solicitud.f_resoluci, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["FOJAS"] = '' if solicitud.fojas is None else solicitud.fojas
            response["NUMERO"] = '' if solicitud.numero is None else solicitud.numero
            response["YEAR"] = '' if solicitud.year is None else solicitud.year
            response["CIUDAD"] = '' if solicitud.ciudad is None else solicitud.ciudad
            response["CARTAIGM"] = '' if solicitud.cartaigm is None else solicitud.cartaigm
            response["OBSER"] = '' if solicitud.obser is None else solicitud.obser
            response["PED_ASOC"] = '' if solicitud.ped_asoc is None else solicitud.ped_asoc
            response["FECHAPED"] = '' if solicitud.fechaped is None or len(solicitud.fechaped)==0 else (datetime.datetime.strptime(solicitud.fechaped, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["ROLPED"] = '' if solicitud.rolped is None else solicitud.rolped
            response["TIPOCOORD"] = solicitud.tipocoord or ''
            response["NORTE"] = '' if solicitud.norte is None else solicitud.norte
            response["MTSN"] = '' if solicitud.mtsn is None else solicitud.mtsn
            response["SUR"] = '' if solicitud.sur is None else solicitud.sur
            response["MTSS"] = '' if solicitud.mtss is None else solicitud.mtss
            response["ESTE"] = '' if solicitud.este is None else solicitud.este
            response["MTSE"] = '' if solicitud.mtse is None else solicitud.mtse
            response["OESTE"] = '' if solicitud.oeste is None else solicitud.oeste
            response["MTSO"] = '' if solicitud.mtso is None else solicitud.mtso
            response["F_PRESTRIB"] = '' if solicitud.f_prestrib is None or len(solicitud.f_prestrib)==0 else (datetime.datetime.strptime(solicitud.f_prestrib, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["DATUM"] = '' if solicitud.datum is None else solicitud.datum
            response["ARCHIVO"] = '' if solicitud.archivo is None else solicitud.archivo
            response["CORTE"] = '' if solicitud.corte is None else solicitud.corte
            response["EDITOR"] = '' if solicitud.editor is None else solicitud.editor
            # response["CPU"] = solicitud.cpu or ''
            response.store()
    db.close()
    # pdb.set_trace()
    file_path = os.path.join(settings.BASE_DIR, "Static/" + file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-dbase")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            os.remove(file_path)
            return response
    raise Http404






#Function for create dbf of Coneciones
def download_conce(request):
    da = {}
    file_name = "conce " + str(datetime.datetime.now()) + ".dbf"
    db = dbf.Dbf("Static/" + file_name, new=True)
    db.addField(
        #Add headers to dbf file
        ("BOLETIN", "C", 6),
        ("F_BOLETIN", "D",8),
        ("TIPO_CONCE", "C", 13),
        ("CONCESION", "C", 60),
        ("CONCESIONA", "C", 60),
        ("REPRESENTA", "C", 60),
        ("DIRECCION", "C", 100),
        ("ROLMINERO", "C", 20),
        ("F_SENTENC1", "D",8),
        ("F_SENTENC2", "D",8),
        ("F_PUBEXT", "D",8),
        ("F_INSCMIN", "D",8),
        ("FOJAS", "C", 10),
        ("NUMERO", "C", 6),
        ("YEAR", "C", 4),
        ("CIUDAD", "C", 15),
        ("JUZGADO", "C", 35),
        ("ROLJUZ", "C", 15),
        ("IND_METAL", "C", 1),
        ("REGION", "C", 2),
        ("PROVINCIA", "C", 15),
        ("COMUNA", "C", 20),
        ("LUGAR", "C", 50),
        ("TIPO_UTM", "C", 1),
        ("NORTEPI", "N", 11,2),
        ("ESTEPI", "N", 11,2),
        ("VERTICES", "N", 2),
        ("HA_PERT", "C", 6),
        ("HECTAREAS", "N", 8),
        ("OBSER", "C", 55),
        ("DATUM", "C", 6),
        ("F_PRESTRIB", "D"),
        ("ARCHIVO", "C", 100),
        ("CORTE", "C", 10),
        ("HUSO", "N", 2),
        ("EDITOR", "C", 11),
    )

    ## fill DBF with some records
    if int(request.POST["fecha"]) != 0:
        diario = Diario.objects.get(pk=int(request.POST["fecha"]))#filter "diario" for date add: tipo_tramite for pedimentos
        solicitudes = diario.registro_mineria_set.all()#get register for specific "diario"
    else:
        solicitudes = Registro_Mineria.objects.all()#Get all register in case that the user wish generate a dbf with all register without care the date
    for solicitud in solicitudes:
        if solicitud.tipo_tramite == "EXTRACTOS DE SENTENCIA DE EXPLORACION" or solicitud.tipo_tramite == "EXTRACTOS DE SENTENCIA DE EXPLOTACION":
            response = db.newRecord()
            #the text after of solicitud. is the attributes
            # response["FDIAR_APRO"] = solicitud.FDIAR_APRO#.strftime("%Y-%M-%D")
            response["BOLETIN"] = solicitud.boletin or ''
            response["F_BOLETIN"] = '' if solicitud.f_boletin == None else (datetime.datetime.strptime(solicitud.f_boletin, '%Y/%m/%d').strftime('%Y%m%d') or '')
            response["TIPO_CONCE"] = solicitud.tipo_conce or ''
            response["CONCESION"] = '' if solicitud.concesion is None else solicitud.concesion
            response["CONCESIONA"] = '' if solicitud.concesiona is None else solicitud.concesiona
            response["REPRESENTA"] = '' if solicitud.representa is None else solicitud.representa
            response["DIRECCION"] = '' if solicitud.direccion is None else solicitud.direccion
            response["ROLMINERO"] = '' if solicitud.rolminero is None else solicitud.rolminero
            response["F_SENTENC1"] = '' if solicitud.f_sentenc1 is None or len(solicitud.f_sentenc1)==0 else (datetime.datetime.strptime(solicitud.f_sentenc1, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_SENTENC2"] = '' if solicitud.f_sentenc2 is None or len(solicitud.f_sentenc2)==0 else (datetime.datetime.strptime(solicitud.f_sentenc2, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_PUBEXT"] =  '' if solicitud.f_pubext is None or len(solicitud.f_pubext)==0 else (datetime.datetime.strptime(solicitud.f_pubext, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_INSCMIN"] = '' if solicitud.f_inscmin is None or len(solicitud.f_inscmin)==0 else (datetime.datetime.strptime(solicitud.f_inscmin, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["FOJAS"] = solicitud.fojas or ''
            response["NUMERO"] = solicitud.numero or ''
            response["YEAR"] = solicitud.year or ''
            response["CIUDAD"] = '' if solicitud.ciudad is None else solicitud.ciudad
            response["JUZGADO"] = '' if solicitud.juzgado is None else solicitud.juzgado
            response["ROLJUZ"] = '' if solicitud.roljuz is None else solicitud.roljuz
            response["IND_METAL"] = '' if solicitud.ind_metal is None else solicitud.ind_metal
            response["REGION"] = '' if solicitud.region is None else solicitud.region
            response["PROVINCIA"] = '' if solicitud.provincia is None else solicitud.provincia
            response["COMUNA"] = '' if solicitud.comuna is None else solicitud.comuna
            response["LUGAR"] = '' if solicitud.lugar is None else solicitud.lugar
            response["TIPO_UTM"] = solicitud.tipo_utm or ''
            nortepi = 0
            if solicitud.nortepi is not None:
                nortepi = float(solicitud.nortepi)
            response["NORTEPI"] = nortepi or 0
            estepi = 0
            if solicitud.estepi is not None:
                estepi = float(solicitud.estepi)
            response["ESTEPI"] = estepi or 0
            vertices = 0
            if solicitud.vertices is not None:
                vertices = float(solicitud.vertices)
            response["VERTICES"] = vertices or 0
            response["HA_PERT"] = solicitud.ha_pert or ''
            hectareas = 0
            if solicitud.hectareas is not None:
                hectareas = float(solicitud.hectareas)
            response["HECTAREAS"] = hectareas or 0
            response["OBSER"] = solicitud.obser or ''
            response["DATUM"] = solicitud.datum or ''
            response["F_PRESTRIB"] =  '' if solicitud.f_prestrib is None or len(solicitud.f_prestrib)==0 else (datetime.datetime.strptime(solicitud.f_prestrib, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["ARCHIVO"] = solicitud.archivo or ''
            response["CORTE"] = solicitud.corte or ''
            huso = 0
            if solicitud.huso != "No se detecta Huso" and solicitud.huso is not None:
                huso = float(solicitud.huso)
            response["HUSO"] = huso or 0
            response["EDITOR"] = solicitud.editor or ''
            # response["CPU"] = solicitud.cpu or ''
            response.store()
    db.close()
    # pdb.set_trace()
    file_path = os.path.join(settings.BASE_DIR, "Static/" + file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-dbase")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            os.remove(file_path)
            return response
    raise Http404





#Function for create dbf of Mensuras
def download_mensu(request):
    da = {}
    file_name = "mensu " + str(datetime.datetime.now()) + ".dbf"
    db = dbf.Dbf("Static/" + file_name, new=True)
    db.addField(
        #Add headers to dbf file
        ("BOLETIN", "C", 6),
        ("F_BOLETIN", "D", 8),
        ("CONCESION", "C", 60),
        ("CONCESIONA", "C", 60),
        ("REPRESENTA", "C", 60),
        ("DIRECCION", "C", 100),
        ("JUZGADO", "C", 35),
        ("ROLJUZ", "C", 15),
        ("REGION", "C", 2),
        ("PROVINCIA", "C", 15),
        ("COMUNA", "C", 20),
        ("LUGAR", "C", 50),
        ("TIPO_UTM", "C", 1),
        ("NORTEPI", "N", 11,2),
        ("ESTEPI", "N", 11,2),
        ("VERTICES", "N", 2),
        ("N_SCARASUP", "N", 8),
        ("E_OCARASUP", "N", 8),
        ("HECTAREAS", "N", 8),
        ("F_SOLICITA", "D", 8),
        ("F_RESOLUC", "D", 8),
        ("F_PRESMAN", "D", 8),
        ("F_MENSURA", "D", 8),
        ("N1", "C", 6),
        ("HA1", "C", 8),
        ("N_S1", "C", 8),
        ("E_O1", "C", 8),
        ("N2", "C", 4),
        ("HA2", "C", 6),
        ("N_S2", "C", 8),
        ("E_O2", "C", 8),
        ("N3", "C", 4),
        ("HA3", "C", 6),
        ("N_S3", "C", 8),
        ("E_O3", "C", 8),
        ("N4", "C", 4),
        ("HA4", "C", 6),
        ("N_S4", "C", 8),
        ("E_O4", "C", 8),
        ("HA_PERT", "C", 6),
        ("IND_METAL", "C", 1),
        ("IND_VIGE", "C", 1),
        ("RAZON", "C", 1),
        ("PERITO", "C", 34),
        ("OPOSICION", "C", 50),
        ("DATUM", "C", 6),
        ("F_PRESTRIB", "D", 8),
        ("ARCHIVO", "C", 100),
        ("CORTE", "C", 10),
        ("HUSO", "N", 2),
        ("EDITOR", "C", 11),
        #("CPU", "C", 80),
    )

    ## fill DBF with some records
    if int(request.POST["fecha"]) != 0:
        diario = Diario.objects.get(pk=int(request.POST["fecha"]))#filter "diario" for date add: tipo_tramite for pedimentos
        solicitudes = diario.registro_mineria_set.all()#get register for specific "diario"
    else:
        solicitudes = Registro_Mineria.objects.all()#Get all register in case that the user wish generate a dbf with all register without care the date
    for solicitud in solicitudes:
        if solicitud.tipo_tramite == "SOLICITUDES DE MENSURA":
            response = db.newRecord()
            #the text after of solicitud. is the attributes
            # response["FDIAR_APRO"] = solicitud.FDIAR_APRO#.strftime("%Y-%M-%D")
            response["BOLETIN"] = solicitud.boletin or ''
            response["F_BOLETIN"] = '' if solicitud.f_boletin is None or len(solicitud.f_boletin)==0 else (datetime.datetime.strptime(solicitud.f_boletin, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["CONCESION"] =  '' if solicitud.concesion is None else solicitud.concesion
            response["CONCESIONA"] =  '' if solicitud.concesiona is None else solicitud.concesiona
            response["REPRESENTA"] =  '' if solicitud.representa is None else solicitud.representa
            response["DIRECCION"] =  '' if solicitud.direccion is None else solicitud.direccion
            response["JUZGADO"] =  '' if solicitud.juzgado is None else solicitud.juzgado
            response["ROLJUZ"] =  '' if solicitud.roljuz is None else solicitud.roljuz
            response["REGION"] =  solicitud.region or ''
            response["PROVINCIA"] =  '' if solicitud.provincia is None else solicitud.provincia
            response["COMUNA"] =  '' if solicitud.comuna is None else solicitud.comuna
            response["LUGAR"] =  '' if solicitud.lugar is None else solicitud.lugar
            response["TIPO_UTM"] =  solicitud.tipo_utm or ''
            nortepi = 0
            if solicitud.nortepi is not None:
                nortepi = float(solicitud.nortepi)
            response["NORTEPI"] =  nortepi or 0
            estepi = 0
            if solicitud.estepi is not None:
                estepi = float(solicitud.estepi)
            response["ESTEPI"] =  estepi or 0
            vertices = 0
            if solicitud.vertices is not None:
                vertices = float(solicitud.vertices)
            response["VERTICES"] =  vertices or 0
            n_scarasup = 0
            if solicitud.n_scarasup is not None:
                n_scarasup = float(solicitud.n_scarasup)
            response["N_SCARASUP"] =  n_scarasup or 0
            e_ocarasup = 0
            if solicitud.e_ocarasup is not None:
                e_ocarasup = float(solicitud.e_ocarasup)
            response["E_OCARASUP"] =  e_ocarasup or 0
            hectareas = 0
            if solicitud.hectareas is not None:
                hectareas = float(solicitud.hectareas)
            response["HECTAREAS"] =  hectareas or 0
            response["F_SOLICITA"] =  '' if solicitud.f_solicita is None or len(solicitud.f_solicita)==0 else (datetime.datetime.strptime(solicitud.f_solicita, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_RESOLUC"] =  '' if solicitud.f_resoluci is None or len(solicitud.f_resoluci)==0 else (datetime.datetime.strptime(solicitud.f_resoluci, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_PRESMAN"] =  '' if solicitud.f_presman is None or len(solicitud.f_presman)==0 else (datetime.datetime.strptime(solicitud.f_presman, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_MENSURA"] =  '' if solicitud.f_mensura is None or len(solicitud.f_mensura)==0 else (datetime.datetime.strptime(solicitud.f_mensura, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["N1"] =  '' if solicitud.n1 is None else solicitud.n1
            response["HA1"] =  '' if solicitud.ha1 is None else solicitud.ha1
            response["N_S1"] =  '' if solicitud.n_s1 is None else solicitud.n_s1
            response["E_O1"] =  '' if solicitud.e_o1 is None else solicitud.e_o1
            response["N2"] =  '' if solicitud.n2 is None else solicitud.n2
            response["HA2"] =  '' if solicitud.ha2 is None else solicitud.ha2
            response["N_S2"] =  '' if solicitud.n_s2 is None else solicitud.n_s2
            response["E_O2"] =  '' if solicitud.e_o2 is None else solicitud.e_o2
            response["N3"] =  '' if solicitud.n3 is None else solicitud.n3
            response["HA3"] =  '' if solicitud.ha3 is None else solicitud.ha3
            response["N_S3"] =  '' if solicitud.n_s3 is None else solicitud.n_s3
            response["E_O3"] =  '' if solicitud.e_o3 is None else solicitud.e_o3
            response["N4"] =  '' if solicitud.n4 is None else solicitud.n4
            response["HA4"] =  '' if solicitud.ha4 is None else solicitud.ha4
            response["N_S4"] =  '' if solicitud.n_s4 is None else solicitud.n_s4
            response["E_O4"] =  '' if solicitud.e_o4 is None else solicitud.e_o4
            response["HA_PERT"] =  '' if solicitud.ha_pert is None else solicitud.ha_pert
            response["IND_METAL"] =  '' if solicitud.ind_metal is None else solicitud.ind_metal
            response["IND_VIGE"] =  '' if solicitud.ind_vige is None else solicitud.ind_vige
            response["RAZON"] =  '' if solicitud.razon is None else solicitud.razon
            response["PERITO"] =  '' if solicitud.perito is None else solicitud.perito
            response["OPOSICION"] =  '' if solicitud.oposicion is None else solicitud.oposicion
            response["DATUM"] =  '' if solicitud.datum is None else solicitud.datum
            response["F_PRESTRIB"] =  '' if solicitud.f_prestrib is None or len(solicitud.f_prestrib)==0 else (datetime.datetime.strptime(solicitud.f_prestrib, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["ARCHIVO"] =  '' if solicitud.archivo is None else solicitud.archivo
            response["CORTE"] =  '' if solicitud.corte is None else solicitud.corte
            huso = 0
            if solicitud.huso != "No se detecta Huso" and solicitud.huso is not None:
                huso = float(solicitud.huso)
            response["HUSO"] =  huso or 0
            response["EDITOR"] =  '' if solicitud.editor is None else solicitud.editor
            # response["CPU"] =  solicitud.cpu or ''
            response.store()
    db.close()
    # pdb.set_trace()
    file_path = os.path.join(settings.BASE_DIR, "Static/" + file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-dbase")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            os.remove(file_path)
            return response
    raise Http404






#Function for create dbf of Vertices Coneciones
def download_ver_conce(request):
    da = {}
    file_name = "ver_con " + str(datetime.datetime.now()) + ".dbf"
    db = dbf.Dbf("Static/" + file_name, new=True)
    db.addField(
        #Add headers to dbf file
        ("BOLETIN", "C", 6),
        ("F_BOLETIN", "D",8),
        ("CONCESION", "C", 60),
        ("REGION", "C", 2),
        ("ROLJUZ", "C", 15),
        ("IDENT_LIND", "C", 8),
        ("COORDNORTE", "N", 11,2),
        ("COORDESTE", "N", 11,2),
    )

    ## fill DBF with some records
    solicitudes = Vertice.objects.all()#Get all register in case that the user wish generate a dbf with all register without care the date
    for solicitud in solicitudes:
        if solicitud.registro_mineria.tipo_tramite == "EXTRACTOS DE SENTENCIA DE EXPLORACION" or solicitud.registro_mineria.tipo_tramite == "EXTRACTOS DE SENTENCIA DE EXPLORACION":
            response = db.newRecord()
            #the text after of solicitud. is the attributes
            # response["FDIAR_APRO"] = solicitud.FDIAR_APRO#.strftime("%Y-%M-%D")
            response["BOLETIN"] = solicitud.boletin or ''
            response["F_BOLETIN"] = '' if solicitud.f_boletin is None or len(solicitud.f_boletin)==0 else (datetime.datetime.strptime(solicitud.f_boletin, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["CONCESION"] = '' if solicitud.concesion is None else solicitud.concesion
            response["REGION"] = solicitud.region or ''
            response["ROLJUZ"] = '' if solicitud.roljuz is None else solicitud.roljuz
            response["IDENT_LIND"] = solicitud.ident_lind or 0
            coordnorte = 0 
            if solicitud.coordnorte is not None:
                coordnorte = float(solicitud.coordnorte)
            response["COORDNORTE"] = coordnorte or 0
            coordeste = 0 
            if solicitud.coordeste is not None:
                coordeste = float(solicitud.coordeste)
            response["COORDESTE"] = coordeste or 0
            # response["CPU"] = solicitud.cpu or ''
            response.store()
    db.close()
    # pdb.set_trace()
    file_path = os.path.join(settings.BASE_DIR, "Static/" + file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-dbase")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            #os.remove(file_path)
            return response
    raise Http404





#Function for create dbf of Vertices Mensuras
def download_ver_mensu(request):
    da = {}
    file_name = "ver_mensu " + str(datetime.datetime.now()) + ".dbf"
    db = dbf.Dbf("Static/" + file_name, new=True)
    db.addField(
        #Add headers to dbf file
        ("BOLETIN", "C", 6),
        ("F_BOLETIN", "D",8),
        ("CONCESION", "C", 60),
        ("REGION", "C", 2),
        ("ROLJUZ", "C", 15),
        ("IDENT_LIND", "C", 8),
        ("COORDNORTE", "N", 11,2),
        ("COORDESTE", "N", 11,2),
    )

    ## fill DBF with some records
    solicitudes = Vertice.objects.all()#Get all register in case that the user wish generate a dbf with all register without care the date
    for solicitud in solicitudes:
        if solicitud.registro_mineria.tipo_tramite == "SOLICITUDES DE MENSURA":
            response = db.newRecord()
            #the text after of solicitud. is the attributes
            # response["FDIAR_APRO"] = solicitud.FDIAR_APRO#.strftime("%Y-%M-%D")
            response["BOLETIN"] = solicitud.boletin or ''
            response["F_BOLETIN"] = '' if solicitud.f_boletin is None or len(solicitud.f_boletin)==0 else (datetime.datetime.strptime(solicitud.f_boletin, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["CONCESION"] = '' if solicitud.concesion is None else solicitud.concesion
            response["REGION"] = solicitud.region or ''
            response["ROLJUZ"] = '' if solicitud.roljuz is None else solicitud.roljuz
            response["IDENT_LIND"] = solicitud.ident_lind or 0
            coordnorte = 0 
            if solicitud.coordnorte is not None:
                coordnorte = float(solicitud.coordnorte)
            response["COORDNORTE"] = coordnorte or 0
            coordeste = 0 
            if solicitud.coordeste is not None:
                coordeste = float(solicitud.coordeste)
            response["COORDESTE"] = coordeste or 0
            # response["CPU"] = solicitud.cpu or ''
            response.store()
    db.close()
    # pdb.set_trace()
    file_path = os.path.join(settings.BASE_DIR, "Static/" + file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-dbase")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            os.remove(file_path)
            return response
    raise Http404