# Skinautica Bsale Power BI

Este proyecto permite conectar los datos de Bsale a Power BI mediante scripts en Python. El objetivo es automatizar la descarga de documentos (boletas, facturas, notas de crédito, etc.) y preparar los datos para su análisis y visualización en Power BI, con foco en la operación de Skinautica.

## 📁 Estructura del Proyecto

- **scripts/**: scripts Python que se conectan a la API de Bsale.
- **data/**: archivos generados (.csv) listos para importar en Power BI.
- **config/.env**: credencial del token de Bsale (excluida del repo).
- **requirements.txt**: librerías requeridas para ejecutar el proyecto.
- **main.py**: orquestador general (opcional).
- **README.md**: este archivo de documentación.

## 🚀 Requisitos

- Python 3.8 o superior
- Cuenta activa en Bsale con acceso a la API REST
- Token de acceso (`access_token`) generado desde Bsale
- Git instalado (para sincronización con GitHub)

## 🔧 Instalación

1. Clonar el repositorio:

   ```
   git clone https://github.com/tuusuario/skinautica-bsale-powerbi.git
   ```

2. Crear un entorno virtual:

   ```
   cd skinautica-bsale-powerbi  
   python -m venv venv  
   venv\Scripts\activate (Windows)  
   source venv/bin/activate (Mac/Linux)
   ```

3. Instalar dependencias:

   ```
   pip install -r requirements.txt
   ```

4. Crear archivo `.env` dentro de la carpeta `config/` con el siguiente contenido:

   ```
   BSALE_ACCESS_TOKEN=tu_token_aqui
   ```

## 📤 Uso

Para descargar los documentos de la semana pasada desde Bsale:

   ```
   python scripts/download_documents.py
   ```

Esto generará un archivo en:

   ```
   data/documentos/documentos_semana_pasada.csv
   ```

El archivo puede ser cargado directamente en Power BI para análisis.

## 🧭 Próximos pasos

- Agregar descarga de detalles por documento
- Incorporar pagos, clientes, stock e impuestos
- Automatizar el proceso con tareas programadas
- Conectar archivos directamente a Power BI Desktop o Power BI Service

## 👤 Autor

**Cristóbal Elton**  
Gerente Comercial — Skinautica
