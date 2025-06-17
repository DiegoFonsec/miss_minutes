**CSRGenerator** es una herramienta modular diseñada como parte de la suite **DP Tools**, - description - .

---

## 🔧 Características

- soon

---

## 📦 Requisitos

- Python >= 3.8
- Django >= 4.x
- Wagtail >= 5.x
- Instalar librería adicional:

```bash
pip install pyOpenSSL
pip install markdown
```

---

## 🚀 Instalación

1. **Ubicación sugerida**: dentro de tu carpeta `apps/` en el proyecto Wagtail.

2. **Agregar a `INSTALLED_APPS`** en tu `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'wagtail_dp_tools.csrgenerator',
]
```

3. **Aplicar migraciones**:

```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Iniciar el servidor** y acceder a `/admin/`

```bash
python manage.py runserver
```

Verás la sección **DP Tools > CSRGenerator** en el panel de navegación.

---

¡Gracias por usar DP Tools – CSRGenerator! 🎉
