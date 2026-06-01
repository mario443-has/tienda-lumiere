import os
import django
from django.utils.text import slugify

# Configurar el entorno de Django para ejecutar un script independiente
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumiere_glamour.settings")
django.setup()

from store.models import Categoria, Producto

def cargar_datos():
    print("Iniciando la carga de categorias y productos para Lumiere Glamour...")

    # ==========================================
    # 1. CREACION DE CATEGORIAS PADRE Y SUBCATEGORIAS
    # ==========================================
    
    # --- PADRE: ROSTRO ---
    rostro, _ = Categoria.objects.get_or_create(
        nombre="Rostro",
        defaults={"descripcion": "Productos profesionales para preparar, unificar y resaltar la piel de tu rostro."}
    )
    # Subcategorías Rostro
    bases, _ = Categoria.objects.get_or_create(
        nombre="Bases y Correctores",
        defaults={"padre": rostro, "descripcion": "Bases de alta cobertura, correctores de ojeras y polvos compactos."}
    )
    rubores, _ = Categoria.objects.get_or_create(
        nombre="Rubores e Iluminadores",
        defaults={"padre": rostro, "descripcion": "Rubores liquidos, en polvo e iluminadores satinados para dar luz."}
    )

    # --- PADRE: OJOS Y CEJAS ---
    ojos, _ = Categoria.objects.get_or_create(
        nombre="Ojos y Cejas",
        defaults={"descripcion": "Define tu mirada con los mejores pigmentos, delineadores y productos de cejas."}
    )
    # Subcategorías Ojos
    sombras, _ = Categoria.objects.get_or_create(
        nombre="Paletas de Sombras",
        defaults={"padre": ojos, "descripcion": "Paletas de sombras altamente pigmentadas en tonos nude, coloridos y satinados."}
    )
    pestanas, _ = Categoria.objects.get_or_create(
        nombre="Delineadores y Pestañinas",
        defaults={"padre": ojos, "descripcion": "Pestanas a prueba de agua y delineadores de precision extrema."}
    )

    # --- PADRE: LABIOS ---
    labios, _ = Categoria.objects.get_or_create(
        nombre="Labios",
        defaults={"descripcion": "Destaca tus labios con colores vibrantes, acabados mate y formulas hidratantes."}
    )
    # Subcategorías Labios
    matte, _ = Categoria.objects.get_or_create(
        nombre="Labiales Matte",
        defaults={"padre": labios, "descripcion": "Labiales liquidos mate de larga duracion e indelebles."}
    )
    brillos, _ = Categoria.objects.get_or_create(
        nombre="Brillos y Tintas",
        defaults={"padre": labios, "descripcion": "Glosses voluminizadores, brillos hidratantes y tintas naturales."}
    )

    # --- PADRE: CUIDADO DE LA PIEL (SKINCARE) ---
    skincare, _ = Categoria.objects.get_or_create(
        nombre="Cuidado de la Piel",
        defaults={"descripcion": "Rutinas completas para mantener una piel radiante, limpia y saludable."}
    )
    # Subcategorías Skincare
    limpieza, _ = Categoria.objects.get_or_create(
        nombre="Limpieza Facial",
        defaults={"padre": skincare, "descripcion": "Jabones limpiadores, aguas micelares y exfoliantes suaves."}
    )
    serums, _ = Categoria.objects.get_or_create(
        nombre="Hidratacion y Serums",
        defaults={"padre": skincare, "descripcion": "Acido hialuronico, vitamina C, serums hidratantes y cremas faciales."}
    )

    # Asegurar slugs para todas las categorías creadas
    for cat in Categoria.objects.all():
        if not cat.slug:
            cat.slug = slugify(cat.nombre)
            cat.save()

    print("-> Categorias jerarquicas creadas correctamente.")

    # ==========================================
    # 2. CREACION DE PRODUCTOS EN PESOS COLOMBIANOS (COP)
    # ==========================================
    # - El precio se envia como String sin decimales ("79900") ya que decimal_places=0.
    # - El descuento se envia como porcentaje decimal fraccionario ("0.15" para 15%) ya que decimal_places=2.
    
    productos_data = [
        # --- Productos de Bases y Correctores ---
        {
            "nombre": "Base de Maquillaje Mate HD Pro",
            "categoria": bases,
            "precio": "79900",       # $79.900 COP
            "descuento": "0.15",     # 15% de Descuento
            "stock": 25,
            "descripcion": "Base liquida de cobertura construible con acabado mate natural. Controla la grasa durante 16 horas sin resecar la piel.",
            "badge": "nuevo"
        },
        {
            "nombre": "Corrector Líquido Cobertura Total",
            "categoria": bases,
            "precio": "34900",       # $34.900 COP
            "descuento": "0.00",     # Sin descuento
            "stock": 30,
            "descripcion": "Corrector de alta cobertura que disimula imperfecciones, ojeras y manchas al instante sin cuartearse.",
            "badge": "tendencia"
        },

        # --- Productos de Rubores e Iluminadores ---
        {
            "nombre": "Rubor Líquido Velvet Cheek",
            "categoria": rubores,
            "precio": "42900",       # $42.900 COP
            "descuento": "0.10",     # 10% de Descuento
            "stock": 15,
            "descripcion": "Rubor liquido de textura sedosa que se funde en la piel aportando un color natural y radiante de larga duracion.",
            "badge": "tendencia"
        },
        {
            "nombre": "Iluminador Compacto Destellos de Oro",
            "categoria": rubores,
            "precio": "49900",       # $49.900 COP
            "descuento": "0.00",
            "stock": 20,
            "descripcion": "Iluminador en polvo micropulido con reflejos dorados perfectos para un efecto 'glow' de aspecto mojado.",
            "badge": ""
        },

        # --- Productos de Paletas de Sombras ---
        {
            "nombre": "Paleta Nude Glam de 18 Tonos",
            "categoria": sombras,
            "precio": "119900",      # $119.900 COP
            "descuento": "0.20",     # 20% de Descuento (Súper oferta!)
            "stock": 12,
            "descripcion": "Una seleccion perfecta de 18 sombras que van desde nudes calidos hasta cobres metalizados ultra cremosos.",
            "badge": "oferta"
        },

        # --- Productos de Delineadores y Pestañinas ---
        {
            "nombre": "Pestañina Alargamiento Infinito Waterproof",
            "categoria": pestanas,
            "precio": "38900",       # $38.900 COP
            "descuento": "0.00",
            "stock": 50,
            "descripcion": "Formula enriquecida con fibras alargadoras y cepillo curvo que eleva y da volumen sin dejar grumos.",
            "badge": "tendencia"
        },

        # --- Productos de Labiales Matte ---
        {
            "nombre": "Labial Líquido Velvet Mate 24h",
            "categoria": matte,
            "precio": "35900",       # $35.900 COP
            "descuento": "0.15",     # 15% de Descuento
            "stock": 40,
            "descripcion": "Labial liquido de secado rapido que ofrece un color mate ultra pigmentado de larga duracion a prueba de transferencias.",
            "badge": "oferta"
        },

        # --- Productos de Brillos y Tintas ---
        {
            "nombre": "Glow Plump Lip Voluminizer",
            "categoria": brillos,
            "precio": "31900",       # $31.900 COP
            "descuento": "0.00",
            "stock": 18,
            "descripcion": "Brillo de labios de efecto mentolado que rellena visualmente los labios dandoles un aspecto jugoso e hidratado.",
            "badge": "nuevo"
        },

        # --- Productos de Hidratación y Sérums ---
        {
            "nombre": "Sérum Hidratante Ácido Hialurónico 2%",
            "categoria": serums,
            "precio": "64900",       # $64.900 COP
            "descuento": "0.15",     # 15% de Descuento
            "stock": 15,
            "descripcion": "Serum concentrado hidratante que rellena lineas de expresion e hidrata profundamente las diferentes capas de la piel.",
            "badge": "nuevo"
        }
    ]

    for prod_info in productos_data:
        prod, created = Producto.objects.get_or_create(
            nombre=prod_info["nombre"],
            defaults={
                "categoria": prod_info["categoria"],
                "precio": prod_info["precio"],
                "descuento": prod_info["descuento"],
                "stock": prod_info["stock"],
                "descripcion": prod_info["descripcion"],
                "badge": prod_info["badge"],
                "slug": slugify(prod_info["nombre"]),
                "is_active": True
            }
        )
        if created:
            print(f"  -> Producto creado: {prod.nombre}")
        else:
            print(f"  -> El producto ya existia: {prod.nombre}")

    print("\nCarga de datos completada con exito! Tu tienda esta lista para probarse.")

if __name__ == "__main__":
    cargar_datos()
