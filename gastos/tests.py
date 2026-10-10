from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Gasto


class ModelosTests(TestCase):
    def setUp(self):
        self.casa = Categoria.objects.create(nombre="Casa")
        self.comida = Categoria.objects.create(nombre="Comida")

    def test_str_de_categoria(self):
        self.assertEqual(str(self.casa), "Casa")

    def test_str_de_gasto(self):
        gasto = Gasto.objects.create(
            descripcion="Alquiler",
            monto=Decimal("1000.50"),
            fecha=date(2026, 10, 1),
            categoria=self.casa,
        )
        self.assertEqual(str(gasto), "Alquiler - $1000.50")

    def test_total_por_categoria(self):
        Gasto.objects.create(descripcion="Luz", monto=Decimal("100"), fecha=date(2026, 10, 1), categoria=self.casa)
        Gasto.objects.create(descripcion="Gas", monto=Decimal("50"), fecha=date(2026, 10, 2), categoria=self.casa)
        Gasto.objects.create(descripcion="Pizza", monto=Decimal("30"), fecha=date(2026, 10, 3), categoria=self.comida)

        total_casa = Gasto.objects.filter(categoria=self.casa).aggregate(total=Sum("monto"))["total"]
        self.assertEqual(total_casa, Decimal("150"))

    def test_no_se_puede_borrar_categoria_con_gastos(self):
        from django.db.models import ProtectedError

        Gasto.objects.create(descripcion="Luz", monto=Decimal("100"), fecha=date(2026, 10, 1), categoria=self.casa)
        with self.assertRaises(ProtectedError):
            self.casa.delete()


class VistasTests(TestCase):
    def setUp(self):
        self.casa = Categoria.objects.create(nombre="Casa")

    def test_lista_responde_200_y_muestra_gastos(self):
        Gasto.objects.create(descripcion="Expensas", monto=Decimal("500"), fecha=date(2026, 10, 1), categoria=self.casa)
        respuesta = self.client.get(reverse("lista_gastos"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Expensas")

    def test_formulario_se_muestra(self):
        respuesta = self.client.get(reverse("agregar_gasto"))
        self.assertEqual(respuesta.status_code, 200)

    def test_agregar_gasto_crea_registro_y_redirige(self):
        respuesta = self.client.post(
            reverse("agregar_gasto"),
            {
                "descripcion": "Internet",
                "monto": "300.00",
                "fecha": "2026-10-05",
                "categoria": self.casa.id,
            },
        )
        self.assertRedirects(respuesta, reverse("lista_gastos"))
        self.assertEqual(Gasto.objects.count(), 1)
        self.assertEqual(Gasto.objects.first().descripcion, "Internet")

    def test_agregar_gasto_invalido_no_crea_nada(self):
        respuesta = self.client.post(
            reverse("agregar_gasto"),
            {"descripcion": "", "monto": "abc", "fecha": "", "categoria": ""},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Gasto.objects.count(), 0)