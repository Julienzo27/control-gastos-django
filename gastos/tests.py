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



class DuplicadosTests(TestCase):
    def setUp(self):
        self.casa = Categoria.objects.create(nombre="Casa")
        Gasto.objects.create(
            descripcion="Metrogas",
            monto=Decimal("5000"),
            fecha=date(2026, 10, 3),
            categoria=self.casa,
        )

    def datos(self, **cambios):
        datos = {
            "descripcion": "Metrogas",
            "monto": "5000",
            "fecha": "2026-10-20",
            "categoria": self.casa.id,
        }
        datos.update(cambios)
        return datos

    def test_gasto_duplicado_en_el_mismo_mes_se_advierte(self):
        respuesta = self.client.post(reverse("agregar_gasto"), self.datos())
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "ya existe un gasto")
        self.assertEqual(Gasto.objects.count(), 1)

    def test_gasto_duplicado_se_carga_si_se_confirma(self):
        self.client.post(
            reverse("agregar_gasto"), self.datos(confirmar_duplicado="on")
        )
        self.assertEqual(Gasto.objects.count(), 2)

    def test_mismo_gasto_en_otro_mes_no_es_duplicado(self):
        self.client.post(reverse("agregar_gasto"), self.datos(fecha="2026-11-03"))
        self.assertEqual(Gasto.objects.count(), 2)

    def test_categoria_nueva_se_crea(self):
        respuesta = self.client.post(reverse("agregar_categoria"), {"nombre": "Salud"})
        self.assertRedirects(respuesta, reverse("agregar_gasto"))
        self.assertTrue(Categoria.objects.filter(nombre="Salud").exists())

    def test_categoria_repetida_se_advierte_sin_importar_mayusculas(self):
        respuesta = self.client.post(reverse("agregar_categoria"), {"nombre": "casa"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "ya existe")
        self.assertEqual(Categoria.objects.count(), 1)


class EditarEliminarTests(TestCase):
    def setUp(self):
        self.casa = Categoria.objects.create(nombre="Casa")
        self.gasto = Gasto.objects.create(
            descripcion="Luz",
            monto=Decimal("100"),
            fecha=date(2026, 10, 1),
            categoria=self.casa,
        )

    def datos(self, **cambios):
        datos = {
            "descripcion": "Luz",
            "monto": "100",
            "fecha": "2026-10-01",
            "categoria": self.casa.id,
        }
        datos.update(cambios)
        return datos

    def test_editar_gasto(self):
        url = reverse("editar_gasto", args=[self.gasto.pk])
        respuesta = self.client.post(url, self.datos(descripcion="Luz Edesur", monto="150"))
        self.assertRedirects(respuesta, reverse("lista_gastos"))
        self.gasto.refresh_from_db()
        self.assertEqual(self.gasto.descripcion, "Luz Edesur")
        self.assertEqual(self.gasto.monto, Decimal("150"))

    def test_editar_sin_cambios_no_se_cuenta_como_duplicado_de_si_mismo(self):
        url = reverse("editar_gasto", args=[self.gasto.pk])
        respuesta = self.client.post(url, self.datos())
        self.assertRedirects(respuesta, reverse("lista_gastos"))
        self.assertEqual(Gasto.objects.count(), 1)

    def test_eliminar_pide_confirmacion_y_no_borra_con_get(self):
        respuesta = self.client.get(reverse("eliminar_gasto", args=[self.gasto.pk]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Luz")
        self.assertEqual(Gasto.objects.count(), 1)

    def test_eliminar_gasto(self):
        respuesta = self.client.post(reverse("eliminar_gasto", args=[self.gasto.pk]))
        self.assertRedirects(respuesta, reverse("lista_gastos"))
        self.assertEqual(Gasto.objects.count(), 0)

    def test_editar_gasto_inexistente_da_404(self):
        respuesta = self.client.get(reverse("editar_gasto", args=[9999]))
        self.assertEqual(respuesta.status_code, 404)


class FiltrosTests(TestCase):
    def setUp(self):
        self.casa = Categoria.objects.create(nombre="Casa")
        self.ringo = Categoria.objects.create(nombre="Ringo")
        Gasto.objects.create(descripcion="Alquiler", monto=Decimal("1000"), fecha=date(2026, 9, 5), categoria=self.casa)
        Gasto.objects.create(descripcion="Luz", monto=Decimal("200"), fecha=date(2026, 10, 5), categoria=self.casa)
        Gasto.objects.create(descripcion="Veterinario", monto=Decimal("300"), fecha=date(2026, 10, 8), categoria=self.ringo)

    def test_sin_filtros_muestra_todo(self):
        respuesta = self.client.get(reverse("lista_gastos"))
        self.assertContains(respuesta, "Alquiler")
        self.assertContains(respuesta, "Luz")
        self.assertContains(respuesta, "Veterinario")

    def test_filtrar_por_mes(self):
        respuesta = self.client.get(reverse("lista_gastos"), {"mes": "2026-10"})
        self.assertContains(respuesta, "Luz")
        self.assertContains(respuesta, "Veterinario")
        self.assertNotContains(respuesta, "Alquiler")

    def test_filtrar_por_categoria(self):
        respuesta = self.client.get(reverse("lista_gastos"), {"categoria": self.ringo.id})
        self.assertContains(respuesta, "Veterinario")
        self.assertNotContains(respuesta, "Luz")

    def test_filtrar_por_mes_y_categoria(self):
        respuesta = self.client.get(
            reverse("lista_gastos"), {"mes": "2026-10", "categoria": self.casa.id}
        )
        self.assertContains(respuesta, "Luz")
        self.assertNotContains(respuesta, "Veterinario")
        self.assertNotContains(respuesta, "Alquiler")

    def test_el_total_respeta_el_filtro(self):
        respuesta = self.client.get(reverse("lista_gastos"), {"mes": "2026-10"})
        self.assertEqual(respuesta.context["total"], Decimal("500"))

    def test_filtros_invalidos_se_ignoran(self):
        respuesta = self.client.get(
            reverse("lista_gastos"), {"mes": "abc", "categoria": "x"}
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Alquiler")