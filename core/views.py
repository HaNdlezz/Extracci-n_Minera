from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from core.models import *
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

@login_required(login_url='/')
def descargar_boletin(request):
    response = {}
    tipos = ["PEDIMENTOS MINEROS","MANIFESTACIONES MINERAS","SOLICITUDES DE MENSURA","EXTRACTOS ARTICULO 83","CITACIONES A JUNTAS Y ASAMBLEA", "EXTRACTOS DE SENTENCIA DE EXPLORACION","EXTRACTOS DE SENTENCIA DE EXPLOTACION","PRORROGAS CONCESION DE EXPLORACION","RENUNCIAS DE CONCESION MINERA","ACUERDOS JUNTA DE ACCIONISTAS","NOMINA CONCESIONES PARA REMATE","NOMINA BENEFICIADOS PATENTE REBAJADA","NOMINA DE CONCESIONES ART. 90","VIGENCIA INSCRIPCION ACTAS DE MENSURA","OTRAS PUBLICACIONES","EXTRACTOS DE SENTENCIA DE EXPLORACION"]
    print request.POST
    os.system('wget -U "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4" ' + request.POST["archivo"])
    name = request.POST["archivo"].split("/")[::-1]
    archivo=str(name[0])
    print "ARCHIVO",type(archivo)
    text = getPDFContent(archivo)
    for x in tipos:
        if x in text:
            text = text.replace(x,"SEPARADOR DE TIPOS DE MINERIA "+x+"TERMINO SEPARADOR")
    datos = text.split("SEPARADOR DE TIPOS DE MINERIA ")
    datos.pop(0)
    codigo_diario = request.POST["archivo"].split("/")
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
    return HttpResponseRedirect(reverse_lazy('index'))

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
    if "PEDIMENTOS" in concesion.tipo_tramite:
        concesion.tipo_conce = "PED"
    if "MANIFESTACIONES" in concesion.tipo_tramite:
        concesion.tipo_conce = "MAN"
    patron = re.compile("Huso\s\d\d|HUSO\s\d\d|huso\s\d\d")
    if patron.search(concesion.texto):
        print patron.search(concesion.texto).group()
        huso = patron.search(concesion.texto).group()
        huso = huso.split(" ")
        concesion.huso = huso[-1]
    else:
        concesion.huso = "No se detecta Huso"
    patron = re.compile("datum\sWGS\s\d\d|datum\sWGS\s\d\d\d\d|Datum\sWGS\s\d\d|Datum\sWGS\s\d\d\d\d|Datum\sWGS\s\d\d\d\d|DATUM\sWGS\s\d\d|DATUM\sWGS\s\d\d\d\d|datum\s\d\d|datum\s\d\d\d\d|Datum\s\d\d|Datum\s\d\d\d\d|DATUM\s\d\d|DATUM\s\d\d\d\d")
    patron2 = re.compile("DATUM\sWGS\d\d|DATUM\sWGS\d\d\d\d|Datum\sWGS\d\d|Datum\sWGS\d\d\d\d|datum\sWGS\d\d|datum\sWGS\d\d\d\d")
    if patron.search(concesion.texto):
        datum = patron.search(concesion.texto).group()
        datum = datum.split(" ")
        datum = datum[-1]
    elif patron2.search(concesion.texto):
        datum = patron2.search(x.texto).group()
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
        datum = patron.search(concesion.texto).group()
    concesion.datum = datum 
    concesion.save()
    print concesion

def Obtener_Datos_General(request):
    codes = []
    diario = Diario.objects.get(pk=int(request.POST["pk_diario_2"]))
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
        if x.tipo_tramite=="MANIFESTACIONES MINERAS" or x.tipo_tramite=="PEDIMENTOS MINEROS":
            extraerConcesiones(x)
    return HttpResponseRedirect(reverse_lazy('Historic_Data'))

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
    response["CVE"] = registro.cve
    print registro.tipo_tramite
    print response
    return HttpResponse(
        json.dumps(response),
        content_type="application/json"
        )

def actualizar_datos(request):
    registro = Registro_Mineria.objects.get(pk=request.POST["pk"])
    registro.boletin = request.POST["BOLETIN"]
    registro.f_boletin = request.POST["F_BOLETIN"]
    registro.concesion = request.POST["CONCESION"]
    registro.concesiona = request.POST["CONCESIONA"]
    registro.representa = request.POST["REPRESENTA"]
    registro.region = request.POST["REGION"]
    registro.provincia = request.POST["PROVINCIA"]
    registro.comuna = request.POST["COMUNA"]
    registro.direccion = request.POST["DIRECCION"]
    registro.tipo_utm = request.POST["TIPO_UTM"]
    registro.nortepi = request.POST["NORTEPI"]
    registro.estepi = request.POST["ESTEPI"]
    registro.huso = request.POST["HUSO"]
    registro.fecha_sentencia1 = request.POST["FECHA_SENTENCIA1"]
    registro.fecha_sentencia2 = request.POST["FECHA_SENTENCIA2"]
    registro.editor = request.POST["EDITOR"]
    registro.ha_pert = request.POST["HA_PERT"]
    registro.juzgado = request.POST["JUZGADO"]
    registro.roljuz = request.POST["ROLJUZ"]
    registro.f_pubext = request.POST["F_PUBEXT"]
    registro.f_inscmin = request.POST["F_INSCMIN"]
    registro.vertices = request.POST["VERTICES"]
    registro.datum = request.POST["DATUM"]
    registro.numero = request.POST["NUMERO"]
    registro.fojas = request.POST["FOJAS"]
    registro.year = request.POST["YEAR"]
    registro.ciudad = request.POST["CIUDAD"]
    registro.cartaigm = request.POST["CARTAIGM"]
    registro.obser = request.POST["OBSER"]
    registro.ped_asoc = request.POST["PED_ASOC"]
    registro.fechaped = request.POST["FECHAPED"]
    registro.rol_minero = request.POST["ROL_MINERO"]
    registro.tipocoord = request.POST["TIPOCOORD"]
    registro.norte = request.POST["NORTE"]
    registro.mtsn = request.POST["MTSN"]
    registro.sur = request.POST["SUR"]
    registro.mtss = request.POST["MTSS"]
    registro.este = request.POST["ESTE"]
    registro.mtse = request.POST["MTSE"]
    registro.oeste = request.POST["OESTE"]
    registro.mtso = request.POST["MTSO"]
    registro.tipo_conce = request.POST["TIPO_CONCE"]
    registro.cve = request.POST["CVE"]
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
    patron3 = re.compile("[VP]\d")
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
    else:
        response["ok"] = -1
    return HttpResponse(
        json.dumps(response),
        content_type="application/json"
        )

def excel_registros(request):
    template_name = 'reporte_registros.html'
    data = {}
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
        worksheet.write(0, 7, 'ROL_MINERO')
        worksheet.write(0, 8, 'FECHA_SENTENCIA1')
        worksheet.write(0, 9, 'FECHA_SENTENCIA2')
        worksheet.write(0, 10, 'F_PUBEXT')
        worksheet.write(0, 11, 'F_INSCMIN')
        worksheet.write(0, 12, 'FOJAS')
        worksheet.write(0, 13, 'NUMERO')
        worksheet.write(0, 14, 'YEAR')
        worksheet.write(0, 15, 'CIUDAD')
        worksheet.write(0, 16, 'JUZGADO')
        worksheet.write(0, 17, 'ROLJUZ')
        worksheet.write(0, 18, 'REGION')
        worksheet.write(0, 19, 'PROVINCIA')
        worksheet.write(0, 20, 'COMUNA')
        worksheet.write(0, 21, 'LUGAR')
        worksheet.write(0, 22, 'TIPO_UTM')
        worksheet.write(0, 23, 'NORTEPI')
        worksheet.write(0, 24, 'ESTEPI')
        worksheet.write(0, 25, 'VERTICES')
        worksheet.write(0, 26, 'HA_PERT')
        worksheet.write(0, 27, 'HECTAREAS')
        worksheet.write(0, 28, 'OBSER')
        worksheet.write(0, 29, 'DATUM')
        worksheet.write(0, 30, 'F_PRESTRIB')
        worksheet.write(0, 31, 'ARCHIVO')
        worksheet.write(0, 32, 'HUSO')
        worksheet.write(0, 33, 'EDITOR')
        cont2=1
        cont = 1
        for x in Registro_Mineria.objects.all():
            try:
                nulo = len(str(x.concesion))
            except:
                nulo = len(str(unidecode.unidecode(x.concesion)))
            if  nulo> 4 and str(x.region)=="2":
                try:
                    fechaFormato = str(x.f_boletin).split("/")
                    fechaFormato =fechaFormato[2]+"/"+fechaFormato[1]+"/"+fechaFormato[0]
                    worksheet.write(cont, 0, x.boletin)
                    worksheet.write(cont, 1, fechaFormato)
                    worksheet.write(cont, 2, x.tipo_conce)
                    worksheet.write(cont, 3, x.concesion)
                    worksheet.write(cont, 4, x.concesiona)
                    worksheet.write(cont, 5, x.representa)
                    worksheet.write(cont, 6, x.direccion)
                    worksheet.write(cont, 7, x.rol_minero)
                    worksheet.write(cont, 8, x.fecha_sentencia1)
                    worksheet.write(cont, 9, x.fecha_sentencia2)
                    worksheet.write(cont, 10, x.f_pubext)
                    worksheet.write(cont, 11, x.f_inscmin)
                    worksheet.write(cont, 12, x.fojas)
                    worksheet.write(cont, 13, x.numero)
                    worksheet.write(cont, 14, x.year)
                    worksheet.write(cont, 15, x.ciudad)
                    worksheet.write(cont, 16, x.juzgado)
                    worksheet.write(cont, 17, x.roljuz)
                    worksheet.write(cont, 18, x.region)
                    worksheet.write(cont, 19, x.provincia)
                    worksheet.write(cont, 20, x.comuna)
                    worksheet.write(cont, 21, "")
                    worksheet.write(cont, 22, x.tipo_utm)
                    worksheet.write(cont, 23, x.nortepi)
                    worksheet.write(cont, 24, x.estepi)
                    worksheet.write(cont, 25, x.vertices)
                    worksheet.write(cont, 26, "")
                    worksheet.write(cont, 27, x.ha_pert)
                    worksheet.write(cont, 28, x.obser)
                    worksheet.write(cont, 29, x.datum)
                    worksheet.write(cont, 30, "")
                    worksheet.write(cont, 31, "")
                    worksheet.write(cont, 32, x.huso)
                    worksheet.write(cont, 33, x.editor)
                    cont += 1
                except:
                    print cont2
                cont2+=1
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
