# -*- coding: utf-8 -*-
from django.conf import settings
from core.models import *
from django.db.models.signals import pre_save
from django.dispatch import receiver
import pdb
import unidecode
import re
import traceback
from django.utils.dateparse import parse_date

@receiver(pre_save, sender=Diario)
def diario_pre_save_handler(sender, instance, **kwargs):
  fields_to_validate = ['fecha']
  pre_validation_loop(instance, fields_to_validate)

@receiver(pre_save, sender=Registro_Mineria)
def registro_mineria_pre_save_handler(sender, instance, **kwargs):
  fields_to_validate = [
    'f_boletin',
    'f_sentenc1',
    'f_sentenc2',
    'f_pubext',
    'f_inscmin',
    'f_prestrib',
    'f_presenta',
    'f_resoluci',
    'f_inscribe',
    'f_solicita',
    'f_presman',
    'f_mensura'
  ]
  pre_validation_loop(instance, fields_to_validate)

@receiver(pre_save, sender=Vertice)
def vertice_pre_save_handler(sender, instance, **kwargs):
  fields_to_validate = ['f_boletin']
  pre_validation_loop(instance, fields_to_validate)

def pre_validation_loop(instance, fields_to_validate):
  for field in fields_to_validate:
    field_data = getattr(instance, field)
    if field_data != "" and field_data != None:
      if date_validation(field_data):
        return True
      else:
        raise Exception('Fecha inválida')

def date_validation(this_date):
  try:
    parse_date(this_date)
    return True
  except Exception as e:
    trace_back = traceback.format_exc()
    message = str(e)+ " " + str(trace_back)
    print message
    return False