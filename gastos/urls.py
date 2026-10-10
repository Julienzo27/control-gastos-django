from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista_gastos, name="lista_gastos"),
    path("agregar/", views.agregar_gasto, name="agregar_gasto"),
    path("gasto/<int:pk>/editar/", views.editar_gasto, name="editar_gasto"),
    path("gasto/<int:pk>/eliminar/", views.eliminar_gasto, name="eliminar_gasto"),
    path("categorias/nueva/", views.agregar_categoria, name="agregar_categoria"),
]