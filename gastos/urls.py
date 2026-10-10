from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista_gastos, name="lista_gastos"),
    path("agregar/", views.agregar_gasto, name="agregar_gasto"),
]