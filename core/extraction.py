# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.conf import settings
from core.models import *
import pdb
import os
import re
import json
import datetime
import unidecode
from core.utils import utils

class extraction():

    @classmethod
    def format_date(cls, fecha):
        meses = {"enero": "1", "febrero": "2", "marzo": "3", "abril": "4", "mayo": "5", "junio": "6", "julio": "7", "agosto": "8", "septiembre": "9", "octubre": "10", "noviembre": "11", "diciembre": "12"}
        dias = {"primero": "1", "uno": "1", "dos": "2", "tres": "3", "cuatro": "4", "cinco": "5", "seis": "6", "siete": "7", "ocho": "8", "nueve": "9", "diez": "10", "once": "11", "doce": "12", "trece": "13", "catorce": "14", "quince": "15", "dieciseis": "16", "diecisiete": "17", "dieciocho": "18", "diecinueve": "19", "veinte": "20", "veintiuno": "21", "veintidos": "22", "veintitres": "23", "veinticuatro": "24", "veinticinco": "25", "veintiseis": "26", "veintisiete": "27", "veintiocho": "28", "veintinueve": "29", "treinta": "30", "treinta y uno": "31"}
        anios = {"mil":"2000","uno": "2001","dos": "2002","tres": "2003", "cuatro": "2004", "cinco": "2005", "seis": "2006", "siete": "2007", "ocho": "2008", "nueve": "2009", "diez": "2010", "once": "2011", "doce": "2012", "trece": "2013", "catorce": "2014", "quince": "2015", "dieciseis": "2016", "diecisiete": "2017", "dieciocho": "2018", "diecinueve": "2019", "veinte": "2020"}
        fecha = fecha[1:].lower().split(" ")
        dia = dias[fecha[0]] if fecha[0] in dias else fecha[0]
        mes = meses[fecha[2]] if fecha[2] in meses else fecha[2]
        anio = anios[fecha[-1]] if fecha[-1] in anios else fecha[-1]
        fecha = dia+"/"+mes+"/"+anio
        return fecha

    @classmethod
    def extract_dates(cls, texto):
        patron3 = re.compile("\s[1-9]{1,2}\s*?(\n)?(de)\s*?(\n)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(\s*)?(\n)?(de)(\s*)?(\n)?([\w]*)(\s*)?(\n)?([\w]*)(\s*)?(\n)?([\w]*)", re.I)
        patron4 = re.compile("\s([\w\d]*)\s*?(\n)?(de)\s*?(\n)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(\s*)?(\n)?(de)(\s*)?(\n)?([\w]*)(\s*)?(\n)?([\w]*)(\s*)?(\n)?([\w]*)", re.I)
        patron1 = re.compile("\s[1-9]{1,2}\s*?(\n)?(de)\s*?(\n)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(\s*)?(\n)?(del)(\s*)?(\n)?([\w]*)(\s*)?(\n)?([\w]*)(\s*)?(\n)?([\w]*)(\s*)?(\n)?([\w]*)", re.I)
        patron2 = re.compile("\s([\w\d]*)\s*?(\n)?(de)\s*?(\n)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(\s*)?(\n)?(del)(\s*)?(\n)?([\w]*)(\s*)?(\n)?([\w]*)(\s*)?(\n)?([\w]*)(\s*)?(\n)?([\w]*)", re.I)
        patron7 = re.compile("\s[1-9]{1,2}\s*?(\n)?(de)\s*?(\n)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(\s*)?(\n)?(de)(\s*)?(\n)?[0-9]{4}", re.I)
        patron8 = re.compile("\s([\w\d]*)\s*?(\n)?(de)\s*?(\n)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(\s*)?(\n)?(de)(\s*)?(\n)?[0-9]{4}", re.I)
        patron5 = re.compile("\s[1-9]{1,2}\s*?(\n)?(de)\s*?(\n)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(\s*)?(\n)?(del)(\s*)?(\n)?([\w]*)(\s*)?(\n)?[0-9]{4}", re.I)
        patron6 = re.compile("\s([\w\d]*)\s*?(\n)?(de)\s*?(\n)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(\s*)?(\n)?(del)(\s*)?(\n)?([\w]*)(\s*)?(\n)?[0-9]{4}", re.I)
        fechas = []
        buscar = unidecode.unidecode(texto).replace(".","")
        try_get_fecha = 5
        while try_get_fecha != 0:
            if patron1.search(buscar):
                fecha = patron1.search(buscar).group()
                buscar = buscar.replace(fecha, " ")
                fechas.append(extraction.format_date(fecha))
                print "one"
            if patron2.search(buscar):
                fecha = patron2.search(buscar).group()
                buscar = buscar.replace(fecha, " ")
                fechas.append(extraction.format_date(fecha))
                print "two"
            if patron3.search(buscar):
                fecha = patron3.search(buscar).group()
                buscar = buscar.replace(fecha, " ")
                fechas.append(extraction.format_date(fecha))
                print "three"
            if patron4.search(buscar):
                fecha = patron4.search(buscar).group()
                buscar = buscar.replace(fecha, " ")
                fechas.append(extraction.format_date(fecha))
                print "four"
            if patron5.search(buscar):
                fecha = patron5.search(buscar).group()
                buscar = buscar.replace(fecha, " ")
                fechas.append(extraction.format_date(fecha))
                print "five"
            if patron6.search(buscar):
                fecha = patron6.search(buscar).group()
                buscar = buscar.replace(fecha, " ")
                fechas.append(extraction.format_date(fecha))
                print "six"
            if patron7.search(buscar):
                fecha = patron7.search(buscar).group()
                buscar = buscar.replace(fecha, " ")
                fechas.append(extraction.format_date(fecha))
                print "seven"
            if patron8.search(buscar):
                fecha = patron8.search(buscar).group()
                buscar = buscar.replace(fecha, " ")
                fechas.append(extraction.format_date(fecha))
                print "eigth"
            try_get_fecha-=1
        return fechas

    @classmethod
    def extraerConcesiones(cls, concesion):
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

    @classmethod
    def extraerManifestaciones(cls, manifestacion):
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

    @classmethod
    def extraerPedimentos(cls, pedimento):
        pedimento.tipo_utm = "M"
        patron = re.compile("(huso|zona)\s\d\d", re.I)
        if patron.search(pedimento.texto):
            pedimento.huso = patron.search(pedimento.texto).group().split(" ")[-1]
        else:
            pedimento.huso = "No se detecta Huso"
        patron = re.compile("[0-9]{1,2}(.?)[0-9]{1,3}(\n)?\s*?\t?(hectáreas|hectareas|has)", re.I)
        if patron.search(pedimento.texto.encode('utf-8')):
            pedimento.hectareas = patron.search(pedimento.texto.encode('utf-8')).group().replace(".","").split(" ")[0]
            pedimento.hectareas = pedimento.hectareas.replace("hectareas","")
            pedimento.hectareas = pedimento.hectareas.replace("hectarea","")
        patron = re.compile("[aA-zZ][-][0-9]{1,4}[-][0-9]{1,4}")
        if patron.search(pedimento.texto):
            pedimento.roljuz = patron.search(pedimento.texto).group()
            pedimento.year = patron.search(pedimento.texto).group().split("-")[-1]
        patron = re.compile("(JUZGADO:)\s?[\w\s\.]{1,}\s?(CAUSA)", re.I)
        if patron.search(pedimento.texto):
            pedimento.juzgado = patron.search(pedimento.texto).group().replace('JUZGADO:', '').replace('CAUSA', '').strip()
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
        patron = re.compile("(fojas|fj|foja|fs)\.?\s*?[0-9]{1,2}(.?)[0-9]{1,3}", re.I)
        if patron.search(pedimento.texto):
            try:
                pedimento.fojas = patron.search(pedimento.texto).group().replace(".","").split(" ")[1]
            except:
                pedimento.fojas = patron.search(pedimento.texto).group().replace(" ","").split(".")[1]
            aux_text = pedimento.texto.split(patron.search(pedimento.texto).group())[1]
            if "vta" in aux_text or "Vta" in aux_text or "Vuelta" in aux_text or "vuelta" in aux_text or "VTA" in aux_text or "VUELTA" in aux_text:
                pedimento.fojas = pedimento.fojas+" "+"VTA"
            patron = re.compile("(numero|Numero|NUMERO|)\s[0-9]{1,2}(.?)[0-9]{1,3}")
            if patron.search(aux_text):
                pedimento.numero = patron.search(aux_text).group().replace(".","").split(" ")[1]
        pedimento.obser = "(CVE "+pedimento.cve+")"
        patron = re.compile("datum\s?WGS?\s[1-9]{1,4}", re.I)
        datum = ""
        if patron.search(pedimento.texto):
            datum = patron.search(pedimento.texto).group()
            datum = datum.split(" ")
            datum = datum[-1]
        if str(datum) == "84" or str(datum) == "1984":
            datum = "WGS84"
        elif str(datum) == "56" or str(datum) == "1956":
            datum = "PSAD56"
        elif str(datum) == "69" or str(datum) == "1969":
            datum = "SAD69"
        patron = re.compile("canoa\s*?(de)?\s*?1956", re.I)
        if patron.search(pedimento.texto):
            datum = "PSAD56"
        pedimento.datum = datum
        patron = re.compile("[^\d\.][1-9]{1,2}\.?[0-9]{3}\,?([0-9]{1,3})?\s*?(metro|metros|m)", re.I)
        aux_text = pedimento.texto
        try_find = 2
        lados = []
        while try_find != 0:
            if patron.search(aux_text):
                lado = patron.search(aux_text).group()[1:].split(" ")[0].replace(".","")
                lados.append(lado)
                aux_text = aux_text.replace(patron.search(aux_text).group(), " ",1)
            try_find-=1
        if len(lados) == 2:
            if "," in lados[0]:
                pedimento.n_scarasup = lados[0].split(",")[0]
                pedimento.n_scarasup = pedimento.n_scarasup.replace("metro","")
            else:
                pedimento.n_scarasup = lados[0]
                pedimento.n_scarasup = pedimento.n_scarasup.replace("metro","")
            if "," in lados[1]:
                pedimento.e_ocarasup = lados[1].split(",")[0]
                pedimento.e_ocarasup = pedimento.e_ocarasup.replace("metro","")
            else:
                pedimento.e_ocarasup = lados[1]
                pedimento.e_ocarasup = pedimento.e_ocarasup.replace("metro","")
            if pedimento.hectareas is not None:
                if (int(pedimento.n_scarasup)*int(pedimento.e_ocarasup))/10000 != int(pedimento.hectareas):
                    pedimento.obser+=",Hectareas no congruentes con lados"
        pedimento.juzgado = utils.get_juzgado(pedimento.texto)
        comuna_provincia_region = utils.get_comuna(pedimento)
        pedimento.comuna = comuna_provincia_region[0] if len(comuna_provincia_region)>0 else ""
        pedimento.dates = extraction.extract_dates(pedimento.texto)
        print pedimento.dates
        # pedimento.provincia = comuna_provincia_region[1][0] if len(comuna_provincia_region)>1 and len(comuna_provincia_region[1])>0 else ""
        # pedimento.region = comuna_provincia_region[1][1] if len(comuna_provincia_region)>1 and len(comuna_provincia_region[1])>1 else ""
        pedimento.save()
        #print pedimento

    @classmethod
    def extraerMensuras(cls, mensura):
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
