from django import forms

from .models import Categoria, Gasto


class GastoForm(forms.ModelForm):
    confirmar_duplicado = forms.BooleanField(
        required=False,
        label="Cargar igual aunque ya exista uno parecido",
    )

    class Meta:
        model = Gasto
        fields = ["descripcion", "monto", "fecha", "categoria"]
        widgets = {
            "descripcion": forms.TextInput(attrs={"autocomplete": "off"}),
            "fecha": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def clean(self):
        datos = super().clean()
        descripcion = datos.get("descripcion")
        monto = datos.get("monto")
        fecha = datos.get("fecha")
        categoria = datos.get("categoria")

        if descripcion and monto is not None and fecha and categoria:
            parecidos = Gasto.objects.filter(
                descripcion__iexact=descripcion.strip(),
                monto=monto,
                categoria=categoria,
                fecha__year=fecha.year,
                fecha__month=fecha.month,
            )
            if self.instance.pk:
                parecidos = parecidos.exclude(pk=self.instance.pk)
            if parecidos.exists() and not datos.get("confirmar_duplicado"):
                raise forms.ValidationError(
                    "Atención: ya existe un gasto igual (misma descripción, monto "
                    "y categoría en ese mes). Si realmente querés cargarlo otra vez, "
                    "tildá la casilla de abajo y guardá."
                )
        return datos


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre"]

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError(
                f"La categoría «{nombre}» ya existe. Elegila de la lista al cargar un gasto."
            )
        return nombre