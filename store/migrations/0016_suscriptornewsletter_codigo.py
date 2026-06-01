from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0015_suscriptor_newsletter"),
    ]

    operations = [
        migrations.AddField(
            model_name="suscriptornewsletter",
            name="codigo_descuento",
            field=models.CharField(blank=True, max_length=24, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="suscriptornewsletter",
            name="porcentaje_descuento",
            field=models.PositiveSmallIntegerField(default=10),
        ),
        migrations.AddField(
            model_name="suscriptornewsletter",
            name="codigo_usado",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="suscriptornewsletter",
            name="codigo_expira",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="suscriptornewsletter",
            name="token_baja",
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
    ]
