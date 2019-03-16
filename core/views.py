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
    # pdf = pyPdf.PdfFileReader(file(path, "rb"))
    # # Iterate pages
    # for i in range(0, pdf.getNumPages()):
    #     # Extract text from page and add to content
    #     # temp_cont = unidecode.unidecode(pdf.getPage(i).extractText()) + " \n"
    #     # content += " ".join(temp_cont.replace(u"\xa0", u" ").strip().split())
    #     for line in pdf.getPage(i).extractText().splitlines():
    #         content += unidecode.unidecode(line) + " \n"
    os.system("ruby pdf_reader.rb '" + path + "'")
    temp_file = open(path.split('.')[0] + ".txt")
    content = temp_file.read()
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
    # print "ARCHIVO",type(archivo)
    text = getPDFContent(archivo)
    # pdb.set_trace()
    for x in tipos:
        if x in text:
            text = text.replace(x,"SEPARADOR DE TIPOS DE MINERIA "+x+"TERMINO SEPARADOR")
    datos = text.split("SEPARADOR DE TIPOS DE MINERIA ")
    # pdb.set_trace()
    datos.pop(0)
    codigo_diario = request["archivo"].split("/")
    format_fecha = codigo_diario[4] + "/" + codigo_diario[5] + "/" + codigo_diario[6]
    diario = Diario.objects.create(codigo=name[0].split(".pdf")[0],fecha=format_fecha)
    diario.save()
    region = '' # TODO: WORKING HERE
    concesion = ''
    concesiona = ''
    for y in datos:
        tipo = y.split("TERMINO SEPARADOR")[0]
        for x in y.split(")"):
            if "CVE:" in x:
                try:
                    print "NEW CVE"
                    temp_x = x
                    if "Provincia de " in x:
                        x = temp_x.split('Provincia de ')[1].split("(")[1].replace(" ","")
                        cve = x.split("CVE:")[1]
                        concesion = temp_x.split('Provincia de ')[1].split('(')[0].split('/')[0]
                        concesiona = temp_x.split('Provincia de ')[1].split('(')[0].split('/')[1]
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

                    os.system('wget -U "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4" ' + "http://www.diariooficial.interior.gob.cl/publicaciones/"+ str(name[4]) +"/" +str(name[3]) +"/" + str(name[2]) + "/" + name[0].split(".pdf")[0] + "/07/" + str(cve) + ".pdf")
                    url = "http://www.diariooficial.interior.gob.cl/publicaciones/"+ str(name[4]) +"/" +str(name[3]) +"/" + str(name[2]) + "/" + name[0].split(".pdf")[0] + "/07/" + str(cve) + ".pdf"
                    aux = Registro_Mineria.objects.create(concesion=concesion,concesiona=concesiona,diario=diario,tipo_tramite=tipo,url=url,cve=cve,texto=getPDFContent(str(cve)+".pdf"))
                    aux.save()
                    cve_downloaded+=1
                    os.system('rm ' + cve+".pdf")
                    os.system('rm ' + cve+".txt")

                    print "END OF CVE SUCESSFULLY"
                except:
                    print "END OF CVE WITH ERROR: " + cve
                    os.system('rm ' + cve+".pdf")
                    os.system('rm ' + cve+".txt")
                    pass
        # aux_anterior = None
#    pedimentos = text.split("MANIFESTACIONES MINERAS")[0]
#    text = text.split("MANIFESTACIONES MINERAS")[1]
#    pedimentos = pedimentos.split("(")
#    pedimentos_final = []
#    for x in pedimentos:
#        if "CVE" in x:
#            x = x.split("CVE:")[1].split(")")[0].replace(" ","")
#            pedimentos_final.append(x)
    os.system('rm ' + name[0])
    os.system('rm ' + name[0].split('.')[0] +".txt")
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

def get_region(codigo, texto):
    #pdb.set_trace()
    regiones = [{"codigo":"15","tipo":"region","nombre":"Arica y Parinacota","lat":-18.5075,"lng":-69.6451,"url":"","codigo_padre":"00"},{"codigo":"01","tipo":"region","nombre":"Tarapac\u00e1","lat":-20.164,"lng":-69.5541,"url":"","codigo_padre":"00"},{"codigo":"02","tipo":"region","nombre":"Antofagasta","lat":-23.7503,"lng":-69.6,"url":"","codigo_padre":"00"},{"codigo":"03","tipo":"region","nombre":"Atacama","lat":-27.5276,"lng":-70.2494,"url":"","codigo_padre":"00"},{"codigo":"04","tipo":"region","nombre":"Coquimbo","lat":-30.8301,"lng":-70.9816,"url":"","codigo_padre":"00"},{"codigo":"05","tipo":"region","nombre":"Valpara\u00edso","lat":-32.9039,"lng":-71.0262,"url":"","codigo_padre":"00"},{"codigo":"13","tipo":"region","nombre":"Metropolitana de Santiago","lat":-33.4417,"lng":-70.6541,"url":"","codigo_padre":"00"},{"codigo":"06","tipo":"region","nombre":"Del Libertador Gral. Bernardo O\u2019Higgins","lat":-34.4294,"lng":-71.0393,"url":"","codigo_padre":"00"},{"codigo":"07","tipo":"region","nombre":"Del Maule","lat":-35.5892,"lng":-71.5007,"url":"","codigo_padre":"00"},{"codigo":"08","tipo":"region","nombre":"Del Biob\u00edo","lat":-37.2442,"lng":-72.4661,"url":"","codigo_padre":"00"},{"codigo":"09","tipo":"region","nombre":"De la Araucan\u00eda","lat":-38.5505,"lng":-72.4382,"url":"","codigo_padre":"00"},{"codigo":"14","tipo":"region","nombre":"De los R\u00edos","lat":-39.9086,"lng":-72.7034,"url":"","codigo_padre":"00"},{"codigo":"10","tipo":"region","nombre":"De los Lagos","lat":-42.1071,"lng":-72.6425,"url":"","codigo_padre":"00"},{"codigo":"11","tipo":"region","nombre":"Ays\u00e9n del Gral. Carlos Ib\u00e1\u00f1ez del Campo","lat":-46.2772,"lng":-73.6628,"url":"","codigo_padre":"00"},{"codigo":"12","tipo":"region","nombre":"Magallanes y de la Ant\u00e1rtica Chilena","lat":-54.3551,"lng":-70.5284,"url":"","codigo_padre":"00"}]
    for region in regiones:
        if region["codigo"] == codigo:
            aux_region = region["nombre"].decode("raw_unicode_escape")
            aux_region = aux_region
            # aux_region = unidecode.unidecode(aux_region)
            if aux_region in texto:
                return region["codigo"]
    return ""

def get_provincia(codigo, texto):
    provincias = [{"codigo":"122","tipo":"provincia","nombre":"Ant\u00e1rtica Chilena","lat":-55.028,"lng":-67.6318,"url":"","codigo_padre":"12"},{"codigo":"021","tipo":"provincia","nombre":"Antofagasta","lat":-24.5646,"lng":-69.2877,"url":"","codigo_padre":"02"},{"codigo":"082","tipo":"provincia","nombre":"Arauco","lat":-37.7277,"lng":-73.3075,"url":"","codigo_padre":"08"},{"codigo":"151","tipo":"provincia","nombre":"Arica","lat":-18.7139,"lng":-69.7522,"url":"","codigo_padre":"15"},{"codigo":"112","tipo":"provincia","nombre":"Ays\u00e9n","lat":-46.3848,"lng":-72.2955,"url":"","codigo_padre":"11"},{"codigo":"083","tipo":"provincia","nombre":"Biob\u00edo","lat":-37.4739,"lng":-72.1572,"url":"","codigo_padre":"08"},{"codigo":"061","tipo":"provincia","nombre":"Cachapoal","lat":-36.45,"lng":-71.7333,"url":"","codigo_padre":"06"},{"codigo":"113","tipo":"provincia","nombre":"Capit\u00e1n Prat","lat":-47.9232,"lng":-72.9245,"url":"","codigo_padre":"11"},{"codigo":"062","tipo":"provincia","nombre":"Cardenal Caro","lat":-34.2812,"lng":-71.8571,"url":"","codigo_padre":"06"},{"codigo":"072","tipo":"provincia","nombre":"Cauquenes","lat":-35.9738,"lng":-72.3142,"url":"","codigo_padre":"07"},{"codigo":"091","tipo":"provincia","nombre":"Caut\u00edn","lat":-38.727,"lng":-72.5989,"url":"","codigo_padre":"09"},{"codigo":"133","tipo":"provincia","nombre":"Chacabuco","lat":-33.1503,"lng":-70.7132,"url":"","codigo_padre":"13"},{"codigo":"032","tipo":"provincia","nombre":"Cha\u00f1aral","lat":-26.3599,"lng":-70.5981,"url":"","codigo_padre":"03"},{"codigo":"102","tipo":"provincia","nombre":"Chilo\u00e9","lat":-43.117,"lng":-73.9984,"url":"","codigo_padre":"10"},{"codigo":"042","tipo":"provincia","nombre":"Choapa","lat":-31.8006,"lng":-70.9827,"url":"","codigo_padre":"04"},{"codigo":"111","tipo":"provincia","nombre":"Coihaique","lat":-45.2865,"lng":-71.7792,"url":"","codigo_padre":"11"},{"codigo":"063","tipo":"provincia","nombre":"Colchagua","lat":-34.6761,"lng":-71.0973,"url":"","codigo_padre":"06"},{"codigo":"081","tipo":"provincia","nombre":"Concepci\u00f3n","lat":-36.8148,"lng":-73.0293,"url":"","codigo_padre":"08"},{"codigo":"031","tipo":"provincia","nombre":"Copiap\u00f3","lat":-27.5765,"lng":-70.0269,"url":"","codigo_padre":"03"},{"codigo":"132","tipo":"provincia","nombre":"Cordillera","lat":-33.6984,"lng":-70.1682,"url":"","codigo_padre":"13"},{"codigo":"073","tipo":"provincia","nombre":"Curic\u00f3","lat":-35.1704,"lng":-70.8954,"url":"","codigo_padre":"07"},{"codigo":"022","tipo":"provincia","nombre":"El Loa","lat":-22.3196,"lng":-68.5107,"url":"","codigo_padre":"02"},{"codigo":"041","tipo":"provincia","nombre":"Elqui","lat":-29.8335,"lng":-70.8014,"url":"","codigo_padre":"04"},{"codigo":"114","tipo":"provincia","nombre":"General Carrera","lat":-46.557,"lng":-72.4123,"url":"","codigo_padre":"11"},{"codigo":"033","tipo":"provincia","nombre":"Huasco","lat":-28.5604,"lng":-70.6146,"url":"","codigo_padre":"03"},{"codigo":"011","tipo":"provincia","nombre":"Iquique","lat":-20.8011,"lng":-70.0963,"url":"","codigo_padre":"01"},{"codigo":"052","tipo":"provincia","nombre":"Isla de Pascua","lat":-27.1212,"lng":-109.366,"url":"","codigo_padre":"05"},{"codigo":"043","tipo":"provincia","nombre":"Limar\u00ed","lat":-30.7342,"lng":-70.9957,"url":"","codigo_padre":"04"},{"codigo":"074","tipo":"provincia","nombre":"Linares","lat":-35.8495,"lng":-71.585,"url":"","codigo_padre":"07"},{"codigo":"101","tipo":"provincia","nombre":"Llanquihue","lat":-41.453,"lng":-72.6135,"url":"","codigo_padre":"10"},{"codigo":"053","tipo":"provincia","nombre":"Los Andes","lat":-32.9544,"lng":-70.3163,"url":"","codigo_padre":"05"},{"codigo":"121","tipo":"provincia","nombre":"Magallanes","lat":-53.6316,"lng":-71.5924,"url":"","codigo_padre":"12"},{"codigo":"134","tipo":"provincia","nombre":"Maipo","lat":-33.7963,"lng":-70.7353,"url":"","codigo_padre":"13"},{"codigo":"092","tipo":"provincia","nombre":"Malleco","lat":-37.803,"lng":-72.7017,"url":"","codigo_padre":"09"},{"codigo":"058","tipo":"provincia","nombre":"Marga Marga","lat":-33.065,"lng":-71.3711,"url":"","codigo_padre":"05"},{"codigo":"135","tipo":"provincia","nombre":"Melipilla","lat":-33.7369,"lng":-71.1743,"url":"","codigo_padre":"13"},{"codigo":"084","tipo":"provincia","nombre":"\u00d1uble","lat":-36.6191,"lng":-72.0182,"url":"","codigo_padre":"08"},{"codigo":"103","tipo":"provincia","nombre":"Osorno","lat":-40.7369,"lng":-72.9849,"url":"","codigo_padre":"10"},{"codigo":"104","tipo":"provincia","nombre":"Palena","lat":-43.4449,"lng":-72.0923,"url":"","codigo_padre":"10"},{"codigo":"152","tipo":"provincia","nombre":"Parinacota","lat":-18.3135,"lng":-69.3788,"url":"","codigo_padre":"15"},{"codigo":"054","tipo":"provincia","nombre":"Petorca","lat":-32.1965,"lng":-70.8318,"url":"","codigo_padre":"05"},{"codigo":"055","tipo":"provincia","nombre":"Quillota","lat":-32.9009,"lng":-71.2947,"url":"","codigo_padre":"05"},{"codigo":"142","tipo":"provincia","nombre":"Ranco","lat":-40.4114,"lng":-72.4988,"url":"","codigo_padre":"14"},{"codigo":"056","tipo":"provincia","nombre":"San Antonio","lat":-33.6648,"lng":-71.4597,"url":"","codigo_padre":"05"},{"codigo":"057","tipo":"provincia","nombre":"San Felipe de Aconcagua","lat":-32.7464,"lng":-70.7489,"url":"","codigo_padre":"05"},{"codigo":"131","tipo":"provincia","nombre":"Santiago","lat":-33.4417,"lng":-70.6541,"url":"","codigo_padre":"13"},{"codigo":"136","tipo":"provincia","nombre":"Talagante","lat":-33.6665,"lng":-70.9331,"url":"","codigo_padre":"13"},{"codigo":"071","tipo":"provincia","nombre":"Talca","lat":-35.3921,"lng":-71.6125,"url":"","codigo_padre":"07"},{"codigo":"014","tipo":"provincia","nombre":"Tamarugal","lat":-39.8567,"lng":-72.6089,"url":"","codigo_padre":"01"},{"codigo":"123","tipo":"provincia","nombre":"Tierra del Fuego","lat":-53.7422,"lng":-69.2249,"url":"","codigo_padre":"12"},{"codigo":"023","tipo":"provincia","nombre":"Tocopilla","lat":-22.2306,"lng":-69.4666,"url":"","codigo_padre":"02"},{"codigo":"124","tipo":"provincia","nombre":"\u00daltima Esperanza","lat":-51.0163,"lng":-73.4285,"url":"","codigo_padre":"12"},{"codigo":"141","tipo":"provincia","nombre":"Valdivia","lat":-39.7811,"lng":-72.5098,"url":"","codigo_padre":"14"},{"codigo":"051","tipo":"provincia","nombre":"Valpara\u00edso","lat":-33.1381,"lng":-71.5617,"url":"","codigo_padre":"05"}]
    for provincia in provincias:
        if provincia["codigo"] == codigo:
            aux_provincia = provincia["nombre"].decode("raw_unicode_escape")
            aux_provincia = aux_provincia
            # aux_provincia = unidecode.unidecode(aux_provincia)
            if aux_provincia in texto:
                return aux_provincia, get_region(provincia["codigo_padre"],texto)
    return []

def get_comuna(texto):
    # pdb.set_trace()
    comunas = [{"codigo":"05602","tipo":"comuna","nombre":"Algarrobo","lat":-33.3332,"lng":-71.6023,"url":"","codigo_padre":"056"},{"codigo":"13502","tipo":"comuna","nombre":"Alhu\u00e9","lat":-34.0355,"lng":-71.028,"url":"","codigo_padre":"135"},{"codigo":"08314","tipo":"comuna","nombre":"Alto Biob\u00edo","lat":-37.8708,"lng":-71.6106,"url":"","codigo_padre":"083"},{"codigo":"03302","tipo":"comuna","nombre":"Alto del Carmen","lat":-28.7508,"lng":-70.4883,"url":"","codigo_padre":"033"},{"codigo":"01107","tipo":"comuna","nombre":"Alto Hospicio","lat":-20.2677,"lng":-70.1007,"url":"","codigo_padre":"011"},{"codigo":"10202","tipo":"comuna","nombre":"Ancud","lat":-41.8657,"lng":-73.8336,"url":"","codigo_padre":"102"},{"codigo":"04103","tipo":"comuna","nombre":"Andacollo","lat":-30.2357,"lng":-71.0828,"url":"","codigo_padre":"041"},{"codigo":"09201","tipo":"comuna","nombre":"Angol","lat":-37.803,"lng":-72.7017,"url":"","codigo_padre":"092"},{"codigo":"12202","tipo":"comuna","nombre":"Ant\u00e1rtica","lat":-64.3589,"lng":-60.8203,"url":"","codigo_padre":"122"},{"codigo":"02101","tipo":"comuna","nombre":"Antofagasta","lat":-23.6499,"lng":-70.4069,"url":"","codigo_padre":"021"},{"codigo":"08302","tipo":"comuna","nombre":"Antuco","lat":-37.3273,"lng":-71.6775,"url":"","codigo_padre":"083"},{"codigo":"08202","tipo":"comuna","nombre":"Arauco","lat":-37.257,"lng":-73.2839,"url":"","codigo_padre":"082"},{"codigo":"15101","tipo":"comuna","nombre":"Arica","lat":-18.477,"lng":-70.3221,"url":"","codigo_padre":"151"},{"codigo":"11201","tipo":"comuna","nombre":"Ays\u00e9n","lat":-45.3975,"lng":-72.6993,"url":"","codigo_padre":"112"},{"codigo":"13402","tipo":"comuna","nombre":"Buin","lat":-33.754,"lng":-70.7163,"url":"","codigo_padre":"134"},{"codigo":"08402","tipo":"comuna","nombre":"Bulnes","lat":-36.7422,"lng":-72.3018,"url":"","codigo_padre":"084"},{"codigo":"05402","tipo":"comuna","nombre":"Cabildo","lat":-32.4095,"lng":-71.0798,"url":"","codigo_padre":"054"},{"codigo":"12201","tipo":"comuna","nombre":"Cabo de Hornos","lat":-54.9352,"lng":-67.6041,"url":"","codigo_padre":"122"},{"codigo":"08303","tipo":"comuna","nombre":"Cabrero","lat":-37.0374,"lng":-72.4057,"url":"","codigo_padre":"083"},{"codigo":"02201","tipo":"comuna","nombre":"Calama","lat":-22.4542,"lng":-68.9337,"url":"","codigo_padre":"022"},{"codigo":"10102","tipo":"comuna","nombre":"Calbuco","lat":-41.7775,"lng":-73.1415,"url":"","codigo_padre":"101"},{"codigo":"03102","tipo":"comuna","nombre":"Caldera","lat":-27.0668,"lng":-70.817,"url":"","codigo_padre":"031"},{"codigo":"05502","tipo":"comuna","nombre":"Calera","lat":-32.7837,"lng":-71.1586,"url":"","codigo_padre":"055"},{"codigo":"13403","tipo":"comuna","nombre":"Calera de Tango","lat":-33.6326,"lng":-70.7821,"url":"","codigo_padre":"134"},{"codigo":"05302","tipo":"comuna","nombre":"Calle Larga","lat":-32.9514,"lng":-70.5524,"url":"","codigo_padre":"053"},{"codigo":"15102","tipo":"comuna","nombre":"Camarones","lat":-19.0089,"lng":-69.9074,"url":"","codigo_padre":"151"},{"codigo":"01402","tipo":"comuna","nombre":"Cami\u00f1a","lat":-19.3118,"lng":-69.4264,"url":"","codigo_padre":"014"},{"codigo":"04202","tipo":"comuna","nombre":"Canela","lat":-31.3935,"lng":-71.4578,"url":"","codigo_padre":"042"},{"codigo":"08203","tipo":"comuna","nombre":"Ca\u00f1ete","lat":-37.8039,"lng":-73.4016,"url":"","codigo_padre":"082"},{"codigo":"09102","tipo":"comuna","nombre":"Carahue","lat":-38.7116,"lng":-73.1651,"url":"","codigo_padre":"091"},{"codigo":"05603","tipo":"comuna","nombre":"Cartagena","lat":-33.5341,"lng":-71.4628,"url":"","codigo_padre":"056"},{"codigo":"05102","tipo":"comuna","nombre":"Casablanca","lat":-33.3262,"lng":-71.3983,"url":"","codigo_padre":"051"},{"codigo":"10201","tipo":"comuna","nombre":"Castro","lat":-42.48,"lng":-73.7625,"url":"","codigo_padre":"102"},{"codigo":"05702","tipo":"comuna","nombre":"Catemu","lat":-32.6981,"lng":-70.956,"url":"","codigo_padre":"057"},{"codigo":"07201","tipo":"comuna","nombre":"Cauquenes","lat":-35.9738,"lng":-72.3142,"url":"","codigo_padre":"072"},{"codigo":"13102","tipo":"comuna","nombre":"Cerrillos","lat":-33.497,"lng":-70.7112,"url":"","codigo_padre":"131"},{"codigo":"13103","tipo":"comuna","nombre":"Cerro Navia","lat":-33.4267,"lng":-70.7434,"url":"","codigo_padre":"131"},{"codigo":"10401","tipo":"comuna","nombre":"Chait\u00e9n","lat":-42.9168,"lng":-72.7164,"url":"","codigo_padre":"104"},{"codigo":"03201","tipo":"comuna","nombre":"Cha\u00f1aral","lat":-26.3425,"lng":-70.6107,"url":"","codigo_padre":"032"},{"codigo":"07202","tipo":"comuna","nombre":"Chanco","lat":-35.7337,"lng":-72.5333,"url":"","codigo_padre":"072"},{"codigo":"06302","tipo":"comuna","nombre":"Ch\u00e9pica","lat":-34.7303,"lng":-71.2688,"url":"","codigo_padre":"063"},{"codigo":"08103","tipo":"comuna","nombre":"Chiguayante","lat":-36.9046,"lng":-73.0164,"url":"","codigo_padre":"081"},{"codigo":"11401","tipo":"comuna","nombre":"Chile Chico","lat":-46.5401,"lng":-71.7218,"url":"","codigo_padre":"114"},{"codigo":"08401","tipo":"comuna","nombre":"Chill\u00e1n","lat":-36.6013,"lng":-72.1093,"url":"","codigo_padre":"084"},{"codigo":"08406","tipo":"comuna","nombre":"Chill\u00e1n Viejo","lat":-36.6333,"lng":-72.1404,"url":"","codigo_padre":"084"},{"codigo":"06303","tipo":"comuna","nombre":"Chimbarongo","lat":-34.7552,"lng":-70.9753,"url":"","codigo_padre":"063"},{"codigo":"09121","tipo":"comuna","nombre":"Cholchol","lat":-38.596,"lng":-72.8445,"url":"","codigo_padre":"091"},{"codigo":"10203","tipo":"comuna","nombre":"Chonchi","lat":-42.6232,"lng":-73.7739,"url":"","codigo_padre":"102"},{"codigo":"11202","tipo":"comuna","nombre":"Cisnes","lat":-44.728,"lng":-72.6828,"url":"","codigo_padre":"112"},{"codigo":"08403","tipo":"comuna","nombre":"Cobquecura","lat":-36.1318,"lng":-72.7911,"url":"","codigo_padre":"084"},{"codigo":"10103","tipo":"comuna","nombre":"Cocham\u00f3","lat":-41.488,"lng":-72.3038,"url":"","codigo_padre":"101"},{"codigo":"11301","tipo":"comuna","nombre":"Cochrane","lat":-47.2494,"lng":-72.5784,"url":"","codigo_padre":"113"},{"codigo":"06102","tipo":"comuna","nombre":"Codegua","lat":-34.0442,"lng":-70.5131,"url":"","codigo_padre":"061"},{"codigo":"08404","tipo":"comuna","nombre":"Coelemu","lat":-36.4877,"lng":-72.7022,"url":"","codigo_padre":"084"},{"codigo":"11101","tipo":"comuna","nombre":"Coihaique","lat":-45.5758,"lng":-72.0621,"url":"","codigo_padre":"111"},{"codigo":"08405","tipo":"comuna","nombre":"Coihueco","lat":-36.6166,"lng":-71.8344,"url":"","codigo_padre":"084"},{"codigo":"06103","tipo":"comuna","nombre":"Coinco","lat":-34.2918,"lng":-70.9706,"url":"","codigo_padre":"061"},{"codigo":"07402","tipo":"comuna","nombre":"Colb\u00fan","lat":-35.6927,"lng":-71.4067,"url":"","codigo_padre":"074"},{"codigo":"01403","tipo":"comuna","nombre":"Colchane","lat":-19.2787,"lng":-68.6343,"url":"","codigo_padre":"014"},{"codigo":"13301","tipo":"comuna","nombre":"Colina","lat":-33.1996,"lng":-70.6702,"url":"","codigo_padre":"133"},{"codigo":"09202","tipo":"comuna","nombre":"Collipulli","lat":-37.9528,"lng":-72.4323,"url":"","codigo_padre":"092"},{"codigo":"06104","tipo":"comuna","nombre":"Coltauco","lat":-34.2498,"lng":-71.0791,"url":"","codigo_padre":"061"},{"codigo":"04302","tipo":"comuna","nombre":"Combarbal\u00e1","lat":-31.1764,"lng":-70.9978,"url":"","codigo_padre":"043"},{"codigo":"08101","tipo":"comuna","nombre":"Concepci\u00f3n","lat":-36.8148,"lng":-73.0293,"url":"","codigo_padre":"081"},{"codigo":"13104","tipo":"comuna","nombre":"Conchal\u00ed","lat":-33.3862,"lng":-70.6727,"url":"","codigo_padre":"131"},{"codigo":"05103","tipo":"comuna","nombre":"Conc\u00f3n","lat":-32.9305,"lng":-71.5191,"url":"","codigo_padre":"051"},{"codigo":"07102","tipo":"comuna","nombre":"Constituci\u00f3n","lat":-35.3309,"lng":-72.4139,"url":"","codigo_padre":"071"},{"codigo":"08204","tipo":"comuna","nombre":"Contulmo","lat":-38.026,"lng":-73.2581,"url":"","codigo_padre":"082"},{"codigo":"03101","tipo":"comuna","nombre":"Copiap\u00f3","lat":-27.3654,"lng":-70.3314,"url":"","codigo_padre":"031"},{"codigo":"04102","tipo":"comuna","nombre":"Coquimbo","lat":-29.968,"lng":-71.337,"url":"","codigo_padre":"041"},{"codigo":"08102","tipo":"comuna","nombre":"Coronel","lat":-37.0265,"lng":-73.1498,"url":"","codigo_padre":"081"},{"codigo":"14102","tipo":"comuna","nombre":"Corral","lat":-39.8892,"lng":-73.433,"url":"","codigo_padre":"141"},{"codigo":"09103","tipo":"comuna","nombre":"Cunco","lat":-38.9307,"lng":-72.0264,"url":"","codigo_padre":"091"},{"codigo":"09203","tipo":"comuna","nombre":"Curacaut\u00edn","lat":-38.4317,"lng":-71.8898,"url":"","codigo_padre":"092"},{"codigo":"13503","tipo":"comuna","nombre":"Curacav\u00ed","lat":-33.4063,"lng":-71.1333,"url":"","codigo_padre":"135"},{"codigo":"10204","tipo":"comuna","nombre":"Curaco de V\u00e9lez","lat":-42.4404,"lng":-73.6037,"url":"","codigo_padre":"102"},{"codigo":"08205","tipo":"comuna","nombre":"Curanilahue","lat":-37.4759,"lng":-73.353,"url":"","codigo_padre":"082"},{"codigo":"09104","tipo":"comuna","nombre":"Curarrehue","lat":-39.3592,"lng":-71.5881,"url":"","codigo_padre":"091"},{"codigo":"07103","tipo":"comuna","nombre":"Curepto","lat":-35.091,"lng":-72.0216,"url":"","codigo_padre":"071"},{"codigo":"07301","tipo":"comuna","nombre":"Curic\u00f3","lat":-34.9756,"lng":-71.2235,"url":"","codigo_padre":"073"},{"codigo":"10205","tipo":"comuna","nombre":"Dalcahue","lat":-42.3776,"lng":-73.6521,"url":"","codigo_padre":"102"},{"codigo":"03202","tipo":"comuna","nombre":"Diego de Almagro","lat":-26.3771,"lng":-70.0488,"url":"","codigo_padre":"032"},{"codigo":"06105","tipo":"comuna","nombre":"Do\u00f1ihue","lat":-34.2024,"lng":-70.9325,"url":"","codigo_padre":"061"},{"codigo":"13105","tipo":"comuna","nombre":"El Bosque","lat":-33.5638,"lng":-70.6714,"url":"","codigo_padre":"131"},{"codigo":"08407","tipo":"comuna","nombre":"El Carmen","lat":-36.8964,"lng":-72.0218,"url":"","codigo_padre":"084"},{"codigo":"13602","tipo":"comuna","nombre":"El Monte","lat":-33.6662,"lng":-71.0294,"url":"","codigo_padre":"136"},{"codigo":"05604","tipo":"comuna","nombre":"El Quisco","lat":-33.4156,"lng":-71.6556,"url":"","codigo_padre":"056"},{"codigo":"05605","tipo":"comuna","nombre":"El Tabo","lat":-33.4847,"lng":-71.5862,"url":"","codigo_padre":"056"},{"codigo":"07104","tipo":"comuna","nombre":"Empedrado","lat":-35.6213,"lng":-72.2473,"url":"","codigo_padre":"071"},{"codigo":"09204","tipo":"comuna","nombre":"Ercilla","lat":-38.0587,"lng":-72.358,"url":"","codigo_padre":"092"},{"codigo":"13106","tipo":"comuna","nombre":"Estaci\u00f3n Central","lat":-33.4503,"lng":-70.6751,"url":"","codigo_padre":"131"},{"codigo":"08104","tipo":"comuna","nombre":"Florida","lat":-36.8209,"lng":-72.6621,"url":"","codigo_padre":"081"},{"codigo":"09105","tipo":"comuna","nombre":"Freire","lat":-38.9538,"lng":-72.6219,"url":"","codigo_padre":"091"},{"codigo":"03303","tipo":"comuna","nombre":"Freirina","lat":-28.5001,"lng":-71.076,"url":"","codigo_padre":"033"},{"codigo":"10104","tipo":"comuna","nombre":"Fresia","lat":-41.1542,"lng":-73.4224,"url":"","codigo_padre":"101"},{"codigo":"10105","tipo":"comuna","nombre":"Frutillar","lat":-41.1167,"lng":-73.05,"url":"","codigo_padre":"101"},{"codigo":"10402","tipo":"comuna","nombre":"Futaleuf\u00fa","lat":-43.1859,"lng":-71.8666,"url":"","codigo_padre":"104"},{"codigo":"14202","tipo":"comuna","nombre":"Futrono","lat":-40.1243,"lng":-72.393,"url":"","codigo_padre":"142"},{"codigo":"09106","tipo":"comuna","nombre":"Galvarino","lat":-38.4085,"lng":-72.7804,"url":"","codigo_padre":"091"},{"codigo":"15202","tipo":"comuna","nombre":"General Lagos","lat":-17.8324,"lng":-69.6094,"url":"","codigo_padre":"152"},{"codigo":"09107","tipo":"comuna","nombre":"Gorbea","lat":-39.0948,"lng":-72.6722,"url":"","codigo_padre":"091"},{"codigo":"06106","tipo":"comuna","nombre":"Graneros","lat":-34.0709,"lng":-70.7501,"url":"","codigo_padre":"061"},{"codigo":"11203","tipo":"comuna","nombre":"Guaitecas","lat":-43.8781,"lng":-73.7485,"url":"","codigo_padre":"112"},{"codigo":"05503","tipo":"comuna","nombre":"Hijuelas","lat":-32.8671,"lng":-71.0929,"url":"","codigo_padre":"055"},{"codigo":"10403","tipo":"comuna","nombre":"Hualaihu\u00e9","lat":-42.0967,"lng":-72.4044,"url":"","codigo_padre":"104"},{"codigo":"07302","tipo":"comuna","nombre":"Huala\u00f1\u00e9","lat":-34.9762,"lng":-71.8043,"url":"","codigo_padre":"073"},{"codigo":"08112","tipo":"comuna","nombre":"Hualp\u00e9n","lat":-36.7827,"lng":-73.1454,"url":"","codigo_padre":"081"},{"codigo":"08105","tipo":"comuna","nombre":"Hualqui","lat":-37.0145,"lng":-72.8662,"url":"","codigo_padre":"081"},{"codigo":"01404","tipo":"comuna","nombre":"Huara","lat":-19.9963,"lng":-69.7718,"url":"","codigo_padre":"014"},{"codigo":"03304","tipo":"comuna","nombre":"Huasco","lat":-28.4518,"lng":-71.2244,"url":"","codigo_padre":"033"},{"codigo":"13107","tipo":"comuna","nombre":"Huechuraba","lat":-33.3665,"lng":-70.6315,"url":"","codigo_padre":"131"},{"codigo":"04201","tipo":"comuna","nombre":"Illapel","lat":-31.6242,"lng":-71.1626,"url":"","codigo_padre":"042"},{"codigo":"13108","tipo":"comuna","nombre":"Independencia","lat":-33.4196,"lng":-70.6627,"url":"","codigo_padre":"131"},{"codigo":"01101","tipo":"comuna","nombre":"Iquique","lat":-20.2232,"lng":-70.1463,"url":"","codigo_padre":"011"},{"codigo":"13603","tipo":"comuna","nombre":"Isla de Maipo","lat":-33.7536,"lng":-70.8862,"url":"","codigo_padre":"136"},{"codigo":"05201","tipo":"comuna","nombre":"Isla de Pascua","lat":-27.1504,"lng":-109.423,"url":"","codigo_padre":"052"},{"codigo":"05104","tipo":"comuna","nombre":"Juan Fern\u00e1ndez","lat":-33.6167,"lng":-78.8667,"url":"","codigo_padre":"051"},{"codigo":"13109","tipo":"comuna","nombre":"La Cisterna","lat":-33.538,"lng":-70.6612,"url":"","codigo_padre":"131"},{"codigo":"05504","tipo":"comuna","nombre":"La Cruz","lat":-32.8258,"lng":-71.2592,"url":"","codigo_padre":"055"},{"codigo":"06202","tipo":"comuna","nombre":"La Estrella","lat":-34.2037,"lng":-71.6073,"url":"","codigo_padre":"062"},{"codigo":"13110","tipo":"comuna","nombre":"La Florida","lat":-33.5225,"lng":-70.5952,"url":"","codigo_padre":"131"},{"codigo":"13111","tipo":"comuna","nombre":"La Granja","lat":-33.5373,"lng":-70.6188,"url":"","codigo_padre":"131"},{"codigo":"04104","tipo":"comuna","nombre":"La Higuera","lat":-29.497,"lng":-71.2656,"url":"","codigo_padre":"041"},{"codigo":"05401","tipo":"comuna","nombre":"La Ligua","lat":-32.449,"lng":-71.2309,"url":"","codigo_padre":"054"},{"codigo":"13112","tipo":"comuna","nombre":"La Pintana","lat":-33.5902,"lng":-70.6322,"url":"","codigo_padre":"131"},{"codigo":"13113","tipo":"comuna","nombre":"La Reina","lat":-33.4565,"lng":-70.5349,"url":"","codigo_padre":"131"},{"codigo":"04101","tipo":"comuna","nombre":"La Serena","lat":-29.8966,"lng":-71.2422,"url":"","codigo_padre":"041"},{"codigo":"14201","tipo":"comuna","nombre":"La Uni\u00f3n","lat":-40.2951,"lng":-73.0829,"url":"","codigo_padre":"142"},{"codigo":"14203","tipo":"comuna","nombre":"Lago Ranco","lat":-40.312,"lng":-72.5002,"url":"","codigo_padre":"142"},{"codigo":"11102","tipo":"comuna","nombre":"Lago Verde","lat":-44.2236,"lng":-71.8396,"url":"","codigo_padre":"111"},{"codigo":"12102","tipo":"comuna","nombre":"Laguna Blanca","lat":-52.3001,"lng":-71.1612,"url":"","codigo_padre":"121"},{"codigo":"08304","tipo":"comuna","nombre":"Laja","lat":-37.2768,"lng":-72.7171,"url":"","codigo_padre":"083"},{"codigo":"13302","tipo":"comuna","nombre":"Lampa","lat":-33.2863,"lng":-70.8789,"url":"","codigo_padre":"133"},{"codigo":"14103","tipo":"comuna","nombre":"Lanco","lat":-39.4522,"lng":-72.7747,"url":"","codigo_padre":"141"},{"codigo":"06107","tipo":"comuna","nombre":"Las Cabras","lat":-34.2945,"lng":-71.3066,"url":"","codigo_padre":"061"},{"codigo":"13114","tipo":"comuna","nombre":"Las Condes","lat":-33.4154,"lng":-70.5837,"url":"","codigo_padre":"131"},{"codigo":"09108","tipo":"comuna","nombre":"Lautaro","lat":-38.5286,"lng":-72.427,"url":"","codigo_padre":"091"},{"codigo":"08201","tipo":"comuna","nombre":"Lebu","lat":-37.6079,"lng":-73.6508,"url":"","codigo_padre":"082"},{"codigo":"07303","tipo":"comuna","nombre":"Licant\u00e9n","lat":-34.9591,"lng":-72.0269,"url":"","codigo_padre":"073"},{"codigo":"05802","tipo":"comuna","nombre":"Limache","lat":-33.0035,"lng":-71.2613,"url":"","codigo_padre":"058"},{"codigo":"07401","tipo":"comuna","nombre":"Linares","lat":-35.8495,"lng":-71.585,"url":"","codigo_padre":"074"},{"codigo":"06203","tipo":"comuna","nombre":"Litueche","lat":-34.1069,"lng":-71.7204,"url":"","codigo_padre":"062"},{"codigo":"05703","tipo":"comuna","nombre":"Llaillay","lat":-32.8899,"lng":-70.8942,"url":"","codigo_padre":"057"},{"codigo":"10107","tipo":"comuna","nombre":"Llanquihue","lat":-41.2574,"lng":-73.0054,"url":"","codigo_padre":"101"},{"codigo":"13115","tipo":"comuna","nombre":"Lo Barnechea","lat":-33.2993,"lng":-70.3748,"url":"","codigo_padre":"131"},{"codigo":"13116","tipo":"comuna","nombre":"Lo Espejo","lat":-33.5247,"lng":-70.6916,"url":"","codigo_padre":"131"},{"codigo":"13117","tipo":"comuna","nombre":"Lo Prado","lat":-33.4489,"lng":-70.721,"url":"","codigo_padre":"131"},{"codigo":"06304","tipo":"comuna","nombre":"Lolol","lat":-34.7689,"lng":-71.6453,"url":"","codigo_padre":"063"},{"codigo":"09109","tipo":"comuna","nombre":"Loncoche","lat":-39.3681,"lng":-72.6315,"url":"","codigo_padre":"091"},{"codigo":"07403","tipo":"comuna","nombre":"Longav\u00ed","lat":-35.9657,"lng":-71.6816,"url":"","codigo_padre":"074"},{"codigo":"09205","tipo":"comuna","nombre":"Lonquimay","lat":-38.4501,"lng":-71.374,"url":"","codigo_padre":"092"},{"codigo":"08206","tipo":"comuna","nombre":"Los \u00c1lamos","lat":-37.6747,"lng":-73.3896,"url":"","codigo_padre":"082"},{"codigo":"05301","tipo":"comuna","nombre":"Los Andes","lat":-32.8347,"lng":-70.5971,"url":"","codigo_padre":"053"},{"codigo":"08301","tipo":"comuna","nombre":"Los \u00c1ngeles","lat":-37.473,"lng":-72.3507,"url":"","codigo_padre":"083"},{"codigo":"14104","tipo":"comuna","nombre":"Los Lagos","lat":-39.8636,"lng":-72.8124,"url":"","codigo_padre":"141"},{"codigo":"10106","tipo":"comuna","nombre":"Los Muermos","lat":-41.3997,"lng":-73.4651,"url":"","codigo_padre":"101"},{"codigo":"09206","tipo":"comuna","nombre":"Los Sauces","lat":-37.9754,"lng":-72.8288,"url":"","codigo_padre":"092"},{"codigo":"04203","tipo":"comuna","nombre":"Los Vilos","lat":-31.9157,"lng":-71.5107,"url":"","codigo_padre":"042"},{"codigo":"08106","tipo":"comuna","nombre":"Lota","lat":-37.0906,"lng":-73.1547,"url":"","codigo_padre":"081"},{"codigo":"09207","tipo":"comuna","nombre":"Lumaco","lat":-38.1636,"lng":-72.8918,"url":"","codigo_padre":"092"},{"codigo":"06108","tipo":"comuna","nombre":"Machal\u00ed","lat":-34.2938,"lng":-70.3371,"url":"","codigo_padre":"061"},{"codigo":"13118","tipo":"comuna","nombre":"Macul","lat":-33.492,"lng":-70.5968,"url":"","codigo_padre":"131"},{"codigo":"14105","tipo":"comuna","nombre":"M\u00e1fil","lat":-39.6654,"lng":-72.9575,"url":"","codigo_padre":"141"},{"codigo":"13119","tipo":"comuna","nombre":"Maip\u00fa","lat":-33.5213,"lng":-70.7572,"url":"","codigo_padre":"131"},{"codigo":"06109","tipo":"comuna","nombre":"Malloa","lat":-34.4455,"lng":-70.9449,"url":"","codigo_padre":"061"},{"codigo":"06204","tipo":"comuna","nombre":"Marchihue","lat":-34.3979,"lng":-71.6144,"url":"","codigo_padre":"062"},{"codigo":"02302","tipo":"comuna","nombre":"Mar\u00eda Elena","lat":-22.1639,"lng":-69.4171,"url":"","codigo_padre":"023"},{"codigo":"13504","tipo":"comuna","nombre":"Mar\u00eda Pinto","lat":-33.5154,"lng":-71.1191,"url":"","codigo_padre":"135"},{"codigo":"14106","tipo":"comuna","nombre":"Mariquina","lat":-39.5399,"lng":-72.9621,"url":"","codigo_padre":"141"},{"codigo":"07105","tipo":"comuna","nombre":"Maule","lat":-35.5057,"lng":-71.7069,"url":"","codigo_padre":"071"},{"codigo":"10108","tipo":"comuna","nombre":"Maull\u00edn","lat":-41.6172,"lng":-73.5956,"url":"","codigo_padre":"101"},{"codigo":"02102","tipo":"comuna","nombre":"Mejillones","lat":-23.0962,"lng":-70.4498,"url":"","codigo_padre":"021"},{"codigo":"09110","tipo":"comuna","nombre":"Melipeuco","lat":-38.8429,"lng":-71.6871,"url":"","codigo_padre":"091"},{"codigo":"13501","tipo":"comuna","nombre":"Melipilla","lat":-33.6866,"lng":-71.2139,"url":"","codigo_padre":"135"},{"codigo":"07304","tipo":"comuna","nombre":"Molina","lat":-35.0896,"lng":-71.2788,"url":"","codigo_padre":"073"},{"codigo":"04303","tipo":"comuna","nombre":"Monte Patria","lat":-30.8291,"lng":-70.6984,"url":"","codigo_padre":"043"},{"codigo":"06110","tipo":"comuna","nombre":"Mostazal","lat":-33.9772,"lng":-70.7092,"url":"","codigo_padre":"061"},{"codigo":"08305","tipo":"comuna","nombre":"Mulch\u00e9n","lat":-37.7147,"lng":-72.2394,"url":"","codigo_padre":"083"},{"codigo":"08306","tipo":"comuna","nombre":"Nacimiento","lat":-37.5011,"lng":-72.6763,"url":"","codigo_padre":"083"},{"codigo":"06305","tipo":"comuna","nombre":"Nancagua","lat":-34.6615,"lng":-71.1749,"url":"","codigo_padre":"063"},{"codigo":"12401","tipo":"comuna","nombre":"Natales","lat":-51.7219,"lng":-72.5208,"url":"","codigo_padre":"124"},{"codigo":"06205","tipo":"comuna","nombre":"Navidad","lat":-34.0068,"lng":-71.8101,"url":"","codigo_padre":"062"},{"codigo":"08307","tipo":"comuna","nombre":"Negrete","lat":-37.5974,"lng":-72.5646,"url":"","codigo_padre":"083"},{"codigo":"08408","tipo":"comuna","nombre":"Ninhue","lat":-36.4011,"lng":-72.397,"url":"","codigo_padre":"084"},{"codigo":"08409","tipo":"comuna","nombre":"\u00d1iqu\u00e9n","lat":-36.2848,"lng":-71.8994,"url":"","codigo_padre":"084"},{"codigo":"05506","tipo":"comuna","nombre":"Nogales","lat":-32.6923,"lng":-71.1894,"url":"","codigo_padre":"055"},{"codigo":"09111","tipo":"comuna","nombre":"Nueva Imperial","lat":-38.7445,"lng":-72.9482,"url":"","codigo_padre":"091"},{"codigo":"13120","tipo":"comuna","nombre":"\u00d1u\u00f1oa","lat":-33.4607,"lng":-70.5927,"url":"","codigo_padre":"131"},{"codigo":"06111","tipo":"comuna","nombre":"Olivar","lat":-34.2186,"lng":-70.8355,"url":"","codigo_padre":"061"},{"codigo":"02202","tipo":"comuna","nombre":"Ollag\u00fce","lat":-21.2238,"lng":-68.2529,"url":"","codigo_padre":"022"},{"codigo":"05803","tipo":"comuna","nombre":"Olmu\u00e9","lat":-33.0132,"lng":-71.1525,"url":"","codigo_padre":"058"},{"codigo":"10301","tipo":"comuna","nombre":"Osorno","lat":-40.5747,"lng":-73.1319,"url":"","codigo_padre":"103"},{"codigo":"04301","tipo":"comuna","nombre":"Ovalle","lat":-30.5942,"lng":-71.1983,"url":"","codigo_padre":"043"},{"codigo":"11302","tipo":"comuna","nombre":"O\u2019Higgins","lat":-48.4643,"lng":-72.5613,"url":"","codigo_padre":"113"},{"codigo":"13604","tipo":"comuna","nombre":"Padre Hurtado","lat":-33.5761,"lng":-70.8003,"url":"","codigo_padre":"136"},{"codigo":"09112","tipo":"comuna","nombre":"Padre las Casas","lat":-38.7658,"lng":-72.5929,"url":"","codigo_padre":"091"},{"codigo":"04105","tipo":"comuna","nombre":"Paiguano","lat":-30.2496,"lng":-70.3832,"url":"","codigo_padre":"041"},{"codigo":"14107","tipo":"comuna","nombre":"Paillaco","lat":-40.0707,"lng":-72.8708,"url":"","codigo_padre":"141"},{"codigo":"13404","tipo":"comuna","nombre":"Paine","lat":-33.8673,"lng":-70.7303,"url":"","codigo_padre":"134"},{"codigo":"10404","tipo":"comuna","nombre":"Palena","lat":-43.6162,"lng":-71.8176,"url":"","codigo_padre":"104"},{"codigo":"06306","tipo":"comuna","nombre":"Palmilla","lat":-34.6042,"lng":-71.3583,"url":"","codigo_padre":"063"},{"codigo":"14108","tipo":"comuna","nombre":"Panguipulli","lat":-39.6436,"lng":-72.3365,"url":"","codigo_padre":"141"},{"codigo":"05704","tipo":"comuna","nombre":"Panquehue","lat":-32.8079,"lng":-70.8428,"url":"","codigo_padre":"057"},{"codigo":"05403","tipo":"comuna","nombre":"Papudo","lat":-32.4699,"lng":-71.3842,"url":"","codigo_padre":"054"},{"codigo":"06206","tipo":"comuna","nombre":"Paredones","lat":-34.6972,"lng":-71.8978,"url":"","codigo_padre":"062"},{"codigo":"07404","tipo":"comuna","nombre":"Parral","lat":-36.14,"lng":-71.8244,"url":"","codigo_padre":"074"},{"codigo":"13121","tipo":"comuna","nombre":"Pedro Aguirre Cerda","lat":-33.4891,"lng":-70.6729,"url":"","codigo_padre":"131"},{"codigo":"07106","tipo":"comuna","nombre":"Pelarco","lat":-35.3723,"lng":-71.3278,"url":"","codigo_padre":"071"},{"codigo":"07203","tipo":"comuna","nombre":"Pelluhue","lat":-35.8145,"lng":-72.5736,"url":"","codigo_padre":"072"},{"codigo":"08410","tipo":"comuna","nombre":"Pemuco","lat":-36.9865,"lng":-72.0191,"url":"","codigo_padre":"084"},{"codigo":"13605","tipo":"comuna","nombre":"Pe\u00f1aflor","lat":-33.6141,"lng":-70.8876,"url":"","codigo_padre":"136"},{"codigo":"13122","tipo":"comuna","nombre":"Pe\u00f1alol\u00e9n","lat":-33.4904,"lng":-70.5105,"url":"","codigo_padre":"131"},{"codigo":"07107","tipo":"comuna","nombre":"Pencahue","lat":-35.3051,"lng":-71.8284,"url":"","codigo_padre":"071"},{"codigo":"08107","tipo":"comuna","nombre":"Penco","lat":-36.7423,"lng":-72.998,"url":"","codigo_padre":"081"},{"codigo":"06307","tipo":"comuna","nombre":"Peralillo","lat":-34.4593,"lng":-71.5,"url":"","codigo_padre":"063"},{"codigo":"09113","tipo":"comuna","nombre":"Perquenco","lat":-38.4154,"lng":-72.3725,"url":"","codigo_padre":"091"},{"codigo":"05404","tipo":"comuna","nombre":"Petorca","lat":-32.1965,"lng":-70.8318,"url":"","codigo_padre":"054"},{"codigo":"06112","tipo":"comuna","nombre":"Peumo","lat":-34.3798,"lng":-71.1687,"url":"","codigo_padre":"061"},{"codigo":"01405","tipo":"comuna","nombre":"Pica","lat":-20.4889,"lng":-69.3289,"url":"","codigo_padre":"014"},{"codigo":"06113","tipo":"comuna","nombre":"Pichidegua","lat":-34.3758,"lng":-71.3469,"url":"","codigo_padre":"061"},{"codigo":"06201","tipo":"comuna","nombre":"Pichilemu","lat":-34.3869,"lng":-72.0032,"url":"","codigo_padre":"062"},{"codigo":"08411","tipo":"comuna","nombre":"Pinto","lat":-36.6978,"lng":-71.8934,"url":"","codigo_padre":"084"},{"codigo":"13202","tipo":"comuna","nombre":"Pirque","lat":-33.7384,"lng":-70.4914,"url":"","codigo_padre":"132"},{"codigo":"09114","tipo":"comuna","nombre":"Pitrufqu\u00e9n","lat":-38.9829,"lng":-72.6429,"url":"","codigo_padre":"091"},{"codigo":"06308","tipo":"comuna","nombre":"Placilla","lat":-34.6135,"lng":-71.0951,"url":"","codigo_padre":"063"},{"codigo":"08412","tipo":"comuna","nombre":"Portezuelo","lat":-36.529,"lng":-72.433,"url":"","codigo_padre":"084"},{"codigo":"12301","tipo":"comuna","nombre":"Porvenir","lat":-53.2898,"lng":-70.3633,"url":"","codigo_padre":"123"},{"codigo":"01401","tipo":"comuna","nombre":"Pozo Almonte","lat":-20.2532,"lng":-69.7848,"url":"","codigo_padre":"014"},{"codigo":"12302","tipo":"comuna","nombre":"Primavera","lat":-52.7122,"lng":-69.2496,"url":"","codigo_padre":"123"},{"codigo":"13123","tipo":"comuna","nombre":"Providencia","lat":-33.4214,"lng":-70.6033,"url":"","codigo_padre":"131"},{"codigo":"05105","tipo":"comuna","nombre":"Puchuncav\u00ed","lat":-32.7499,"lng":-71.396,"url":"","codigo_padre":"051"},{"codigo":"09115","tipo":"comuna","nombre":"Puc\u00f3n","lat":-39.2824,"lng":-71.9545,"url":"","codigo_padre":"091"},{"codigo":"13124","tipo":"comuna","nombre":"Pudahuel","lat":-33.4184,"lng":-70.8324,"url":"","codigo_padre":"131"},{"codigo":"13201","tipo":"comuna","nombre":"Puente Alto","lat":-33.6079,"lng":-70.5778,"url":"","codigo_padre":"132"},{"codigo":"10101","tipo":"comuna","nombre":"Puerto Montt","lat":-41.4633,"lng":-72.9314,"url":"","codigo_padre":"101"},{"codigo":"10302","tipo":"comuna","nombre":"Puerto Octay","lat":-40.9755,"lng":-72.8833,"url":"","codigo_padre":"103"},{"codigo":"10109","tipo":"comuna","nombre":"Puerto Varas","lat":-41.316,"lng":-72.9836,"url":"","codigo_padre":"101"},{"codigo":"06309","tipo":"comuna","nombre":"Pumanque","lat":-34.6052,"lng":-71.6443,"url":"","codigo_padre":"063"},{"codigo":"04304","tipo":"comuna","nombre":"Punitaqui","lat":-30.8256,"lng":-71.2585,"url":"","codigo_padre":"043"},{"codigo":"12101","tipo":"comuna","nombre":"Punta Arenas","lat":-53.1641,"lng":-70.9305,"url":"","codigo_padre":"121"},{"codigo":"10206","tipo":"comuna","nombre":"Puqueld\u00f3n","lat":-42.6015,"lng":-73.6714,"url":"","codigo_padre":"102"},{"codigo":"09208","tipo":"comuna","nombre":"Pur\u00e9n","lat":-38.0326,"lng":-73.0728,"url":"","codigo_padre":"092"},{"codigo":"10303","tipo":"comuna","nombre":"Purranque","lat":-40.9085,"lng":-73.1653,"url":"","codigo_padre":"103"},{"codigo":"05705","tipo":"comuna","nombre":"Putaendo","lat":-32.6279,"lng":-70.7165,"url":"","codigo_padre":"057"},{"codigo":"15201","tipo":"comuna","nombre":"Putre","lat":-18.1798,"lng":-69.5544,"url":"","codigo_padre":"152"},{"codigo":"10304","tipo":"comuna","nombre":"Puyehue","lat":-40.6806,"lng":-72.599,"url":"","codigo_padre":"103"},{"codigo":"10207","tipo":"comuna","nombre":"Queil\u00e9n","lat":-42.9001,"lng":-73.4827,"url":"","codigo_padre":"102"},{"codigo":"10208","tipo":"comuna","nombre":"Quell\u00f3n","lat":-43.1156,"lng":-73.6172,"url":"","codigo_padre":"102"},{"codigo":"10209","tipo":"comuna","nombre":"Quemchi","lat":-42.1426,"lng":-73.475,"url":"","codigo_padre":"102"},{"codigo":"08308","tipo":"comuna","nombre":"Quilaco","lat":-37.6799,"lng":-72.0074,"url":"","codigo_padre":"083"},{"codigo":"13125","tipo":"comuna","nombre":"Quilicura","lat":-33.3551,"lng":-70.7278,"url":"","codigo_padre":"131"},{"codigo":"08309","tipo":"comuna","nombre":"Quilleco","lat":-37.4335,"lng":-71.8761,"url":"","codigo_padre":"083"},{"codigo":"08413","tipo":"comuna","nombre":"Quill\u00f3n","lat":-36.7383,"lng":-72.469,"url":"","codigo_padre":"084"},{"codigo":"05501","tipo":"comuna","nombre":"Quillota","lat":-32.8793,"lng":-71.2508,"url":"","codigo_padre":"055"},{"codigo":"05801","tipo":"comuna","nombre":"Quilpu\u00e9","lat":-33.0492,"lng":-71.4435,"url":"","codigo_padre":"058"},{"codigo":"10210","tipo":"comuna","nombre":"Quinchao","lat":-42.472,"lng":-73.4898,"url":"","codigo_padre":"102"},{"codigo":"06114","tipo":"comuna","nombre":"Quinta de Tilcoco","lat":-34.367,"lng":-71.0096,"url":"","codigo_padre":"061"},{"codigo":"13126","tipo":"comuna","nombre":"Quinta Normal","lat":-33.428,"lng":-70.6964,"url":"","codigo_padre":"131"},{"codigo":"05107","tipo":"comuna","nombre":"Quintero","lat":-32.7872,"lng":-71.5274,"url":"","codigo_padre":"051"},{"codigo":"08414","tipo":"comuna","nombre":"Quirihue","lat":-36.2839,"lng":-72.5414,"url":"","codigo_padre":"084"},{"codigo":"06101","tipo":"comuna","nombre":"Rancagua","lat":-34.162,"lng":-70.741,"url":"","codigo_padre":"061"},{"codigo":"08415","tipo":"comuna","nombre":"R\u00e1nquil","lat":-36.6485,"lng":-72.6064,"url":"","codigo_padre":"084"},{"codigo":"07305","tipo":"comuna","nombre":"Rauco","lat":-34.9295,"lng":-71.3111,"url":"","codigo_padre":"073"},{"codigo":"13127","tipo":"comuna","nombre":"Recoleta","lat":-33.4173,"lng":-70.6303,"url":"","codigo_padre":"131"},{"codigo":"09209","tipo":"comuna","nombre":"Renaico","lat":-37.6654,"lng":-72.5687,"url":"","codigo_padre":"092"},{"codigo":"13128","tipo":"comuna","nombre":"Renca","lat":-33.4141,"lng":-70.7129,"url":"","codigo_padre":"131"},{"codigo":"06115","tipo":"comuna","nombre":"Rengo","lat":-34.4017,"lng":-70.8561,"url":"","codigo_padre":"061"},{"codigo":"06116","tipo":"comuna","nombre":"Requ\u00ednoa","lat":-34.3533,"lng":-70.6797,"url":"","codigo_padre":"061"},{"codigo":"07405","tipo":"comuna","nombre":"Retiro","lat":-36.0458,"lng":-71.7591,"url":"","codigo_padre":"074"},{"codigo":"05303","tipo":"comuna","nombre":"Rinconada","lat":-32.8765,"lng":-70.7085,"url":"","codigo_padre":"053"},{"codigo":"14204","tipo":"comuna","nombre":"R\u00edo Bueno","lat":-40.333,"lng":-72.9513,"url":"","codigo_padre":"142"},{"codigo":"07108","tipo":"comuna","nombre":"R\u00edo Claro","lat":-35.2827,"lng":-71.2665,"url":"","codigo_padre":"071"},{"codigo":"04305","tipo":"comuna","nombre":"R\u00edo Hurtado","lat":-30.2603,"lng":-70.6668,"url":"","codigo_padre":"043"},{"codigo":"11402","tipo":"comuna","nombre":"R\u00edo Ib\u00e1\u00f1ez","lat":-46.2938,"lng":-71.9357,"url":"","codigo_padre":"114"},{"codigo":"10305","tipo":"comuna","nombre":"R\u00edo Negro","lat":-40.7829,"lng":-73.2319,"url":"","codigo_padre":"103"},{"codigo":"12103","tipo":"comuna","nombre":"R\u00edo Verde","lat":-52.5814,"lng":-71.5128,"url":"","codigo_padre":"121"},{"codigo":"07306","tipo":"comuna","nombre":"Romeral","lat":-34.9634,"lng":-71.1205,"url":"","codigo_padre":"073"},{"codigo":"09116","tipo":"comuna","nombre":"Saavedra","lat":-38.7803,"lng":-73.3897,"url":"","codigo_padre":"091"},{"codigo":"07307","tipo":"comuna","nombre":"Sagrada Familia","lat":-34.9949,"lng":-71.3798,"url":"","codigo_padre":"073"},{"codigo":"04204","tipo":"comuna","nombre":"Salamanca","lat":-31.7737,"lng":-70.9717,"url":"","codigo_padre":"042"},{"codigo":"05601","tipo":"comuna","nombre":"San Antonio","lat":-33.5812,"lng":-71.613,"url":"","codigo_padre":"056"},{"codigo":"13401","tipo":"comuna","nombre":"San Bernardo","lat":-33.5913,"lng":-70.702,"url":"","codigo_padre":"134"},{"codigo":"08416","tipo":"comuna","nombre":"San Carlos","lat":-36.4221,"lng":-71.9594,"url":"","codigo_padre":"084"},{"codigo":"07109","tipo":"comuna","nombre":"San Clemente","lat":-35.534,"lng":-71.4865,"url":"","codigo_padre":"071"},{"codigo":"05304","tipo":"comuna","nombre":"San Esteban","lat":-32.693,"lng":-70.3703,"url":"","codigo_padre":"053"},{"codigo":"08417","tipo":"comuna","nombre":"San Fabi\u00e1n","lat":-36.5538,"lng":-71.5487,"url":"","codigo_padre":"084"},{"codigo":"05701","tipo":"comuna","nombre":"San Felipe","lat":-32.7464,"lng":-70.7489,"url":"","codigo_padre":"057"},{"codigo":"06301","tipo":"comuna","nombre":"San Fernando","lat":-34.584,"lng":-70.9874,"url":"","codigo_padre":"063"},{"codigo":"12104","tipo":"comuna","nombre":"San Gregorio","lat":-52.3135,"lng":-69.6842,"url":"","codigo_padre":"121"},{"codigo":"08418","tipo":"comuna","nombre":"San Ignacio","lat":-36.8186,"lng":-71.9883,"url":"","codigo_padre":"084"},{"codigo":"07406","tipo":"comuna","nombre":"San Javier","lat":-35.6035,"lng":-71.7362,"url":"","codigo_padre":"074"},{"codigo":"13129","tipo":"comuna","nombre":"San Joaqu\u00edn","lat":-33.4961,"lng":-70.6245,"url":"","codigo_padre":"131"},{"codigo":"13203","tipo":"comuna","nombre":"San Jos\u00e9 de Maipo","lat":-33.6921,"lng":-70.1325,"url":"","codigo_padre":"132"},{"codigo":"10306","tipo":"comuna","nombre":"San Juan de la Costa","lat":-40.5156,"lng":-73.3997,"url":"","codigo_padre":"103"},{"codigo":"13130","tipo":"comuna","nombre":"San Miguel","lat":-33.5017,"lng":-70.6489,"url":"","codigo_padre":"131"},{"codigo":"08419","tipo":"comuna","nombre":"San Nicol\u00e1s","lat":-36.4996,"lng":-72.2126,"url":"","codigo_padre":"084"},{"codigo":"10307","tipo":"comuna","nombre":"San Pablo","lat":-40.4118,"lng":-73.0102,"url":"","codigo_padre":"103"},{"codigo":"13505","tipo":"comuna","nombre":"San Pedro","lat":-33.8779,"lng":-71.4609,"url":"","codigo_padre":"135"},{"codigo":"02203","tipo":"comuna","nombre":"San Pedro de Atacama","lat":-22.9157,"lng":-68.2004,"url":"","codigo_padre":"022"},{"codigo":"08108","tipo":"comuna","nombre":"San Pedro de la Paz","lat":-36.8635,"lng":-73.1085,"url":"","codigo_padre":"081"},{"codigo":"07110","tipo":"comuna","nombre":"San Rafael","lat":-35.2942,"lng":-71.5254,"url":"","codigo_padre":"071"},{"codigo":"13131","tipo":"comuna","nombre":"San Ram\u00f3n","lat":-33.5349,"lng":-70.6392,"url":"","codigo_padre":"131"},{"codigo":"08310","tipo":"comuna","nombre":"San Rosendo","lat":-37.2021,"lng":-72.748,"url":"","codigo_padre":"083"},{"codigo":"06117","tipo":"comuna","nombre":"San Vicente","lat":-34.4381,"lng":-71.0792,"url":"","codigo_padre":"061"},{"codigo":"08311","tipo":"comuna","nombre":"Santa B\u00e1rbara","lat":-37.6627,"lng":-72.0184,"url":"","codigo_padre":"083"},{"codigo":"06310","tipo":"comuna","nombre":"Santa Cruz","lat":-34.6383,"lng":-71.367,"url":"","codigo_padre":"063"},{"codigo":"08109","tipo":"comuna","nombre":"Santa Juana","lat":-37.1726,"lng":-72.9352,"url":"","codigo_padre":"081"},{"codigo":"05706","tipo":"comuna","nombre":"Santa Mar\u00eda","lat":-32.7446,"lng":-70.654,"url":"","codigo_padre":"057"},{"codigo":"13101","tipo":"comuna","nombre":"Santiago Centro","lat":-33.4417,"lng":-70.6541,"url":"","codigo_padre":"131"},{"codigo":"05606","tipo":"comuna","nombre":"Santo Domingo","lat":-33.7076,"lng":-71.6301,"url":"","codigo_padre":"056"},{"codigo":"02103","tipo":"comuna","nombre":"Sierra Gorda","lat":-22.8921,"lng":-69.3203,"url":"","codigo_padre":"021"},{"codigo":"13601","tipo":"comuna","nombre":"Talagante","lat":-33.6643,"lng":-70.9296,"url":"","codigo_padre":"136"},{"codigo":"07101","tipo":"comuna","nombre":"Talca","lat":-35.4288,"lng":-71.6607,"url":"","codigo_padre":"071"},{"codigo":"08110","tipo":"comuna","nombre":"Talcahuano","lat":-36.7364,"lng":-73.1047,"url":"","codigo_padre":"081"},{"codigo":"02104","tipo":"comuna","nombre":"Taltal","lat":-25.4054,"lng":-70.4826,"url":"","codigo_padre":"021"},{"codigo":"09101","tipo":"comuna","nombre":"Temuco","lat":-38.7362,"lng":-72.5989,"url":"","codigo_padre":"091"},{"codigo":"07308","tipo":"comuna","nombre":"Teno","lat":-34.8701,"lng":-71.0895,"url":"","codigo_padre":"073"},{"codigo":"09117","tipo":"comuna","nombre":"Teodoro Schmidt","lat":-38.9989,"lng":-73.093,"url":"","codigo_padre":"091"},{"codigo":"03103","tipo":"comuna","nombre":"Tierra Amarilla","lat":-27.4877,"lng":-70.2696,"url":"","codigo_padre":"031"},{"codigo":"13303","tipo":"comuna","nombre":"Tiltil","lat":-33.0655,"lng":-70.8465,"url":"","codigo_padre":"133"},{"codigo":"12303","tipo":"comuna","nombre":"Timaukel","lat":-54.2877,"lng":-69.1644,"url":"","codigo_padre":"123"},{"codigo":"08207","tipo":"comuna","nombre":"Tir\u00faa","lat":-38.3315,"lng":-73.3794,"url":"","codigo_padre":"082"},{"codigo":"02301","tipo":"comuna","nombre":"Tocopilla","lat":-22.0858,"lng":-70.193,"url":"","codigo_padre":"023"},{"codigo":"09118","tipo":"comuna","nombre":"Tolt\u00e9n","lat":-39.2022,"lng":-73.2004,"url":"","codigo_padre":"091"},{"codigo":"08111","tipo":"comuna","nombre":"Tom\u00e9","lat":-36.6177,"lng":-72.9579,"url":"","codigo_padre":"081"},{"codigo":"12402","tipo":"comuna","nombre":"Torres del Paine","lat":-50.9896,"lng":-73.0893,"url":"","codigo_padre":"124"},{"codigo":"11303","tipo":"comuna","nombre":"Tortel","lat":-47.8242,"lng":-73.5645,"url":"","codigo_padre":"113"},{"codigo":"09210","tipo":"comuna","nombre":"Traigu\u00e9n","lat":-38.2509,"lng":-72.6647,"url":"","codigo_padre":"092"},{"codigo":"08420","tipo":"comuna","nombre":"Treguaco","lat":-36.4095,"lng":-72.6603,"url":"","codigo_padre":"084"},{"codigo":"08312","tipo":"comuna","nombre":"Tucapel","lat":-37.2901,"lng":-71.9491,"url":"","codigo_padre":"083"},{"codigo":"14101","tipo":"comuna","nombre":"Valdivia","lat":-39.8201,"lng":-73.2457,"url":"","codigo_padre":"141"},{"codigo":"03301","tipo":"comuna","nombre":"Vallenar","lat":-28.5777,"lng":-70.7566,"url":"","codigo_padre":"033"},{"codigo":"05101","tipo":"comuna","nombre":"Valpara\u00edso","lat":-33.0436,"lng":-71.6231,"url":"","codigo_padre":"051"},{"codigo":"07309","tipo":"comuna","nombre":"Vichuqu\u00e9n","lat":-34.8594,"lng":-72.0074,"url":"","codigo_padre":"073"},{"codigo":"09211","tipo":"comuna","nombre":"Victoria","lat":-38.2336,"lng":-72.3329,"url":"","codigo_padre":"092"},{"codigo":"04106","tipo":"comuna","nombre":"Vicu\u00f1a","lat":-30.0287,"lng":-70.7108,"url":"","codigo_padre":"041"},{"codigo":"09119","tipo":"comuna","nombre":"Vilc\u00fan","lat":-38.6701,"lng":-72.2238,"url":"","codigo_padre":"091"},{"codigo":"07407","tipo":"comuna","nombre":"Villa Alegre","lat":-35.6868,"lng":-71.6704,"url":"","codigo_padre":"074"},{"codigo":"05804","tipo":"comuna","nombre":"Villa Alemana","lat":-33.0429,"lng":-71.3724,"url":"","codigo_padre":"058"},{"codigo":"09120","tipo":"comuna","nombre":"Villarrica","lat":-39.2803,"lng":-72.2182,"url":"","codigo_padre":"091"},{"codigo":"05109","tipo":"comuna","nombre":"Vi\u00f1a del Mar","lat":-33.0445,"lng":-71.5224,"url":"","codigo_padre":"051"},{"codigo":"13132","tipo":"comuna","nombre":"Vitacura","lat":-33.3863,"lng":-70.5698,"url":"","codigo_padre":"131"},{"codigo":"07408","tipo":"comuna","nombre":"Yerbas Buenas","lat":-35.6882,"lng":-71.5636,"url":"","codigo_padre":"074"},{"codigo":"08313","tipo":"comuna","nombre":"Yumbel","lat":-37.0964,"lng":-72.5562,"url":"","codigo_padre":"083"},{"codigo":"08421","tipo":"comuna","nombre":"Yungay","lat":-37.122,"lng":-72.0132,"url":"","codigo_padre":"084"},{"codigo":"05405","tipo":"comuna","nombre":"Zapallar","lat":-32.5933,"lng":-71.3686,"url":"","codigo_padre":"054"}]
    for comuna in comunas:
        aux_comuna = comuna["nombre"].decode("raw_unicode_escape")
        aux_comuna = aux_comuna
        # aux_comuna = unidecode.unidecode(aux_comuna)
        if aux_comuna in texto:
            return aux_comuna, get_provincia(comuna["codigo_padre"], texto)
            #return aux_comuna, comuna["codigo_padre"]
    return [] 

def get_juzgado(texto):
    juzgados={
        "1o Juzgado de Letras de Arica":"01 Arica",                 
        "1o Juzgado De Letras de Arica":"01 Arica",
        "2o Juzgado de Letras de Arica":"02 Arica",
        "2o Juzgado De Letras de Arica":"02 Arica",
        "3o Juzgado de Letras de Arica":"03 Arica",
        "3o Juzgado de Letras de Arica":"03 Arica",
        "Juzgado de Letras y Gar.Pozo Almonte":"Pozo Almonte",
        "1o Juzgado de Letras de Iquique":"01 Iquique",
        "2o Juzgado de Letras de Iquique":"02 Iquique",
        "3o Juzgado de Letras de Iquique":"03 Iquique",
        "Juzgado de Letras Tocopilla":"Tocopilla",
        "Juzgado de Letras y Gar.de Maria Elena":"Maria Elena",
        "1o Juzgado de Letras de Calama":"01 Calama",
        "2o Juzgado de Letras de Calama":"02 Calama",
        "3o Juzgado de Letras de Calama":"03 Calama",
        "Juzgado de Letras y Gar. de Taltal":"Taltal",
        "1o Juzgado de Letras Civil de Antofagasta":"01 Antofagasta",
        "2o Juzgado de Letras Civil de Antofagasta":"02 Antofagasta",
        "3o Juzgado de Letras Civil de Antofagasta":"03 Antofagasta",
        "4o Juzgado de Letras Civil de Antofagasta":"04 Antofagasta",
        "Juzgado de Letras y Garantia Mejillones":"Mejillones",
        "Juzgado de Letras y Gar. de Chanaral":"Chanaral",
        "Juzgado de Letras de Diego de Almagro":"Diego de Almagro",
        "1o Juzgado de Letras de Copiapo":"01 Copiapo",
        "2o Juzgado de Letras de Copiapo":"02 Copiapo",
        "3o Juzgado de Letras de Copiapo":"03 Copiapo",
        "Juzgado de Letras y Gar.de Freirina":"Freirina",
        "4o Juzgado de Letras de Copiapo":"04 Copiapo",
        "1o Juzgado de Letras de Vallenar":"01 Vallenar",
        "2o Juzgado de Letras de Vallenar":"02 Vallenar",
        "Juzgado de Letras y Gar.de Caldera":"Caldera",
        "1o Juzgado de Letras de la Serena":"01 la Serena",
        "2o Juzgado de Letras de la Serena":"02 la Serena",
        "3o Juzgado de Letras de la Serena":"03 la Serena",
        "1o Juzgado de Letras de Coquimbo":"01 Coquimbo",
        "2o Juzgado de Letras de Coquimbo":"02 Coquimbo",
        "3o Juzgado de Letras de Coquimbo":"03 Coquimbo",
        "Juzgado de Letras de Vicuna":"Vicuna",
        "Juzgado de letras y garantia de Andacollo":"Andacollo",
        "1o Juzgado de Letras de Ovalle":"01 Ovalle",
        "2o Juzgado de Letras de Ovalle":"02 Ovalle",
        "3o Juzgado de Letras de Ovalle":"03 Ovalle",
        "Juzgado de Letras y Gar.de Combarbala":"Combarbala",
        "Juzgado de Letras de Illapel":"Illapel",
        "Juzgado de Letras y Gar. de los Vilos":"Vilos",
        "1o Juzgado Civil de Valparaiso":"01 Valparaiso",
        "2o Juzgado Civil de Valparaiso":"02 Valparaiso",
        "3o Juzgado Civil de Valparaiso":"03 Valparaiso",
        "4o Juzgado Civil de Valparaiso":"04 Valparaiso",
        "5o Juzgado Civil de Valparaiso":"05 Valparaiso",
        "1o Juzgado Civil de Vina del Mar":"01 Vina del Mar",
        "2o Juzgado Civil de Vina del Mar":"02 Vina del Mar",
        "3o Juzgado Civil de Vina del Mar":"03 Vina del Mar",
        "1o Juzgado de Letras de Quilpue":"01 Quilpue",
        "2o Juzgado de Letras de Quilpue":"02 Quilpue",
        "Juzgado de Letras de Villa Alemana":"Villa Alemana",
        "Juzgado de Letras de Casablanca":"Casablanca",
        "Juzgado de Letras de La Ligua":"La Ligua",
        "Juzgado de Letras y Gar. de Petorca":"Petorca",
        "1o Juzgado de Letras de Los Andes":"01 Los Andes",
        "2o Juzgado de Letras de Los Andes":"02 Los Andes",
        "1o Juzgado de Letras de San Felipe":"01 San Felipe",
        "2o Juzgado de Letras de San Felipe":"02 San Felipe",
        "Juzgado de Letras y Gar.de Putaendo":"Putaendo",
        "1o Juzgado de Letras de Quillota":"01 Quillota",
        "2o Juzgado de Letras de Quillota":"02 Quillota",
        "Juzgado de Letras de La Calera":"La Calera",
        "Juzgado de Letras de Limache":"Limache",
        "1o Juzgado de Letras de San Antonio":"01 San Antonio",
        "2o Juzgado de Letras de San Antonio":"02 San Antonio",
        "Juzgado de Letras y Gar. de Isla de Pascua":"Isla de Pascua",
        "Juzgado de Letras y Gar.de Quintero":"Quintero",
        "1o Juzgado Civil de Rancagua":"01 Rancagua",
        "2o Juzgado Civil de Rancagua":"02 Rancagua",
        "1o Juzgado de Letras de Rengo":"Rengo",
        "Juzgado de Letras de San Vicente de Tagua":"Tagua",
        "1o Juzgado de Letras y Gar.de Peumo":"01 Peumo",
        "1o Juzgado de Letras de San Fernando":"01 San Fernando",
        "2o Juzgado de Letras de San Fernando":"02 San Fernando",
        "1o Juzgado De Letras De Santa Cruz":"01 Santa Cruz",
        "2o Juzgado de Letras de Santa Cruz":"02 Santa Cruz",
        "Juzgado de Letras y Gar.de Pichilemu":"Pichilemu",
        "Juzgado de Letras y Gar.de Litueche":"Litueche",
        "Juzgado de Letras y Gar.de Peralillo":"Peralillo",
        "1o Juzgado de Letras de Talca":"01 Talca",
        "2o Juzgado de Letras de Talca":"02 Talca",
        "3o Juzgado de Letras de Talca":"03 Talca",
        "4o Juzgado de Letras de Talca":"04 Talca",
        "Juzgado de Letras de Constitucion":"Constitucion",
        "Juzgado De Letras Y Gar. de Curepto":"Curepto",
        "1o Juzgado de Letras de Curico":"01 Curico",
        "2o Juzgado de Letras de Curico":"02 Curico",
        "3o Juzgado de Letras de Curico":"03 Curico",
        "Juzgado De Letras Y Gar. de Licanten":"Licanten",
        "Juzgado de Letras de Molina":"Molina",
        "1o Juzgado de Letras de Linares":"01 Linares",
        "2o Juzgado de Letras de Linares":"02 Linares",
        "Juzgado de Letras de San Javier":"San Javier",
        "Juzgado de Letras de Cauquenes":"Cauquenes",
        "Juzgado de Letras y Gar. de Chanco":"Chanco",
        "Juzgado de Letras de Parral":"Parral",
        "1o Juzgado Civil de Chillan":"01 Chillan",
        "2o Juzgado Civil de Chillan":"02 Chillan",
        "1o Juzgado de Letras de San Carlos":"01 San Carlos",
        "Juzgado de Letras de Yungay":"Yungay",
        "Juzgado de Letras y Gar. de Bulnes":"Bulnes",
        "Juzgado de Letras y Gar.de Coelemu":"Coelemu",
        "Juzgado de Letras y Gar.de Quirihue":"Quirihue",
        "1o Juzgado de Letras de Los Angeles":"01 Angeles",
        "2o Juzgado de Letras de Los Angeles":"02 Angeles",
        "2o Juzgado de Letras de Los Angeles":"03 Angeles",
        "Juzgado de Letras y Gar. de Mulchen":"Mulchen",
        "Juzgado de Letras y Gar.de Nacimiento":"Nacimiento",
        "Juzgado de Letras y Gar.de Laja":"Laja",
        "Juzgado de Letras y Gar.de Yumbel":"Yumbel",
        "1o Juzgado Civil de Concepcion":"01 Concepcion",
        "2o Juzgado Civil de Concepcion":"02 Concepcion",
        "3o Juzgado Civil de Concepcion":"03 Concepcion",
        "4o Juzgado Civil de Concepcion":"04 Concepcion",
        "1o Juzgado Civil de Talcahuano":"01 Talcahuano",
        "2o Juzgado Civil de Talcahuano":"02 Talcahuano",
        "Juzgado de Letras de Tome":"Tome",
        "Juzgado de Letras y Gar.de Florida":"Florida",
        "Juzgado de Letras y Gar.de Santa Juana":"Santa Juana",
        "Juzgado de Letras y Gar. de Lota":"Lota",
        "1o Juzgado de Letras de Coronel":"01 Coronel",
        "2o Juzgado de Letras de Coronel":"02 Coronel",
        "Juzgado de Letras y Gar.de Lebu":"Lebu",
        "Juzgado de Letras de Arauco":"Arauco",
        "Juzgado de Letras y Gar.de Curanilahue":"Curanilahue",
        "Juzgado de Letras de Canete":"Canete",
        "Juzgado de Letras y Gar. Santa Barbara":"Santa Barbara",
        "Juzgado de Letras y Gar.de Cabrero":"Cabrero",
        "1o Juzgado Civil de Temuco":"01 Temuco",
        "2o Juzgado Civil de Temuco":"02 Temuco",
        "Juzgado de Letras de Angol":"Angol",
        "Juzgado de Letras y Gar.de Collipulli":"Collipulli",
        "Juzgado de Letras y Gar.de Traiguen":"Traiguen",
        "Juzgado de Letras de Victoria":"Victoria",
        "Juzgado de Letras y Gar.de Curacautin":"Curacautin",
        "Juzgado de Letras Loncoche":"Loncoche",
        "Juzgado de Letras de Pitrufquen":"Pitrufquen",
        "Juzgado de Letras de Villarrica":"Villarrica",
        "Juzgado de Letras de Nueva Imperial":"Nueva Imperial",
        "Juzgado de Letras y Gar.de Pucon":"Pucon",
        "Juzgado de Letras de Lautaro":"Lautaro",
        "Juzgado de Letras y Gar.de Carahue":"Carahue",
        "3o Juzgado Civil de Temuco":"03 Temuco",
        "Juzgado de Letras y Gar.de Tolten":"Tolten",
        "Juzgado de Letras y Gar.de Puren":"Puren",
        "1o Juzgado Civil de Valdivia":"01 Valdivia",
        "2o Juzgado Civil de Valdivia":"02 Valdivia",
        "Juzgado de Letras de Mariquina":"Mariquina",
        "Juzgado de Letras y Gar.de Paillaco":"Paillaco",
        "Juzgado de Letras Los Lagos":"Los Lagos",
        "Juzgado de Letras y Gar. de Panguipulli":"Panguipulli",
        "Juzgado de Letras y Gar.de la Union":"la Union",
        "Juzgado de Letras y Gar.de Rio Bueno":"Rio Bueno",
        "1o Juzgado de Letras de Osorno":"01 Osorno",
        "2o Juzgado de Letras de Osorno":"02 Osorno",
        "Juzgado de Letras de Rio Negro":"Rio Negro",
        "1o Juzgado Civil de Puerto Montt":"01 Puerto Montt",
        "2o Juzgado Civil de Puerto Montt":"02 Puerto Montt",
        "Juzgado de Letras de Puerto Varas":"Puerto Varas",
        "Juzgado de Letras y Gar.de Calbuco":"Calbuco",
        "Juzgado de Letras y Gar. de Maullin":"Maullin",
        "Juzgado de Letras de Castro":"Castro",
        "Juzgado de Letras de Ancud":"Ancud",
        "Juzgado de Letras y Garantia de Achao":"Achao",
        "Juzgado de Letras y Gar. de Chaiten":"Chaiten",
        "Juzgado de Letras y Gar. de Los Muermos":"Los Muermos",
        "Juzgado de Letras y Gar. de Quellon":"Quellon",
        "Juzgado de Letras y Gar. de Hualaihue":"Hualaihue",
        "1o Juzgado de Letras de Coyhaique":"01 Coyhaique",
        "1o Juzgado de Letras de Coyhaique":"02 Coyhaique",
        "Juzgado de Letras y Gar.de pto.Aysen":"pto.Aysen",
        "Juzgado de Letras y Gar.de Chile Chico":"Chile Chico",
        "Juzgado de Letras y Gar.de Cochrane":"Cochrane",
        "Juzgado de Letras y Gar.de Puerto Cisnes":"Puerto Cisnes",
        "1o Juzgado de Letras de Punta Arenas":"01 Punta Arenas",
        "2o Juzgado de Letras de Punta Arenas":"02 Punta Arenas",
        "3o Juzgado de Letras de Punta Arenas":"03 Punta Arenas",
        "Juzgado de Letras y Gar. de Puerto Natales":"Puerto Natales",
        "Juzgado de Letras y Gar.de Porvenir":"Porvenir",
        "Juzgado de Letras y Garantia de Cabo de Hornos":"Cabo de Hornos",
        "1o Juzgado Civil de Santiago":"01 Santiago",
        "2o Juzgado Civil de Santiago":"02 Santiago",
        "3o Juzgado Civil de Santiago":"03 Santiago",
        "4o Juzgado Civil de Santiago":"04 Santiago",
        "5o Juzgado Civil de Santiago":"05 Santiago",
        "6o Juzgado Civil de Santiago":"06 Santiago",
        "7o Juzgado Civil de Santiago":"07 Santiago",
        "8o Juzgado Civil de Santiago":"08 Santiago",
        "9o Juzgado Civil de Santiago":"09 Santiago",
        "10o Juzgado Civil de Santiago":"10 Santiago",
        "11o Juzgado Civil de Santiago":"11 Santiago",
        "12o Juzgado Civil de Santiago":"12 Santiago",
        "13o Juzgado Civil de Santiago":"13 Santiago",
        "14o Juzgado Civil de Santiago":"14 Santiago",
        "15o Juzgado Civil de Santiago":"15 Santiago",
        "16o Juzgado Civil de Santiago":"16 Santiago",
        "17o Juzgado Civil de Santiago":"17 Santiago",
        "18o Juzgado Civil de Santiago":"18 Santiago",
        "19o Juzgado Civil de Santiago":"19 Santiago",
        "20o Juzgado Civil de Santiago":"20 Santiago",
        "21o Juzgado Civil de Santiago":"20 Santiago",
        "22o Juzgado Civil de Santiago":"20 Santiago",
        "23o Juzgado Civil de Santiago":"20 Santiago",
        "24o Juzgado Civil de Santiago":"20 Santiago",
        "25o Juzgado Civil de Santiago":"20 Santiago",
        "26o Juzgado Civil de Santiago":"20 Santiago",
        "27o Juzgado Civil de Santiago":"20 Santiago",
        "28o Juzgado Civil de Santiago":"20 Santiago",
        "29o Juzgado Civil de Santiago":"20 Santiago",
        "30o Juzgado Civil de Santiago":"20 Santiago",
        "Juzgado de Letras de Colina":"Colina",
        "1o Juzgado Civil de San Miguel":"01 San Miguel",
        "2o Juzgado Civil de San Miguel":"02 San Miguel",
        "3o Juzgado Civil de San Miguel":"03 San Miguel",
        "4o Juzgado Civil de San Miguel":"04 San Miguel",
        "1o Juzgado Civil de Puente Alto":"01 Puente Alto",
        "1o Juzgado De Letras De Talagante":"01 Talagante",
        "2o Juzgado De Letras De Talagante":"02 Talagante",
        "1o Juzgado de Letras de Melipilla":"01 Melipilla",
        "1o Juzgado de Letras de Buin":"01 Buin",
        "2o Juzgado de Letras de Buin":"02 Buin",
        "Juzgado de Letras de Penaflor":"Penaflor",
        "1o Juzgado de Letras de San Bernardo":"01 San Bernardo",
        "2o Juzgado de Letras de San Bernardo":"02 San Bernardo",
        "3o Juzgado de Letras de San Bernardo":"03 San Bernardo",
        "4o Juzgado de Letras de San Bernardo":"04 San Bernardo",
    }
    for juzgado in juzgados:
        if juzgado.upper() in texto.upper():
            return juzgados[juzgado]
    return ""

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
    patron = re.compile("[0-9]{1,2}(.?)[0-9]{1,3}\s(hectareas|Hectareas|HECTAREAS|Has|HAS|has)")
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
    if len(fechas) >= 3:
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
    patron = re.compile("[1-9]{1,2}\.?[0-9]{3}\s(metro|Metro|METRO|metros|Metros|METROS|m|M)")
    aux_text = pedimento.texto
    try_find = 2
    lados = []
    while try_find != 0:
        if patron.search(aux_text):
            lado = patron.search(aux_text).group().split(" ")[0].replace(".","")
            lados.append(lado)
            aux_text = aux_text.replace(patron.search(aux_text).group(), " ",1)
        try_find-=1
    if len(lados) == 2:
        pedimento.n_scarasup = lados[0]
        pedimento.e_ocarasup = lados[1]
        if pedimento.hectareas is not None:
            if (int(pedimento.n_scarasup)*int(pedimento.e_ocarasup))/10000 != int(pedimento.hectareas):
                pedimento.obser+=",Hectareas no congruentes con lados"
    pedimento.juzgado = get_juzgado(pedimento.texto)
    comuna_provincia_region = get_comuna(pedimento.texto)
    pedimento.comuna = comuna_provincia_region[0] if len(comuna_provincia_region)>0 else ""
    pedimento.provincia = comuna_provincia_region[1][0] if len(comuna_provincia_region)>1 and len(comuna_provincia_region[1])>0 else ""
    pedimento.region = comuna_provincia_region[1][1] if len(comuna_provincia_region)>1 and len(comuna_provincia_region[1])>1 else ""
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
        x.cpu = "0"
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

def download(request):
    template_name = 'reporte_registros.html'
    data = {}
    data["diario"] = Diario.objects.all()
    #tipo_reporte = type_matches(request.POST[""])
    if request.POST:
        if request.POST['type'] == 'pedimentos':
            response = download_pedi(request)
        if request.POST['type'] == 'ver_concesiones':
            response = download_ver_conce(request)
        if request.POST['type'] == 'concesiones':
            response = download_conce(request)
        if request.POST['type'] == 'manifestaciones':
            response = download_manifes(request)
        if request.POST['type'] == 'ver_mensuras':
            response = download_ver_mensu(request)
        if request.POST['type'] == 'mensuras':
            response = download_mensu(request)
        return response
    
    return render(request, template_name, data)


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
            #the text after of solicitud. is the attributes
            # response["FDIAR_APRO"] = solicitud.FDIAR_APRO#.strftime("%Y-%M-%D")
            response["BOLETIN"] = solicitud.boletin or ''
            response["F_BOLETIN"] = '' if solicitud.f_boletin is None or len(solicitud.f_boletin)==0 else (datetime.datetime.strptime(solicitud.f_boletin, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["CONCESION"] = '' if solicitud.concesion is None else solicitud.concesion.encode('utf-8')
            response["CONCESIONA"] = '' if solicitud.concesiona is None else solicitud.concesiona.encode('utf-8')
            response["REPRESENTA"] = '' if solicitud.representa is None else solicitud.representa.encode('utf-8')
            response["DIRECCION"] = '' if solicitud.direccion is None else solicitud.direccion.encode('utf-8')
            response["REGION"] = solicitud.region or ''
            response["PROVINCIA"] = '' if solicitud.provincia is None else solicitud.provincia.encode('utf-8')
            response["COMUNA"] = '' if solicitud.comuna is None else solicitud.comuna.encode('utf-8')
            response["LUGAR"] = '' if solicitud.lugar is None else solicitud.lugar.encode('utf-8')
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
            response["IND_METAL"] = '' if solicitud.ind_metal is None else solicitud.ind_metal.encode('utf-8')
            hectareas = 0
            if solicitud.hectareas is not None:
                hectareas = float(solicitud.hectareas)
            response["HECTAREAS"] = hectareas or 0
            response["HA_PERT"] = '' if solicitud.ha_pert is None else solicitud.ha_pert.encode('utf-8')
            response["JUZGADO"] = '' if solicitud.juzgado is None else solicitud.juzgado.encode('utf-8')
            response["ROLJUZ"] = '' if solicitud.roljuz is None else solicitud.roljuz.encode('utf-8')
            response["F_PRESENTA"] = '' if solicitud.f_presenta is None or len(solicitud.f_presenta)==0 else (datetime.datetime.strptime(solicitud.f_presenta, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_RESOLUCI"] = '' if solicitud.f_resoluci is None or len(solicitud.f_resoluci)==0 else (datetime.datetime.strptime(solicitud.f_resoluci, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_INSCRIBE"] = '' if solicitud.f_inscribe is None or len(solicitud.f_inscribe)==0 else (datetime.datetime.strptime(solicitud.f_inscribe, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["FOJAS"] = '' if solicitud.fojas is None else solicitud.fojas.encode('utf-8')
            response["NUMERO"] = '' if solicitud.numero is None else solicitud.numero.encode('utf-8')
            response["YEAR"] = '' if solicitud.year is None else solicitud.year.encode('utf-8')
            response["CIUDAD"] = '' if solicitud.ciudad is None else solicitud.ciudad.encode('utf-8').encode('utf-8')
            response["CARTAIGM"] = '' if solicitud.cartaigm is None else solicitud.cartaigm.encode('utf-8')
            response["OBSER"] = '' if solicitud.obser is None else solicitud.obser.encode('utf-8')
            response["DATUM"] = '' if solicitud.datum is None else solicitud.datum.encode('utf-8')
            response["F_PRESTRIB"] = '' if solicitud.f_prestrib is None or len(solicitud.f_prestrib)==0 else (datetime.datetime.strptime(solicitud.f_prestrib, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["ARCHIVO"] = '' if solicitud.archivo is None else solicitud.archivo.encode('utf-8')
            response["CORTE"] = '' if solicitud.corte is None else solicitud.corte.encode('utf-8')
            response["EDITOR"] = '' if solicitud.editor is None else solicitud.editor.encode('utf-8')
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
            response["CONCESION"] = '' if solicitud.concesion is None else solicitud.concesion.encode('utf-8')
            response["CONCESIONA"] = '' if solicitud.concesiona is None else solicitud.concesiona.encode('utf-8')
            response["REPRESENTA"] = '' if solicitud.representa is None else solicitud.representa.encode('utf-8')
            response["DIRECCION"] = '' if solicitud.direccion is None else solicitud.direccion.encode('utf-8')
            response["REGION"] = solicitud.region or ''
            response["PROVINCIA"] = '' if solicitud.provincia is None else solicitud.provincia.encode('utf-8')
            response["COMUNA"] = '' if solicitud.comuna is None else solicitud.comuna.encode('utf-8')
            response["LUGAR"] = '' if solicitud.comuna is None else solicitud.comuna.encode('utf-8')
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
            response["HA_PERT"] = '' if solicitud.ha_pert is None else solicitud.ha_pert.encode('utf-8')
            response["JUZGADO"] = '' if solicitud.juzgado is None else solicitud.juzgado.encode('utf-8')
            response["ROLJUZ"] = '' if solicitud.roljuz is None else solicitud.roljuz.encode('utf-8')
            response["F_PRESENTA"] = '' if solicitud.f_presenta is None or len(solicitud.f_presenta)==0 else (datetime.datetime.strptime(solicitud.f_presenta, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_RESOLUCI"] = '' if solicitud.f_resoluci is None or len(solicitud.f_resoluci)==0 else (datetime.datetime.strptime(solicitud.f_resoluci, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_INSCRIBE"] = '' if solicitud.f_resoluci is None or len(solicitud.f_resoluci)==0 else (datetime.datetime.strptime(solicitud.f_resoluci, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["FOJAS"] = '' if solicitud.fojas is None else solicitud.fojas.encode('utf-8')
            response["NUMERO"] = '' if solicitud.numero is None else solicitud.numero.encode('utf-8')
            response["YEAR"] = '' if solicitud.year is None else solicitud.year.encode('utf-8')
            response["CIUDAD"] = '' if solicitud.ciudad is None else solicitud.ciudad.encode('utf-8')
            response["CARTAIGM"] = '' if solicitud.cartaigm is None else solicitud.cartaigm.encode('utf-8')
            response["OBSER"] = '' if solicitud.obser is None else solicitud.obser.encode('utf-8')
            response["PED_ASOC"] = '' if solicitud.ped_asoc is None else solicitud.ped_asoc.encode('utf-8')
            response["FECHAPED"] = '' if solicitud.fechaped is None or len(solicitud.fechaped)==0 else (datetime.datetime.strptime(solicitud.fechaped, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["ROLPED"] = '' if solicitud.rolped is None else solicitud.rolped.encode('utf-8')
            response["TIPOCOORD"] = solicitud.tipocoord or ''
            response["NORTE"] = '' if solicitud.norte is None else solicitud.norte.encode('utf-8')
            response["MTSN"] = '' if solicitud.mtsn is None else solicitud.mtsn.encode('utf-8')
            response["SUR"] = '' if solicitud.sur is None else solicitud.sur.encode('utf-8')
            response["MTSS"] = '' if solicitud.mtss is None else solicitud.mtss.encode('utf-8')
            response["ESTE"] = '' if solicitud.este is None else solicitud.este.encode('utf-8')
            response["MTSE"] = '' if solicitud.mtse is None else solicitud.mtse.encode('utf-8')
            response["OESTE"] = '' if solicitud.oeste is None else solicitud.oeste.encode('utf-8')
            response["MTSO"] = '' if solicitud.mtso is None else solicitud.mtso.encode('utf-8')
            response["F_PRESTRIB"] = '' if solicitud.f_prestrib is None or len(solicitud.f_prestrib)==0 else (datetime.datetime.strptime(solicitud.f_prestrib, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["DATUM"] = '' if solicitud.datum is None else solicitud.datum.encode('utf-8')
            response["ARCHIVO"] = '' if solicitud.archivo is None else solicitud.archivo.encode('utf-8')
            response["CORTE"] = '' if solicitud.corte is None else solicitud.corte.encode('utf-8')
            response["EDITOR"] = '' if solicitud.editor is None else solicitud.editor.encode('utf-8')
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
            response["CONCESION"] = '' if solicitud.concesion is None else solicitud.concesion.encode('utf-8')
            response["CONCESIONA"] = '' if solicitud.concesiona is None else solicitud.concesiona.encode('utf-8')
            response["REPRESENTA"] = '' if solicitud.representa is None else solicitud.representa.encode('utf-8')
            response["DIRECCION"] = '' if solicitud.direccion is None else solicitud.direccion.encode('utf-8')
            response["ROLMINERO"] = '' if solicitud.rolminero is None else solicitud.rolminero.encode('utf-8')
            response["F_SENTENC1"] = '' if solicitud.f_sentenc1 is None or len(solicitud.f_sentenc1)==0 else (datetime.datetime.strptime(solicitud.f_sentenc1, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_SENTENC2"] = '' if solicitud.f_sentenc2 is None or len(solicitud.f_sentenc2)==0 else (datetime.datetime.strptime(solicitud.f_sentenc2, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_PUBEXT"] =  '' if solicitud.f_pubext is None or len(solicitud.f_pubext)==0 else (datetime.datetime.strptime(solicitud.f_pubext, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["F_INSCMIN"] = '' if solicitud.f_inscmin is None or len(solicitud.f_inscmin)==0 else (datetime.datetime.strptime(solicitud.f_inscmin, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["FOJAS"] = solicitud.fojas or ''
            response["NUMERO"] = solicitud.numero or ''
            response["YEAR"] = solicitud.year or ''
            response["CIUDAD"] = '' if solicitud.ciudad is None else solicitud.ciudad.encode('utf-8')
            response["JUZGADO"] = '' if solicitud.juzgado is None else solicitud.juzgado.encode('utf-8')
            response["ROLJUZ"] = '' if solicitud.roljuz is None else solicitud.roljuz.encode('utf-8')
            response["IND_METAL"] = '' if solicitud.ind_metal is None else solicitud.ind_metal.encode('utf-8')
            response["REGION"] = '' if solicitud.region is None else solicitud.region.encode('utf-8')
            response["PROVINCIA"] = '' if solicitud.provincia is None else solicitud.provincia.encode('utf-8')
            response["COMUNA"] = '' if solicitud.comuna is None else solicitud.comuna.encode('utf-8')
            response["LUGAR"] = '' if solicitud.lugar is None else solicitud.lugar.encode('utf-8')
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
            response["CONCESION"] =  '' if solicitud.concesion is None else solicitud.concesion.encode('utf-8')
            response["CONCESIONA"] =  '' if solicitud.concesiona is None else solicitud.concesiona.encode('utf-8')
            response["REPRESENTA"] =  '' if solicitud.representa is None else solicitud.representa.encode('utf-8')
            response["DIRECCION"] =  '' if solicitud.direccion is None else solicitud.direccion.encode('utf-8')
            response["JUZGADO"] =  '' if solicitud.juzgado is None else solicitud.juzgado.encode('utf-8')
            response["ROLJUZ"] =  '' if solicitud.roljuz is None else solicitud.roljuz.encode('utf-8')
            response["REGION"] =  solicitud.region or ''
            response["PROVINCIA"] =  '' if solicitud.provincia is None else solicitud.provincia.encode('utf-8')
            response["COMUNA"] =  '' if solicitud.comuna is None else solicitud.comuna.encode('utf-8')
            response["LUGAR"] =  '' if solicitud.lugar is None else solicitud.lugar.encode('utf-8')
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
            response["N1"] =  '' if solicitud.n1 is None else solicitud.n1.encode('utf-8')
            response["HA1"] =  '' if solicitud.ha1 is None else solicitud.ha1.encode('utf-8')
            response["N_S1"] =  '' if solicitud.n_s1 is None else solicitud.n_s1.encode('utf-8')
            response["E_O1"] =  '' if solicitud.e_o1 is None else solicitud.e_o1.encode('utf-8')
            response["N2"] =  '' if solicitud.n2 is None else solicitud.n2.encode('utf-8')
            response["HA2"] =  '' if solicitud.ha2 is None else solicitud.ha2.encode('utf-8')
            response["N_S2"] =  '' if solicitud.n_s2 is None else solicitud.n_s2.encode('utf-8')
            response["E_O2"] =  '' if solicitud.e_o2 is None else solicitud.e_o2.encode('utf-8')
            response["N3"] =  '' if solicitud.n3 is None else solicitud.n3.encode('utf-8')
            response["HA3"] =  '' if solicitud.ha3 is None else solicitud.ha3.encode('utf-8')
            response["N_S3"] =  '' if solicitud.n_s3 is None else solicitud.n_s3.encode('utf-8')
            response["E_O3"] =  '' if solicitud.e_o3 is None else solicitud.e_o3.encode('utf-8')
            response["N4"] =  '' if solicitud.n4 is None else solicitud.n4.encode('utf-8')
            response["HA4"] =  '' if solicitud.ha4 is None else solicitud.ha4.encode('utf-8')
            response["N_S4"] =  '' if solicitud.n_s4 is None else solicitud.n_s4.encode('utf-8')
            response["E_O4"] =  '' if solicitud.e_o4 is None else solicitud.e_o4.encode('utf-8')
            response["HA_PERT"] =  '' if solicitud.ha_pert is None else solicitud.ha_pert.encode('utf-8')
            response["IND_METAL"] =  '' if solicitud.ind_metal is None else solicitud.ind_metal.encode('utf-8')
            response["IND_VIGE"] =  '' if solicitud.ind_vige is None else solicitud.ind_vige.encode('utf-8')
            response["RAZON"] =  '' if solicitud.razon is None else solicitud.razon.encode('utf-8')
            response["PERITO"] =  '' if solicitud.perito is None else solicitud.perito.encode('utf-8')
            response["OPOSICION"] =  '' if solicitud.oposicion is None else solicitud.oposicion.encode('utf-8')
            response["DATUM"] =  '' if solicitud.datum is None else solicitud.datum.encode('utf-8')
            response["F_PRESTRIB"] =  '' if solicitud.f_prestrib is None or len(solicitud.f_prestrib)==0 else (datetime.datetime.strptime(solicitud.f_prestrib, '%Y/%m/%d').strftime('%Y%m%d')) or ''
            response["ARCHIVO"] =  '' if solicitud.archivo is None else solicitud.archivo.encode('utf-8')
            response["CORTE"] =  '' if solicitud.corte is None else solicitud.corte.encode('utf-8')
            huso = 0
            if solicitud.huso != "No se detecta Huso" and solicitud.huso is not None:
                huso = float(solicitud.huso)
            response["HUSO"] =  huso or 0
            response["EDITOR"] =  '' if solicitud.editor is None else solicitud.editor.encode('utf-8')
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
    diario = Diario.objects.get(pk=request.POST["fecha"])
    for solicitud in solicitudes:
        if solicitud.registro_mineria.tipo_tramite == "EXTRACTOS DE SENTENCIA DE EXPLORACION" or solicitud.registro_mineria.tipo_tramite == "EXTRACTOS DE SENTENCIA DE EXPLORACION":
            if diario.fecha == solicitud.f_boletin:
                response = db.newRecord()
                #the text after of solicitud. is the attributes
                # response["FDIAR_APRO"] = solicitud.FDIAR_APRO#.strftime("%Y-%M-%D")
                response["BOLETIN"] = solicitud.boletin or ''
                response["F_BOLETIN"] = '' if solicitud.f_boletin is None or len(solicitud.f_boletin)==0 else (datetime.datetime.strptime(solicitud.f_boletin, '%Y/%m/%d').strftime('%Y%m%d')) or ''
                response["CONCESION"] = '' if solicitud.concesion is None else solicitud.concesion.encode('utf-8')
                response["REGION"] = solicitud.region or ''
                response["ROLJUZ"] = '' if solicitud.roljuz is None else solicitud.roljuz.encode('utf-8')
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
    diario = Diario.objects.get(pk=request.POST["fecha"])
    solicitudes = Vertice.objects.all()#Get all register in case that the user wish generate a dbf with all register without care the date
    for solicitud in solicitudes:
        if solicitud.registro_mineria.tipo_tramite == "SOLICITUDES DE MENSURA":
            if diario.fecha == solicitud.f_boletin:
                response = db.newRecord()
                #the text after of solicitud. is the attributes
                # response["FDIAR_APRO"] = solicitud.FDIAR_APRO#.strftime("%Y-%M-%D")
                response["BOLETIN"] = solicitud.boletin or ''
                response["F_BOLETIN"] = '' if solicitud.f_boletin is None or len(solicitud.f_boletin)==0 else (datetime.datetime.strptime(solicitud.f_boletin, '%Y/%m/%d').strftime('%Y%m%d')) or ''
                response["CONCESION"] = '' if solicitud.concesion is None else solicitud.concesion.encode('utf-8')
                response["REGION"] = solicitud.region or ''
                response["ROLJUZ"] = '' if solicitud.roljuz is None else solicitud.roljuz.encode('utf-8')
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