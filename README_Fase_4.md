# Fase 4 – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Curso: Programación 213023 – UNAD

## Descripción
Aplicación didáctica en Python para la empresa ficticia Software FJ. Administra clientes, servicios de sala, equipo y asesoría, y reservas mediante listas en memoria. No utiliza bases de datos.

## Requisitos
Python 3.10 o posterior. Tkinter suele incluirse con Python; en algunas instalaciones de Linux debe instalarse aparte. No requiere bibliotecas externas.

## Ejecución
Interfaz gráfica:
```bash
python Fase4_Software_FJ.py
```
Simulación de 17 casos:
```bash
python Fase4_Software_FJ.py --demo
```

## Diseño
- `Entidad`: clase abstracta.
- `Cliente`: encapsulación y validaciones.
- `Servicio`: clase abstracta con `Sala`, `Equipo` y `Asesoria`.
- `Reserva`: procesamiento, confirmación y cancelación.
- `SistemaFJ`: colecciones de clientes, servicios y reservas.
- `InterfazFJ`: interfaz Tkinter.

El código incluye excepciones personalizadas, registros de errores en `software_fj.log` y parámetros opcionales para cálculos de costos. En Python la sobrecarga de métodos se simula con parámetros opcionales, no mediante varias firmas del mismo método.

## Pruebas
La opción `--demo` ejecuta 17 operaciones válidas e inválidas y comunica sus resultados. Se recomienda ejecutar también la interfaz manualmente antes de entregar.

## Entrega
Subir el proyecto al repositorio del grupo, revisar el funcionamiento entre los cinco integrantes y compartir el enlace en el foro. El informe grupal PDF debe incluir portada, introducción, enlace real al repositorio, conclusiones y referencias APA.

**Importante:** los datos se pierden al cerrar la aplicación. Los archivos solo se usan para registrar eventos y errores, de acuerdo con el anexo.
