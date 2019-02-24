"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import core.views as views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', views.index, name="index"),
    url(r'^descargar_boletin/', views.descargar_boletin, name="descargar_boletin"),
    url(r'^Historic_Data/', views.Historic_Data, name="Historic_Data"),
    url(r'^Obtener_Datos_General/', views.Obtener_Datos_General, name="Obtener_Datos_General"),
    url(r'^get_datos/', views.get_datos, name="get_datos"),
    url(r'^actualizar_datos/', views.actualizar_datos, name="actualizar_datos"),
    url(r'^ingresar_vertices/', views.ingresar_vertices, name="ingresar_vertices"),
    url(r'^excel_registros/', views.excel_registros, name="excel_registros"),
    url(r'^excel_vertices/', views.excel_vertices, name="excel_vertices"),
    url(r'^create_database_tst/', views.create_database_tst, name="create_database_tst"),
    url(r'^$', views.login_user, name="login"),
]
