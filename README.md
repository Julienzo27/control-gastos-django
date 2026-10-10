\# Control de gastos personales



App web hecha con Django para registrar gastos y ver cuánto se gasta por categoría.



\## Qué hace



\- Registra gastos con descripción, monto, fecha y categoría.

\- Muestra la lista de gastos ordenada por fecha (del más nuevo al más viejo).

\- Calcula el total general y el total por categoría.

\- Panel de administración de Django para gestionar categorías y gastos.



\## Tecnologías



Python, Django 6.1, SQLite, HTML.



\## Cómo probarlo



Requiere Python 3.12 o superior.



&#x20;   python -m venv .venv

&#x20;   .venv\\Scripts\\Activate.ps1

&#x20;   pip install -r requirements.txt

&#x20;   python manage.py migrate

&#x20;   python manage.py createsuperuser

&#x20;   python manage.py runserver



Después abrí http://127.0.0.1:8000/admin/ para crear categorías y entrá a http://127.0.0.1:8000/ para ver la lista y agregar gastos.



\## Tests



&#x20;   python manage.py test



\## Ideas para seguir



\- Filtrar gastos por mes y por categoría.

\- Editar y borrar gastos desde la página.

\- Gráfico de gastos por categoría.

\- Agregar usuarios para que cada persona vea solo sus gastos.

