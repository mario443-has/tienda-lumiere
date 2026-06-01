from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0014_remove_producto_etiqueta_producto_badge"),
    ]

    operations = [
        migrations.CreateModel(
            name="SuscriptorNewsletter",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("activo", models.BooleanField(default=True)),
                ("fecha_suscripcion", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Suscriptor del newsletter",
                "verbose_name_plural": "Suscriptores del newsletter",
                "ordering": ["-fecha_suscripcion"],
            },
        ),
    ]
