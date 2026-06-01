from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
from django.db import models
from django.db.models import Count
from django.templatetags.static import static
from django.utils.text import slugify


class CategoriaQuerySet(models.QuerySet):
    def con_productos(self):
        """Anota cada categoria con su cantidad de productos."""
        return self.annotate(num_productos=Count("productos"))

    def principales(self):
        """Devuelve las categorias de primer nivel."""
        return self.filter(padre__isnull=True)

    def subcategorias(self, categoria):
        """Devuelve las subcategorias directas de una categoria."""
        return self.filter(padre=categoria)


class CategoriaManager(models.Manager):
    def get_queryset(self):
        return CategoriaQuerySet(self.model, using=self._db)

    def principales_con_productos(self):
        return self.get_queryset().principales().con_productos()


class Categoria(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    padre = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategorias",
        help_text="Categoría padre (opcional, para subcategorías)",
    )
    imagen_circular = CloudinaryField(
        "imagen_circular",
        blank=True,
        null=True,
        help_text="Imagen circular para la categoría (ej. para la página de inicio)",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    objects = CategoriaManager()

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["padre"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
            original_slug = self.slug
            contador = 1
            while Categoria.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{contador}"
                contador += 1
        super().save(*args, **kwargs)

    @property
    def ruta_completa(self):
        if self.padre:
            return f"{self.padre.ruta_completa} > {self.nombre}"
        return self.nombre

    def __str__(self):
        return self.nombre


class Favorito(models.Model):
    session_key = models.CharField(max_length=40)
    producto = models.ForeignKey("Producto", on_delete=models.CASCADE, related_name="favoritos")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session_key", "producto")
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"

    def __str__(self):
        return f"Favorito: {self.producto.nombre} - Session: {self.session_key}"


def _force_https(url: str) -> str:
    if not url:
        return url
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http://"):
        return "https://" + url[len("http://"):]
    return url


class Producto(models.Model):
    BADGE_CHOICES = [
        ("", "Sin etiqueta"),
        ("nuevo", "Nuevo"),
        ("tendencia", "Tendencia"),
        ("oferta", "Oferta"),
    ]

    nombre = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    long_description = RichTextField(
        blank=True, null=True, verbose_name="Descripción Larga (con formato)"
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=Decimal("0"),
        help_text="Ingrese el precio sin puntos ni comas (ej. 30000 para $30.000)",
    )
    descuento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Porcentaje de descuento (ej. 0.10 para 10%)",
    )
    imagen = CloudinaryField("imagen", blank=True, null=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="productos",
        help_text="Categoría principal del producto",
    )
    is_active = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    stock = models.IntegerField(default=0)
    badge = models.CharField(
        max_length=10,
        choices=BADGE_CHOICES,
        default="",
        blank=True,
        verbose_name="Etiqueta/Insignia",
        help_text="Selecciona una etiqueta o insignia para mostrar en el producto (solo se mostrará una)",
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-fecha_creacion"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
            original_slug = self.slug
            contador = 1
            while Producto.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{contador}"
                contador += 1
        super().save(*args, **kwargs)

    def get_precio_final(self):
        precio_decimal = Decimal(self.precio)
        descuento_decimal = Decimal(self.descuento)
        if descuento_decimal > 0:
            final_price = precio_decimal * (1 - descuento_decimal)
            return final_price.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return precio_decimal

    def get_precio_schema(self) -> str:
        """Devuelve el precio en el formato decimal que espera schema.org."""
        try:
            value = Decimal(self.get_precio_final())
            return f"{value:.2f}"
        except (InvalidOperation, TypeError):
            return ""

    def get_primary_image_url(self, absolute: bool = False) -> str:
        url = None

        if getattr(self, "imagen", None):
            try:
                url = self.imagen.url
            except Exception:
                url = None

        if not url and hasattr(self, "images") and self.images.exists():
            first = self.images.first()
            try:
                url = first.image.url
            except Exception:
                url = None

        if not url:
            url = static("img/sin_imagen.jpg")

        return _force_https(url)

    def get_badge_class(self):
        badge_classes = {
            "oferta": "badge-oferta",
            "nuevo": "badge-nuevo",
            "tendencia": "badge-tendencia",
        }
        return badge_classes.get(self.badge, "")

    def __str__(self):
        return self.nombre


class ProductImage(models.Model):
    producto = models.ForeignKey(Producto, related_name="images", on_delete=models.CASCADE)
    image = CloudinaryField("imagen", blank=True, null=True)
    alt_text = models.CharField(
        max_length=255, blank=True, help_text="Texto alternativo para la imagen"
    )
    order = models.IntegerField(
        default=0, help_text="Orden de visualización de la imagen"
    )

    class Meta:
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Productos"
        ordering = ["order"]

    def __str__(self):
        return f"Imagen para {self.producto.nombre} (Orden: {self.order})"


class Variacion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="variaciones")
    nombre = models.CharField(max_length=100)
    valor = models.CharField(max_length=100)
    color = models.CharField(max_length=50, blank=True, null=True)
    color_hex = models.CharField(
        max_length=7,
        blank=True,
        null=True,
        help_text="Código HEX del color (ej. #FF0000)",
    )
    tono = models.CharField(max_length=50, blank=True, null=True)
    presentacion = models.CharField(max_length=50, blank=True, null=True)
    imagen = CloudinaryField(
        "imagen_variacion",
        blank=True,
        null=True,
        help_text="Imagen específica para esta variación",
    )
    price_override = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Opcional: Precio para esta variación. Si está vacío, usa el precio del producto principal.",
    )

    class Meta:
        unique_together = ("producto", "nombre", "valor")
        verbose_name = "Variación"
        verbose_name_plural = "Variaciones"

    @property
    def precio_final(self):
        base_price = self.price_override if self.price_override is not None else self.producto.precio
        base_price_decimal = Decimal(base_price)
        if self.producto.descuento and self.producto.descuento > 0:
            final_price = base_price_decimal * (1 - Decimal(self.producto.descuento))
            return final_price.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return base_price_decimal

    def __str__(self):
        parts = [self.producto.nombre, self.nombre, self.color, self.tono, self.presentacion]
        return " - ".join(part for part in parts if part)


class MenuItem(models.Model):
    nombre = models.CharField(max_length=100)
    url = models.CharField(
        max_length=255, help_text="URL a la que apunta el elemento de menú"
    )
    order = models.IntegerField(default=0, help_text="Orden de aparición en el menú")

    class Meta:
        verbose_name = "Elemento de Menú"
        verbose_name_plural = "Elementos de Menú"
        ordering = ["order"]

    def __str__(self):
        return self.nombre


class SiteSetting(models.Model):
    key = models.CharField(
        max_length=100,
        unique=True,
        help_text="Clave de la configuración (ej. 'whatsapp_number')",
    )
    value = models.CharField(max_length=255, help_text="Valor de la configuración")

    class Meta:
        verbose_name = "Configuración del Sitio"
        verbose_name_plural = "Configuraciones del Sitio"

    def __str__(self):
        return f"{self.key}: {self.value}"


class Anuncio(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    imagen = CloudinaryField("imagen", blank=True, null=True)
    url = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        help_text="URL a la que redirige el anuncio (opcional)",
    )
    is_active = models.BooleanField(
        default=True, help_text="¿Está activo este anuncio?"
    )
    order = models.IntegerField(
        default=0, help_text="Orden de visualización en el carrusel"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Anuncio"
        verbose_name_plural = "Anuncios"
        ordering = ["order", "-fecha_creacion"]

    def __str__(self):
        return self.titulo
