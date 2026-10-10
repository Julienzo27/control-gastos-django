from django.contrib import admin

from .models import Categoria, Gasto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ("descripcion", "monto", "fecha", "categoria")
    list_filter = ("categoria", "fecha")

# Register your models here.
