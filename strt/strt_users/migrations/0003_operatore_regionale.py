# Generated by Django 2.2.9 on 2021-01-27 16:21

from django.db import migrations, models
import strt_users.enums


def remap_opreg(apps, schema_editor):
    QualificaUfficio = apps.get_model('strt_users', 'QualificaUfficio')
    for qu in QualificaUfficio.objects.filter(qualifica__in=['PIAN', 'URB']):
        qu.qualifica = 'OPREG'
        qu.save()


class Migration(migrations.Migration):

    dependencies = [
        ('strt_users', '0002_qualificaufficio_is_soggetto_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qualificaufficio',
            name='qualifica',
            field=models.CharField(choices=[(strt_users.enums.Qualifica('Operatore Comunale'), 'Operatore Comunale'), (strt_users.enums.Qualifica('Operatore Regionale'), 'Operatore Regionale'), (strt_users.enums.Qualifica('AC - Aut Competente'), 'AC - Aut Competente'), (strt_users.enums.Qualifica('SCA'), 'SCA'), (strt_users.enums.Qualifica('Genio Civile'), 'Genio Civile'), (strt_users.enums.Qualifica('Sola lettura'), 'Sola lettura')], max_length=18),
        ),
        migrations.RunPython(remap_opreg),
    ]