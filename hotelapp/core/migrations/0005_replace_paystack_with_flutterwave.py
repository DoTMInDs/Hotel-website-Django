from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_customuser_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='hubtel_reference',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True, db_index=True),
        ),
    ]

