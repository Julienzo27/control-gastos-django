from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoriaForm, GastoForm
from .models import Categoria, Gasto

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def lista_gastos(request):
    mes = request.GET.get("mes", "")
    categoria_id = request.GET.get("categoria", "")

    gastos = Gasto.objects.select_related("categoria").order_by("-fecha")

    if mes:
        try:
            anio, numero = mes.split("-")
            gastos = gastos.filter(fecha__year=int(anio), fecha__month=int(numero))
        except ValueError:
            mes = ""

    if categoria_id.isdigit():
        gastos = gastos.filter(categoria_id=int(categoria_id))
    else:
        categoria_id = ""

    total = gastos.aggregate(total=Sum("monto"))["total"] or 0
    totales_por_categoria = (
        gastos.values("categoria__nombre")
        .annotate(total=Sum("monto"))
        .order_by("-total")
    )

    meses = [
        {
            "valor": fecha.strftime("%Y-%m"),
            "texto": f"{MESES[fecha.month - 1].capitalize()} {fecha.year}",
        }
        for fecha in Gasto.objects.dates("fecha", "month", order="DESC")
    ]

    return render(
        request,
        "gastos/lista.html",
        {
            "gastos": gastos,
            "total": total,
            "totales_por_categoria": totales_por_categoria,
            "meses": meses,
            "categorias": Categoria.objects.order_by("nombre"),
            "mes_sel": mes,
            "categoria_sel": categoria_id,
            "filtrando": bool(mes or categoria_id),
        },
    )


def agregar_gasto(request):
    if request.method == "POST":
        form = GastoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_gastos")
    else:
        form = GastoForm()
    return render(request, "gastos/formulario.html", {"form": form})


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