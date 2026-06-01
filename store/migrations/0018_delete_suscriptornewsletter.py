from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0017_remove_suscriptornewsletter_codigo_fields"),
    ]

    operations = [
        migrations.DeleteModel(
            name="SuscriptorNewsletter",
        ),
    ]
