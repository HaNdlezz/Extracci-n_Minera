# -*- coding: utf-8 -*-
from core.utils import utils

class extraction():

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
        comuna_provincia_region = utils.get_comuna(pedimento.texto)
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
