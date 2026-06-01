from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0016_suscriptornewsletter_codigo"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="suscriptornewsletter",
            name="codigo_descuento",
        ),
        migrations.RemoveField(
            model_name="suscriptornewsletter",
            name="porcentaje_descuento",
        ),
        migrations.RemoveField(
            model_name="suscriptornewsletter",
            name="codigo_usado",
        ),
        migrations.RemoveField(
            model_name="suscriptornewsletter",
            name="codigo_expira",
        ),
        migrations.RemoveField(
            model_name="suscriptornewsletter",
            name="token_baja",
        ),
    ]
