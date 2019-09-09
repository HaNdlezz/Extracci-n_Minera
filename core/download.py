# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.conf import settings
from core.models import *
import pdb
import os
import datetime
import unidecode
from dbfpy import dbf

class download():

    #Function for create dbf of Pedimentos
    @classmethod
    def download_pedi(cls, request):
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
        file_path = os.path.join(settings.BASE_DIR, "Static/" + file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/x-dbase")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                os.remove(file_path)
                return response
        raise Http404






    #Function for create dbf of Manifestaciones
    @classmethod
    def download_manifes(cls, request):
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
        file_path = os.path.join(settings.BASE_DIR, "Static/" + file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/x-dbase")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                os.remove(file_path)
                return response
        raise Http404






    #Function for create dbf of Coneciones
    @classmethod
    def download_conce(cls, request):
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
        file_path = os.path.join(settings.BASE_DIR, "Static/" + file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/x-dbase")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                os.remove(file_path)
                return response
        raise Http404





    #Function for create dbf of Mensuras
    @classmethod
    def download_mensu(cls, request):
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
        file_path = os.path.join(settings.BASE_DIR, "Static/" + file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/x-dbase")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                os.remove(file_path)
                return response
        raise Http404






    #Function for create dbf of Vertices Coneciones
    @classmethod
    def download_ver_conce(cls, request):
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
        file_path = os.path.join(settings.BASE_DIR, "Static/" + file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/x-dbase")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                #os.remove(file_path)
                return response
        raise Http404





    #Function for create dbf of Vertices Mensuras
    @classmethod
    def download_ver_mensu(cls, request):
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
        file_path = os.path.join(settings.BASE_DIR, "Static/" + file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/x-dbase")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                os.remove(file_path)
                return response
        raise Http404