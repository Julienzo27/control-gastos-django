from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoriaForm, GastoForm
from .models import Gasto


def lista_gastos(request):
    gastos = Gasto.objects.select_related("categoria").order_by("-fecha")
    total = gastos.aggregate(total=Sum("monto"))["total"] or 0
    totales_por_categoria = (
        Gasto.objects.values("categoria__nombre")
        .annotate(total=Sum("monto"))
        .order_by("-total")
    )
    return render(request, "gastos/lista.html", {
        "gastos": gastos,
        "total": total,
        "totales_por_categoria": totales_por_categoria,
    })


def agregar_gasto(request):
    if request.method == "POST":
        form = GastoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_gastos")
    else:
        form = GastoForm()
    return render(request, "gastos/formulario.html", {"form": form})



def agregar_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("agregar_gasto")
    else:
        form = CategoriaForm()
    return render(
        request,
        "gastos/formulario.html",
        {"form": form, "titulo": "Nueva categoría"},
    )


def editar_gasto(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == "POST":
        form = GastoForm(request.POST, instance=gasto)
        if form.is_valid():
            form.save()
            return redirect("lista_gastos")
    else:
        form = GastoForm(instance=gasto)
    return render(
        request,
        "gastos/formulario.html",
        {"form": form, "titulo": "Editar gasto"},
    )


def eliminar_gasto(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == "POST":
        gasto.delete()
        return redirect("lista_gastos")
    return render(request, "gastos/confirmar_eliminar.html", {"gasto": gasto})
