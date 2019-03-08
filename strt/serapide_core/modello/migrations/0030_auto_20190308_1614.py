# Generated by Django 2.0.8 on 2019-03-08 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modello', '0029_proceduravas_assoggettamento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='azione',
            name='tipologia',
            field=models.CharField(choices=[('unknown', 'UNKNOWN'), ('creato_piano', 'Creato Piano'), ('richiesta_verifica_vas', 'Richiesta Verifica VAS'), ('avvio_procedimento', 'Avvio Procedimento'), ('formazione_del_piano', 'Formazione del Piano'), ('protocollo_genio_civile', 'Protocollo Genio Civile'), ('pareri_verifica_sca', 'Pareri Verifica VAS'), ('osservazioni_enti', 'Osservazioni Enti'), ('osservazioni_regione', 'Osservazioni Regione'), ('upload_osservazioni_privati', 'Upload Osservazioni Privati'), ('convocazione_conferenza_copianificazione', 'Convocazione Conferenza di Copianificazione'), ('emissione_provvedimento_verifica', 'Emissione Provvedimento di Verifica'), ('emissione_documento_preliminare_vas', 'Emissione Documento Preliminare VAS'), ('pubblicazione_provvedimento_verifica', 'Pubblicazione Provvedimento di Verifica'), ('avvio_consultazioni_sca', 'Avvio Consultazioni SCA'), ('pareri_sca', 'Pareri SCA')], default='unknown', max_length=80),
        ),
    ]
