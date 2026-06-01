# Lumiere Glamour

Proyecto web de tienda virtual desarrollado con Django. Permite publicar productos de maquillaje, organizarlos por categorias, mostrar anuncios, gestionar favoritos por sesion y preparar pedidos por WhatsApp.

## Tecnologias principales

- Python 3.13
- Django
- SQLite para desarrollo local
- PostgreSQL opcional mediante `DATABASE_URL`
- Cloudinary para almacenamiento de imagenes
- Tailwind CSS para estilos compilados
- WhiteNoise para servir archivos estaticos

## Estructura del proyecto

```text
lumiere_glamour/     Configuracion principal de Django
store/               Aplicacion de tienda, modelos, vistas, URLs y plantillas
static/              Archivos CSS, JavaScript e imagenes estaticas
media/               Archivos locales usados durante desarrollo
manage.py            Comando administrativo de Django
requirements.txt     Dependencias de Python
package.json         Dependencias y scripts del frontend
```

## Variables de entorno

El proyecto carga variables desde `.env` si el archivo existe en la raiz.

```env
SECRET_KEY=clave-secreta-de-django
DEBUG=True
DATABASE_URL=
DB_SSL_REQUIRED=False
CLOUDINARY_CLOUD_NAME=nombre-cloudinary
CLOUDINARY_API_KEY=api-key-cloudinary
CLOUDINARY_API_SECRET=api-secret-cloudinary
WHATSAPP_NUMBER=573007221200
```

`DATABASE_URL` es opcional en desarrollo. Si `DEBUG=False`, debe configurarse una base de datos o usar temporalmente `SKIP_DB_CHECK=1` para comandos que no requieran conexion real.

## Instalacion local

1. Crear y activar el entorno virtual.

```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Instalar dependencias de Python.

```powershell
pip install -r requirements.txt
```

3. Instalar dependencias del frontend.

```powershell
npm install
```

4. Ejecutar migraciones.

```powershell
python manage.py migrate
```

5. Compilar estilos.

```powershell
npm run build
```

6. Iniciar el servidor local.

```powershell
python manage.py runserver
```

## Funcionalidades principales

- Catalogo de productos activos con paginacion.
- Filtro por categoria, subcategoria y etiqueta comercial.
- Busqueda en vivo de productos.
- Favoritos guardados por sesion y sincronizados con el navegador.
- Carrito en el navegador con compra por WhatsApp.
- Panel de administracion para productos, categorias, anuncios y configuraciones.
- Imagenes de productos, categorias y anuncios almacenadas en Cloudinary.

## Despliegue

El proyecto no incluye configuraciones amarradas a proveedores concretos. Para subirlo a un servidor, configura las variables de entorno, ejecuta migraciones, compila los estaticos y levanta la aplicacion con un servidor WSGI compatible con Django.

Cloudinary debe permanecer configurado para que las imagenes funcionen correctamente en produccion.
