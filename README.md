# MedAssist Pro v2.0

Sistema de apoyo al diagnóstico clínico con inteligencia artificial, diseñado para profesionales médicos.

## Características

- Login seguro por DNI y contraseña con panel de administrador
- Registro de historia clínica (signos vitales, antecedentes, síntomas)
- Análisis clínico asistido por IA (Google Gemini)
- Gestión de cuentas médicas por el administrador
- Generación e impresión de orden médica

## Credenciales por defecto (cambiar en producción)

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| Administrador | `admin` | `Admin2026!` |

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app_medica.py
```

## Configuración de secretos (local)

Crear el archivo `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "tu_clave_api_aqui"
```

## Deploy en Streamlit Community Cloud

1. Subir este repositorio a GitHub
2. Ir a share.streamlit.io
3. Conectar con GitHub y seleccionar este repositorio
4. En "Advanced settings > Secrets" agregar: `GEMINI_API_KEY = "tu_clave"`
5. Hacer clic en Deploy

## Nota importante sobre datos

Los datos de pacientes se guardan en una base de datos SQLite local.
Este archivo NO se sube a GitHub por seguridad.

> Uso exclusivo profesional medico. El diagnostico final es responsabilidad del medico tratante.
