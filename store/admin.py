from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Anuncio,
    Categoria,
    MenuItem,
    ProductImage,
    Producto,
    SiteSetting,
    Variacion,
)

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug", "padre", "num_productos", "imagen_circular_preview")
    prepopulated_fields = {"slug": ("nombre",)}
    search_fields = ("nombre", "descripcion")
    list_filter = ("padre",)
    ordering = ("nombre",)
    readonly_fields = ("imagen_circular_preview",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "nombre",
                    "descripcion",
                    "slug",
                    "padre",
                    "imagen_circular",
                    "imagen_circular_preview",
                )
            },
        ),
    )

    def num_productos(self, obj):
        return getattr(obj, "num_productos", obj.productos.count())

    num_productos.short_description = "Numero de productos"

    def imagen_circular_preview(self, obj):
        if obj.imagen_circular:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.imagen_circular.url,
            )
        return "Sin imagen"

    imagen_circular_preview.short_description = "Imagen circular"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "order", "image_preview")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "Sin imagen"

    image_preview.short_description = "Vista previa"


class VariacionInline(admin.TabularInline):
    model = Variacion
    extra = 1
    fields = (
        "nombre",
        "valor",
        "color",
        "color_hex",
        "tono",
        "presentacion",
        "price_override",
        "imagen",
        "imagen_preview",
    )
    readonly_fields = ("imagen_preview",)

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" />', obj.imagen.url)
        return "Sin imagen"

    imagen_preview.short_description = "Vista previa"


class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "categoria",
        "precio",
        "descuento",
        "is_active",
        "stock",
        "fecha_creacion",
    )
    prepopulated_fields = {"slug": ("nombre",)}
    search_fields = ("nombre", "descripcion", "categoria__nombre")
    list_filter = ("is_active", "categoria")
    inlines = [ProductImageInline, VariacionInline]
    date_hierarchy = "fecha_creacion"
    ordering = ("-fecha_creacion",)
    fieldsets = (
        (
            "Informacion basica",
            {
                "fields": (
                    "nombre",
                    "slug",
                    "descripcion",
                    "long_description",
                    "categoria",
                )
            },
        ),
        ("Precios y stock", {"fields": ("precio", "descuento", "stock")}),
        (
            "Estado y etiqueta",
            {
                "fields": ("is_active", "badge"),
                "description": "Define si el producto esta activo y su etiqueta principal.",
            },
        ),
        ("Imagen principal", {"fields": ("imagen",)}),
    )


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("nombre", "url", "order")
    list_editable = ("url", "order")
    ordering = ("order",)


class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "value")
    list_editable = ("value",)
    search_fields = ("key", "value")
    ordering = ("key",)


class AnuncioAdmin(admin.ModelAdmin):
    list_display = ("titulo", "is_active", "order", "fecha_creacion", "anuncio_preview")
    list_editable = ("is_active", "order")
    search_fields = ("titulo", "descripcion")
    list_filter = ("is_active",)
    ordering = ("order", "-fecha_creacion")
    readonly_fields = ("anuncio_preview",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "titulo",
                    "descripcion",
                    "imagen",
                    "anuncio_preview",
                    "url",
                    "is_active",
                    "order",
                )
            },
        ),
    )

    def anuncio_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="100" height="auto" />', obj.imagen.url)
        return "Sin imagen"

    anuncio_preview.short_description = "Vista previa"


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(SiteSetting, SiteSettingAdmin)
admin.site.register(Anuncio, AnuncioAdmin)
