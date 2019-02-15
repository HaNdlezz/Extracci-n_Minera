from __future__ import unicode_literals
from django.shortcuts import get_object_or_404
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from datetime import date

class Diario(models.Model):
	codigo = models.CharField(max_length=50)
	fecha = models.CharField(max_length=50)

class Registro_Mineria(models.Model):
    diario = models.ForeignKey(Diario)
    boletin = models.CharField(max_length=200,null=True,blank=True)
    f_boletin = models.CharField(max_length=200,null=True,blank=True)
    tipo_conce = models.CharField(max_length=200)
    concesion = models.CharField(max_length=200,null=True,blank=True)
    concesiona = models.CharField(max_length=200,null=True,blank=True)
    representa = models.CharField(max_length=200,null=True,blank=True)
    direccion = models.CharField(max_length=200,null=True,blank=True)
    rolminero = models.CharField(max_length=200,null=True,blank=True)
    f_sentenc1 = models.CharField(max_length=200,null=True,blank=True)
    f_sentenc2 = models.CharField(max_length=200,null=True,blank=True)
    f_pubext = models.CharField(max_length=200,null=True,blank=True)
    f_inscmin = models.CharField(max_length=200,null=True,blank=True)
    fojas = models.CharField(max_length=200,null=True,blank=True)
    numero = models.CharField(max_length=200,null=True,blank=True)
    year = models.CharField(max_length=200,null=True,blank=True)
    ciudad = models.CharField(max_length=200,null=True,blank=True)
    juzgado = models.CharField(max_length=200,null=True,blank=True)
    roljuz = models.CharField(max_length=200,null=True,blank=True)
    ind_metal = models.CharField(max_length=200,null=True,blank=True)
    region = models.CharField(max_length=200,null=True,blank=True)
    provincia = models.CharField(max_length=200,null=True,blank=True)
    comuna = models.CharField(max_length=200,null=True,blank=True)
    lugar = models.CharField(max_length=200,null=True,blank=True)
    tipo_utm = models.CharField(max_length=200,null=True,blank=True)
    nortepi = models.CharField(max_length=200,null=True,blank=True)
    estepi = models.CharField(max_length=200,null=True,blank=True)
    vertices = models.CharField(max_length=200,null=True,blank=True)
    ha_pert = models.CharField(max_length=200,null=True,blank=True)
    hectareas = models.CharField(max_length=200,null=True,blank=True)
    obser = models.CharField(max_length=200,null=True,blank=True)
    datum = models.CharField(max_length=200,null=True,blank=True)
    f_prestrib = models.CharField(max_length=200,null=True,blank=True)
    archivo = models.CharField(max_length=200,null=True,blank=True)
    corte = models.CharField(max_length=200,null=True,blank=True)
    huso = models.CharField(max_length=200,null=True,blank=True)
    editor = models.CharField(max_length=200,null=True,blank=True)
    tipo_tramite = models.CharField(max_length=200,null=True,blank=True)
    cve = models.CharField(max_length=200)
    texto = models.TextField(max_length=100000,null=True,blank=True)
    url = models.CharField(max_length=254,null=True,blank=True)
    def __str__(self):
        return self.tipo_tramite + " - " + self.cve

class Vertice(models.Model):
    registro_mineria = models.ForeignKey(Registro_Mineria)
    boletin = models.CharField(max_length=254,null=True,blank=True)
    f_boletin = models.CharField(max_length=254,null=True,blank=True)
    concesion = models.CharField(max_length=254,null=True,blank=True)
    region = models.CharField(max_length=254,null=True,blank=True)
    roljuz = models.CharField(max_length=254,null=True,blank=True)
    ident_lind = models.CharField(max_length=254,null=True,blank=True)
    coordnorte = models.CharField(max_length=254,null=True,blank=True)
    coordeste = models.CharField(max_length=254,null=True,blank=True)