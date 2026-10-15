from django.contrib import admin
from .models import Juego, Resena

@admin.register(Juego)
class JuegoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "plataforma", "anio_lanzamiento")
    list_filter = ("plataforma", "anio_lanzamiento")
    search_fields = ("titulo", "descripcion")


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ("juego", "usuario", "calificacion", "fecha_creacion")
    list_filter = ("calificacion", "fecha_creacion")
    search_fields = ("juego__titulo", "usuario__username", "contenido")
