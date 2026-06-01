import json
from decimal import Decimal

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from .models import (
    Anuncio,
    Categoria,
    Favorito,
    MenuItem,
    Producto,
    SiteSetting,
    Variacion,
)


def google_verification(request):
    return HttpResponse(
        "google-site-verification: google1e60e56990e838db.html",
        content_type="text/plain",
    )


def format_precio(precio):
    """Devuelve un precio en formato de pesos colombianos."""
    if precio is None or precio == "":
        return "$ 0"

    if not isinstance(precio, (int, float, Decimal)):
        try:
            precio = float(precio)
        except (ValueError, TypeError):
            return "$ 0"

    return f"$ {'{:,.0f}'.format(precio).replace(',', '.')}"


def get_site_setting(key, default=""):
    value = SiteSetting.objects.filter(key=key).values_list("value", flat=True).first()
    return value or default


def get_common_context(request):
    """Construye los datos compartidos por las vistas publicas de la tienda."""
    if not request.session.session_key:
        request.session.save()

    favoritos_ids = set(
        Favorito.objects.filter(session_key=request.session.session_key).values_list(
            "producto_id", flat=True
        )
    )

    return {
        "favoritos_ids": favoritos_ids,
        "categorias_principales": Categoria.objects.filter(padre__isnull=True),
        "menu_items": MenuItem.objects.all().order_by("order"),
        "whatsapp_number": get_site_setting(
            "whatsapp_number", getattr(settings, "WHATSAPP_NUMBER", "573007221200")
        ),
    }


def api_buscar_productos(request):
    """Retorna productos activos para la busqueda en vivo del encabezado."""
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse(
            {
                "productos": [],
                "mensaje": "La busqueda debe tener al menos 2 caracteres.",
            }
        )

    productos = Producto.objects.filter(
        Q(nombre__icontains=query)
        | Q(descripcion__icontains=query)
        | Q(categoria__nombre__icontains=query),
        is_active=True,
    ).distinct()[:8]

    resultados = [
        {
            "id": producto.id,
            "nombre": producto.nombre,
            "precio": format_precio(producto.get_precio_final()),
            "imagen": producto.get_primary_image_url(),
            "url": f"/producto/{producto.id}/",
            "categoria": producto.categoria.nombre if producto.categoria else "",
            "descuento": bool(producto.descuento),
        }
        for producto in productos
    ]

    return JsonResponse({"exito": True, "productos": resultados, "total": len(resultados)})


def inicio(request):
    """Muestra el catalogo principal con busqueda, filtros, anuncios y paginacion."""
    query = request.GET.get("q")
    categoria_id = request.GET.get("categoria")
    subcategoria_id = request.GET.get("subcategoria")
    ofertas_activas = request.GET.get("ofertas")
    page = request.GET.get("page", 1)

    productos_queryset = Producto.objects.filter(is_active=True)
    nombre_categoria_actual = None
    categoria_actual_obj = None

    if ofertas_activas == "true":
        productos_queryset = productos_queryset.filter(descuento__gt=0)
        nombre_categoria_actual = "Ofertas Especiales"

    if query:
        productos_queryset = productos_queryset.filter(
            Q(nombre__icontains=query)
            | Q(descripcion__icontains=query)
            | Q(categoria__nombre__icontains=query)
        ).distinct()

    if categoria_id:
        try:
            categoria_actual_obj = Categoria.objects.get(id=categoria_id)
            productos_queryset = productos_queryset.filter(categoria=categoria_actual_obj)
            nombre_categoria_actual = categoria_actual_obj.nombre
        except Categoria.DoesNotExist:
            pass

    if subcategoria_id:
        try:
            subcategoria_actual_obj = Categoria.objects.get(id=subcategoria_id)
            productos_queryset = productos_queryset.filter(
                Q(categoria=subcategoria_actual_obj)
                | Q(categoria__padre=subcategoria_actual_obj)
            ).distinct()
            nombre_categoria_actual = subcategoria_actual_obj.nombre
            if subcategoria_actual_obj.padre:
                categoria_actual_obj = subcategoria_actual_obj.padre
        except Categoria.DoesNotExist:
            pass

    paginator = Paginator(productos_queryset, 12)
    try:
        productos_paginados = paginator.page(page)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)

    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key

    favoritos = set(
        Favorito.objects.filter(session_key=session_key).values_list("producto_id", flat=True)
    )

    productos_procesados = [
        {
            "id": producto.id,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "precio": format_precio(producto.precio),
            "descuento": format_precio(producto.descuento) if producto.descuento else "0",
            "get_precio_final": format_precio(producto.get_precio_final()),
            "imagen": producto.get_primary_image_url(),
            "is_favorito": producto.id in favoritos,
        }
        for producto in productos_paginados
    ]

    params = request.GET.copy()
    params.pop("page", None)

    context = get_common_context(request)
    context.update(
        {
            "productos": productos_procesados,
            "pagina_productos": productos_paginados,
            "query": query or "",
            "categoria_actual": categoria_actual_obj.id if categoria_actual_obj else None,
            "nombre_categoria_actual": nombre_categoria_actual or "Todos los productos",
            "ofertas_activas": ofertas_activas == "true",
            "anuncios": Anuncio.objects.filter(is_active=True).order_by("order"),
            "favoritos": list(favoritos),
            "extra_query": ("&" + params.urlencode()) if params else "",
            "active_page": "inicio",
        }
    )

    return render(request, "store/index.html", context)


def productos_por_categoria(request, slug):
    """Muestra los productos de una categoria y de todas sus subcategorias."""
    categoria_actual = get_object_or_404(Categoria, slug=slug)
    categorias_a_incluir = [categoria_actual]

    def get_all_subcategories(category, visited=None):
        visited = visited or set()
        subcategories = []
        for subcategory in category.subcategorias.all():
            if subcategory.id not in visited:
                visited.add(subcategory.id)
                subcategories.append(subcategory)
                subcategories.extend(get_all_subcategories(subcategory, visited))
        return subcategories

    categorias_a_incluir.extend(get_all_subcategories(categoria_actual))

    productos_queryset = Producto.objects.filter(
        categoria__in=categorias_a_incluir, is_active=True
    ).order_by("-fecha_creacion")

    paginator = Paginator(productos_queryset, 12)
    page = request.GET.get("page", 1)
    try:
        productos_paginados = paginator.page(page)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)

    params = request.GET.copy()
    params.pop("page", None)

    context = get_common_context(request)
    context.update(
        {
            "categoria": categoria_actual,
            "productos": productos_paginados.object_list,
            "pagina_productos": productos_paginados,
            "nombre_categoria_actual": categoria_actual.nombre,
            "active_page": categoria_actual.slug,
            "extra_query": ("&" + params.urlencode()) if params else "",
        }
    )

    return render(request, "store/categoria.html", context)


def producto_detalle(request, pk):
    """Muestra la informacion completa de un producto."""
    producto = get_object_or_404(Producto, pk=pk)
    common_context = get_common_context(request)

    context = {
        "producto": producto,
        "is_favorito": producto.id in common_context["favoritos_ids"],
        "variaciones": [
            {
                "id": variacion.id,
                "nombre": variacion.nombre,
                "valor": variacion.valor,
                "color": variacion.color,
                "tono": variacion.tono,
                "color_hex": variacion.color_hex,
                "imagen": variacion.imagen.url if variacion.imagen else "",
                "precio_formateado": format_precio(variacion.precio_final),
                "precio_final": variacion.precio_final,
            }
            for variacion in producto.variaciones.all()
        ],
    }
    context.update(common_context)

    return render(request, "store/producto.html", context)


@csrf_exempt
def toggle_favorito(request):
    """Agrega o elimina un producto de favoritos usando la sesion anonima."""
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    try:
        data = json.loads(request.body)
        producto_id = data.get("producto_id")
        if not producto_id:
            return JsonResponse({"error": "ID de producto no proporcionado"}, status=400)

        if not request.session.session_key:
            request.session.save()

        favorito, created = Favorito.objects.get_or_create(
            session_key=request.session.session_key, producto_id=producto_id
        )

        if not created:
            favorito.delete()
            return JsonResponse(
                {
                    "success": True,
                    "mensaje": "Producto eliminado de favoritos",
                    "is_favorito": False,
                }
            )

        return JsonResponse(
            {
                "success": True,
                "mensaje": "Producto anadido a favoritos",
                "is_favorito": True,
            }
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Formato JSON invalido"}, status=400)


@csrf_exempt
def agregar_al_carrito(request):
    """Agrega productos o variaciones al carrito almacenado en la sesion."""
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    try:
        data = json.loads(request.body)
        producto_id = data.get("producto_id")
        quantity = int(data.get("quantity", 1))
        variant_id = data.get("variant_id")
        color = data.get("color")

        producto = get_object_or_404(Producto, id=producto_id)
        variante = None
        if variant_id and str(variant_id) != str(producto_id):
            variante = get_object_or_404(Variacion, id=variant_id, producto=producto)

        item_to_add = {
            "id": producto.id,
            "name": producto.nombre,
            "price": float(variante.precio_final if variante else producto.get_precio_final()),
            "quantity": quantity,
            "variant_id": variante.id if variante else producto.id,
            "color": variante.color if variante else color,
            "imageUrl": (
                variante.imagen.url
                if variante and variante.imagen
                else producto.get_primary_image_url()
            ),
        }

        cart = request.session.setdefault("cart", [])
        for item in cart:
            if item.get("variant_id") == item_to_add["variant_id"]:
                item["quantity"] += item_to_add["quantity"]
                break
        else:
            cart.append(item_to_add)

        request.session.modified = True

        return JsonResponse(
            {
                "mensaje": "Producto agregado al carrito",
                "producto_id": producto_id,
                "quantity": quantity,
            }
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Formato JSON invalido"}, status=400)
    except (TypeError, ValueError):
        return JsonResponse({"error": "Cantidad invalida"}, status=400)


def ver_carrito(request):
    """Renderiza el carrito guardado en la sesion con precios y subtotales."""
    productos_carrito_detalles = []

    for item in request.session.get("cart", []):
        producto_id = item.get("id")
        if not producto_id:
            continue

        producto = Producto.objects.filter(id=producto_id).first()
        if not producto:
            continue

        variant_id = item.get("variant_id")
        quantity = int(item.get("quantity", 1))
        variante = None
        if variant_id and str(variant_id) != str(producto_id):
            variante = Variacion.objects.filter(id=variant_id, producto=producto).first()

        final_price = variante.precio_final if variante else producto.get_precio_final()
        image_url = (
            variante.imagen.url
            if variante and variante.imagen
            else producto.get_primary_image_url()
        )

        productos_carrito_detalles.append(
            {
                "id": producto.id,
                "name": producto.nombre,
                "price": float(final_price),
                "quantity": quantity,
                "variant_id": variante.id if variante else producto.id,
                "color": variante.color if variante else item.get("color", "N/A"),
                "imageUrl": image_url,
                "price_formatted": format_precio(final_price),
                "subtotal": float(final_price * Decimal(quantity)),
            }
        )

    context = get_common_context(request)
    context["carrito_detalles"] = productos_carrito_detalles
    return render(request, "store/carrito.html", context)


def ver_favoritos(request):
    """Muestra los productos favoritos de la sesion actual."""
    if not request.session.session_key:
        request.session.save()

    favoritos_ids = set(
        Favorito.objects.filter(session_key=request.session.session_key).values_list(
            "producto_id", flat=True
        )
    )

    context = get_common_context(request)
    context.update(
        {
            "favoritos_productos": Producto.objects.filter(
                id__in=favoritos_ids, is_active=True
            ),
            "active_page": "favoritos",
        }
    )
    return render(request, "store/favoritos.html", context)


def productos_por_etiqueta(request, badge):
    """Lista productos activos filtrados por etiqueta comercial."""
    badge_display = {
        "nuevo": "Productos Nuevos",
        "tendencia": "Tendencias",
        "oferta": "Ofertas Especiales",
    }

    context = get_common_context(request)
    context.update(
        {
            "pagina_productos": Producto.objects.filter(badge=badge, is_active=True),
            "nombre_categoria_actual": badge_display.get(badge, "Productos"),
            "categoria_actual": badge,
            "active_page": badge,
        }
    )

    return render(request, "store/index.html", context)


def api_favoritos(request):
    """Devuelve los productos favoritos almacenados en localStorage del navegador."""
    ids = request.GET.get("ids", "")
    id_list = [int(product_id) for product_id in ids.split(",") if product_id.isdigit()]
    productos = Producto.objects.filter(id__in=id_list, is_active=True)

    return JsonResponse(
        {
            "productos": [
                {
                    "id": producto.id,
                    "nombre": producto.nombre,
                    "precio": f"${producto.get_precio_final():,.0f}",
                    "imagen": producto.get_primary_image_url() or "/static/img/sin_imagen.jpg",
                    "url": f"/producto/{producto.id}/",
                }
                for producto in productos
            ]
        }
    )

