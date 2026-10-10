from django import forms

from .models import Gasto


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ["descripcion", "monto", "fecha", "categoria"]
        widgets = {"fecha": forms.DateInput(attrs={"type": "date"})}