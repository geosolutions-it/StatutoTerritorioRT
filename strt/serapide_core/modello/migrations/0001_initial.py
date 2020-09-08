# Generated by Django 2.2.9 on 2020-09-08 09:19

from django.db import migrations, models
import django.db.models.deletion
import serapide_core.modello.enums
import strt_users.enums
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Azione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('tipologia', models.CharField(choices=[(serapide_core.modello.enums.TipologiaAzione('UNKNOWN'), 'UNKNOWN'), (serapide_core.modello.enums.TipologiaAzione('Creato Piano/Variante'), 'Creato Piano/Variante'), (serapide_core.modello.enums.TipologiaAzione('Selezione tipologia VAS'), 'Selezione tipologia VAS'), (serapide_core.modello.enums.TipologiaAzione('Pareri verifica VAS'), 'Pareri verifica VAS'), (serapide_core.modello.enums.TipologiaAzione('Emissione Provvedimento di verifica'), 'Emissione Provvedimento di verifica'), (serapide_core.modello.enums.TipologiaAzione('Pubblicazione provvedimento di verifica AC'), 'Pubblicazione provvedimento di verifica AC'), (serapide_core.modello.enums.TipologiaAzione('Pubblicazione provvedimento di verifica AP'), 'Pubblicazione provvedimento di verifica AP'), (serapide_core.modello.enums.TipologiaAzione('Invio documentazione preliminare'), 'Invio documentazione preliminare'), (serapide_core.modello.enums.TipologiaAzione('Trasmissione pareri SCA'), 'Trasmissione pareri SCA'), (serapide_core.modello.enums.TipologiaAzione('Trasmissione pareri AC'), 'Trasmissione pareri AC'), (serapide_core.modello.enums.TipologiaAzione('Redazione documenti VAS'), 'Redazione documenti VAS'), (serapide_core.modello.enums.TipologiaAzione('Trasmissione documento preliminare di verifica'), 'Trasmissione documento preliminare di verifica'), (serapide_core.modello.enums.TipologiaAzione('Avvio del Procedimento'), 'Avvio del Procedimento'), (serapide_core.modello.enums.TipologiaAzione('Contributi Tecnici'), 'Contributi Tecnici'), (serapide_core.modello.enums.TipologiaAzione('Richiesta Integrazioni'), 'Richiesta Integrazioni'), (serapide_core.modello.enums.TipologiaAzione('Integrazioni Richieste'), 'Integrazioni Richieste'), (serapide_core.modello.enums.TipologiaAzione('Formazione del Piano'), 'Formazione del Piano'), (serapide_core.modello.enums.TipologiaAzione('Protocollo Genio Civile'), 'Protocollo Genio Civile'), (serapide_core.modello.enums.TipologiaAzione('Richiesta Conferenza di copianificazione'), 'Richiesta Conferenza di copianificazione'), (serapide_core.modello.enums.TipologiaAzione('Esito conferenza di copianificazione'), 'Esito conferenza di copianificazione'), (serapide_core.modello.enums.TipologiaAzione('Trasmissione Adozione'), 'Trasmissione Adozione'), (serapide_core.modello.enums.TipologiaAzione('Pubblicazione BURT'), 'Pubblicazione BURT'), (serapide_core.modello.enums.TipologiaAzione('Osservazioni Soggetti Istituzionali'), 'Osservazioni Soggetti Istituzionali'), (serapide_core.modello.enums.TipologiaAzione('Osservazioni Regione'), 'Osservazioni Regione'), (serapide_core.modello.enums.TipologiaAzione('Upload Osservazioni Privati'), 'Upload Osservazioni Privati'), (serapide_core.modello.enums.TipologiaAzione('Controdeduzioni'), 'Controdeduzioni'), (serapide_core.modello.enums.TipologiaAzione('Piano Controdedotto'), 'Piano Controdedotto'), (serapide_core.modello.enums.TipologiaAzione('Risultanze conferenza paesaggistica'), 'Risultanze conferenza paesaggistica'), (serapide_core.modello.enums.TipologiaAzione('Revisione Piano post Conf. Paesaggistica'), 'Revisione Piano post Conf. Paesaggistica'), (serapide_core.modello.enums.TipologiaAzione('Pareri SCA'), 'Pareri SCA'), (serapide_core.modello.enums.TipologiaAzione('Parere Motivato'), 'Parere Motivato'), (serapide_core.modello.enums.TipologiaAzione('Upload elaborati VAS'), 'Upload elaborati VAS'), (serapide_core.modello.enums.TipologiaAzione('Invio documentazione per Approvazione'), 'Invio documentazione per Approvazione'), (serapide_core.modello.enums.TipologiaAzione('Attribuzione Conformità PIT'), 'Attribuzione Conformità PIT'), (serapide_core.modello.enums.TipologiaAzione('Convocazione CP'), 'Convocazione CP'), (serapide_core.modello.enums.TipologiaAzione('Pubblicazione Approvazione'), 'Pubblicazione Approvazione'), (serapide_core.modello.enums.TipologiaAzione('Convocazione Commissione Paritetica'), 'Convocazione Commissione Paritetica'), (serapide_core.modello.enums.TipologiaAzione('Compilazione Finale Monitoraggio Urbanistico'), 'Compilazione Finale Monitoraggio Urbanistico'), (serapide_core.modello.enums.TipologiaAzione('Pubblicazione Piano'), 'Pubblicazione Piano'), (serapide_core.modello.enums.TipologiaAzione('Validazione elaborati cartografici - Adozione'), 'Validazione elaborati cartografici - Adozione'), (serapide_core.modello.enums.TipologiaAzione('Processamento elaborati cartografici - Adozione'), 'Processamento elaborati cartografici - Adozione'), (serapide_core.modello.enums.TipologiaAzione('Validazione elaborati cartografici - PCD Adozione'), 'Validazione elaborati cartografici - PCD Adozione'), (serapide_core.modello.enums.TipologiaAzione('Processamento elaborati cartografici - PCD Adozione'), 'Processamento elaborati cartografici - PCD Adozione'), (serapide_core.modello.enums.TipologiaAzione('Validazione elaborati cartografici - CP Adozione'), 'Validazione elaborati cartografici - CP Adozione'), (serapide_core.modello.enums.TipologiaAzione('Processamento elaborati cartografici - CP Adozione'), 'Processamento elaborati cartografici - CP Adozione'), (serapide_core.modello.enums.TipologiaAzione('Validazione elaborati cartografici - Approvazione'), 'Validazione elaborati cartografici - Approvazione'), (serapide_core.modello.enums.TipologiaAzione('Processamento elaborati cartografici - Approvazione'), 'Processamento elaborati cartografici - Approvazione'), (serapide_core.modello.enums.TipologiaAzione('Validazione elaborati cartografici - CP Approvazione'), 'Validazione elaborati cartografici - CP Approvazione'), (serapide_core.modello.enums.TipologiaAzione('Processamento elaborati cartografici - CP Approvazione'), 'Processamento elaborati cartografici - CP Approvazione')], default=serapide_core.modello.enums.TipologiaAzione('UNKNOWN'), max_length=60)),
                ('qualifica_richiesta', models.CharField(choices=[(strt_users.enums.QualificaRichiesta('Responsabile Comunale'), 'Responsabile Comunale'), (strt_users.enums.QualificaRichiesta('AC'), 'AC'), (strt_users.enums.QualificaRichiesta('SCA'), 'SCA'), (strt_users.enums.QualificaRichiesta('Genio Civile'), 'Genio Civile'), (strt_users.enums.QualificaRichiesta('Responsabile Pianificazione'), 'Responsabile Pianificazione'), (strt_users.enums.QualificaRichiesta('Responsabile Urbanistica'), 'Responsabile Urbanistica'), (strt_users.enums.QualificaRichiesta('Responsabile Regionale'), 'Responsabile Regionale'), (strt_users.enums.QualificaRichiesta('Sistema'), 'Sistema')], max_length=26)),
                ('stato', models.CharField(choices=[(serapide_core.modello.enums.StatoAzione('attesa'), 'attesa'), (serapide_core.modello.enums.StatoAzione('necessaria'), 'necessaria'), (serapide_core.modello.enums.StatoAzione('eseguita'), 'eseguita'), (serapide_core.modello.enums.StatoAzione('fallita'), 'fallita')], max_length=22)),
                ('data', models.DateTimeField(blank=True, null=True)),
                ('avvio_scadenza', models.DateField(blank=True, null=True)),
                ('scadenza', models.DateField(blank=True, null=True)),
                ('order', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name_plural': 'Azioni',
                'db_table': 'strt_core_azione',
            },
        ),
        migrations.CreateModel(
            name='AzioneReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[(serapide_core.modello.enums.TipoReportAzione('info'), 'info'), (serapide_core.modello.enums.TipoReportAzione('warn'), 'warn'), (serapide_core.modello.enums.TipoReportAzione('err'), 'err')], default=serapide_core.modello.enums.TipoReportAzione('info'), max_length=21)),
                ('messaggio', models.TextField()),
                ('data', models.DateTimeField()),
            ],
            options={
                'db_table': 'strt_core_azione_report',
            },
        ),
        migrations.CreateModel(
            name='ConferenzaCopianificazione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
                ('id_pratica', models.TextField(blank=True, null=True)),
                ('data_richiesta_conferenza', models.DateTimeField(blank=True, null=True)),
                ('data_scadenza_risposta', models.DateTimeField(blank=True, null=True)),
                ('data_chiusura_conferenza', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Conferenze di Copianificazione',
                'db_table': 'strt_core_conferenza_copianificazione',
            },
        ),
        migrations.CreateModel(
            name='Delega',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qualifica', models.CharField(choices=[(strt_users.enums.Qualifica('Operatore Comunale'), 'Operatore Comunale'), (strt_users.enums.Qualifica('AC - Aut Competente'), 'AC - Aut Competente'), (strt_users.enums.Qualifica('SCA'), 'SCA'), (strt_users.enums.Qualifica('Genio Civile'), 'Genio Civile'), (strt_users.enums.Qualifica('Pianificazione'), 'Pianificazione'), (strt_users.enums.Qualifica('Urbanistica'), 'Urbanistica'), (strt_users.enums.Qualifica('Sola lettura'), 'Sola lettura')], max_length=18)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Deleghe',
                'db_table': 'strt_core_delega',
            },
        ),
        migrations.CreateModel(
            name='ElaboratoCartografico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.TextField()),
                ('minx', models.FloatField()),
                ('maxx', models.FloatField()),
                ('miny', models.FloatField()),
                ('maxy', models.FloatField()),
                ('crs', models.CharField(max_length=12)),
                ('zipfile', models.TextField(null=True)),
                ('ingerito', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'strt_cartografia_elaborato',
            },
        ),
        migrations.CreateModel(
            name='FasePianoStorico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fase', models.CharField(choices=[(serapide_core.modello.enums.Fase('UNKNOWN'), 'UNKNOWN'), (serapide_core.modello.enums.Fase('DRAFT'), 'DRAFT'), (serapide_core.modello.enums.Fase('ANAGRAFICA'), 'ANAGRAFICA'), (serapide_core.modello.enums.Fase('AVVIO'), 'AVVIO'), (serapide_core.modello.enums.Fase('ADOZIONE'), 'ADOZIONE'), (serapide_core.modello.enums.Fase('APPROVAZIONE'), 'APPROVAZIONE'), (serapide_core.modello.enums.Fase('PUBBLICAZIONE'), 'PUBBLICAZIONE')], default=serapide_core.modello.enums.Fase('UNKNOWN'), max_length=18)),
                ('data_apertura', models.DateTimeField()),
                ('data_chiusura', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'strt_core_piano_storico_fasi',
            },
        ),
        migrations.CreateModel(
            name='LottoCartografico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'strt_cartografia_lotto',
            },
        ),
        migrations.CreateModel(
            name='ParereAdozioneVAS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
                ('data_creazione', models.DateTimeField(auto_now_add=True)),
                ('data_invio_parere', models.DateTimeField(blank=True, null=True)),
                ('data_ricezione_parere', models.DateTimeField(blank=True, null=True)),
                ('inviata', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Pareri Adozione VAS',
                'db_table': 'strt_core_pareri_adozione_vas',
            },
        ),
        migrations.CreateModel(
            name='ParereVAS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
                ('data_creazione', models.DateTimeField(auto_now_add=True)),
                ('data_invio_parere', models.DateTimeField(blank=True, null=True)),
                ('data_ricezione_parere', models.DateTimeField(blank=True, null=True)),
                ('inviata', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Pareri VAS',
                'db_table': 'strt_core_pareri_vas',
            },
        ),
        migrations.CreateModel(
            name='ParereVerificaVAS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
                ('data_creazione', models.DateTimeField(auto_now_add=True)),
                ('data_invio_parere', models.DateTimeField(blank=True, null=True)),
                ('data_ricezione_parere', models.DateTimeField(blank=True, null=True)),
                ('inviata', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Pareri Verifica VAS',
                'db_table': 'strt_core_pareri_verifica_vas',
            },
        ),
        migrations.CreateModel(
            name='Piano',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
                ('codice', models.CharField(max_length=255, unique=True)),
                ('tipologia', models.CharField(choices=[(serapide_core.modello.enums.TipologiaPiano('UNKNOWN'), 'UNKNOWN'), (serapide_core.modello.enums.TipologiaPiano('OPERATIVO'), 'OPERATIVO'), (serapide_core.modello.enums.TipologiaPiano('STRUTTURALE'), 'STRUTTURALE')], default=serapide_core.modello.enums.TipologiaPiano('UNKNOWN'), max_length=26)),
                ('descrizione', models.TextField(blank=True, null=True)),
                ('url', models.URLField(blank=True, default='', null=True)),
                ('numero_delibera', models.TextField(blank=True, null=True)),
                ('data_delibera', models.DateTimeField(blank=True, null=True)),
                ('data_creazione', models.DateTimeField(auto_now_add=True)),
                ('data_accettazione', models.DateTimeField(blank=True, null=True)),
                ('data_avvio', models.DateTimeField(blank=True, null=True)),
                ('data_approvazione', models.DateTimeField(blank=True, null=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('data_protocollo_genio_civile', models.DateTimeField(blank=True, null=True)),
                ('fase', models.CharField(choices=[(serapide_core.modello.enums.Fase('UNKNOWN'), 'UNKNOWN'), (serapide_core.modello.enums.Fase('DRAFT'), 'DRAFT'), (serapide_core.modello.enums.Fase('ANAGRAFICA'), 'ANAGRAFICA'), (serapide_core.modello.enums.Fase('AVVIO'), 'AVVIO'), (serapide_core.modello.enums.Fase('ADOZIONE'), 'ADOZIONE'), (serapide_core.modello.enums.Fase('APPROVAZIONE'), 'APPROVAZIONE'), (serapide_core.modello.enums.Fase('PUBBLICAZIONE'), 'PUBBLICAZIONE')], default=serapide_core.modello.enums.Fase('UNKNOWN'), max_length=18)),
                ('redazione_norme_tecniche_attuazione_url', models.URLField(blank=True, default='', null=True)),
                ('compilazione_rapporto_ambientale_url', models.URLField(blank=True, default='', null=True)),
                ('conformazione_pit_ppr_url', models.URLField(blank=True, default='', null=True)),
                ('monitoraggio_urbanistico_url', models.URLField(blank=True, default='', null=True)),
            ],
            options={
                'verbose_name_plural': 'Piani',
                'db_table': 'strt_core_piano',
            },
        ),
        migrations.CreateModel(
            name='PianoControdedotto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
            ],
            options={
                'verbose_name_plural': 'Piani Controdedotti',
                'db_table': 'strt_core_piano_controdedotto',
            },
        ),
        migrations.CreateModel(
            name='PianoRevPostCP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
            ],
            options={
                'verbose_name_plural': 'Piani Rev. post CP',
                'db_table': 'strt_core_piano_rev_post_cp',
            },
        ),
        migrations.CreateModel(
            name='ProceduraAdozione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
                ('data_creazione', models.DateTimeField(auto_now_add=True)),
                ('data_delibera_adozione', models.DateTimeField(blank=True, null=True)),
                ('data_ricezione_osservazioni', models.DateTimeField(blank=True, null=True)),
                ('data_ricezione_pareri', models.DateTimeField(blank=True, null=True)),
                ('pubblicazione_burt_url', models.URLField(blank=True, default='', null=True)),
                ('pubblicazione_burt_data', models.DateTimeField(blank=True, null=True)),
                ('pubblicazione_burt_bollettino', models.TextField(blank=True, null=True)),
                ('pubblicazione_sito_url', models.URLField(blank=True, default='', null=True)),
                ('osservazioni_concluse', models.BooleanField(default=False)),
                ('richiesta_conferenza_paesaggistica', models.BooleanField(default=False)),
                ('url_piano_controdedotto', models.URLField(blank=True, default='', null=True)),
                ('url_rev_piano_post_cp', models.URLField(blank=True, default='', null=True)),
                ('conclusa', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Procedure Adozione',
                'db_table': 'strt_core_adozione',
            },
        ),
        migrations.CreateModel(
            name='ProceduraAdozioneVAS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
                ('data_creazione', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('conclusa', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Procedure Adozione VAS',
                'db_table': 'strt_core_adozione_vas',
            },
        ),
        migrations.CreateModel(
            name='ProceduraApprovazione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
                ('data_creazione', models.DateTimeField(auto_now_add=True)),
                ('data_delibera_approvazione', models.DateTimeField(blank=True, null=True)),
                ('pubblicazione_url', models.URLField(blank=True, default='', null=True)),
                ('pubblicazione_url_data', models.DateTimeField(blank=True, null=True)),
                ('richiesta_conferenza_paesaggistica', models.BooleanField(default=False)),
                ('url_piano_pubblicato', models.URLField(blank=True, default='', null=True)),
                ('url_rev_piano_post_cp', models.URLField(blank=True, default='', null=True)),
                ('conclusa', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Procedure Approvazione',
                'db_table': 'strt_core_approvazione',
            },
        ),
        migrations.CreateModel(
            name='ProceduraAvvio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
                ('conferenza_copianificazione', models.CharField(blank=True, choices=[(serapide_core.modello.enums.TipologiaCopianificazione('Posticipata'), 'Posticipata'), (serapide_core.modello.enums.TipologiaCopianificazione('Necessaria'), 'Necessaria'), (serapide_core.modello.enums.TipologiaCopianificazione('Non necessaria'), 'Non necessaria')], default=None, max_length=40, null=True)),
                ('data_creazione', models.DateTimeField(auto_now_add=True)),
                ('data_scadenza_risposta', models.DateTimeField(blank=True, null=True)),
                ('garante_nominativo', models.TextField(blank=True, null=True)),
                ('garante_pec', models.EmailField(blank=True, max_length=254, null=True)),
                ('notifica_genio_civile', models.BooleanField(default=False)),
                ('richiesta_integrazioni', models.BooleanField(default=False)),
                ('messaggio_integrazione', models.TextField(blank=True, null=True)),
                ('conclusa', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Procedure Avvio',
                'db_table': 'strt_core_avvio',
            },
        ),
        migrations.CreateModel(
            name='ProceduraPubblicazione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
                ('data_creazione', models.DateTimeField(auto_now_add=True)),
                ('data_pubblicazione', models.DateTimeField(blank=True, null=True)),
                ('pubblicazione_url', models.URLField(blank=True, default='', null=True)),
                ('pubblicazione_url_data', models.DateTimeField(blank=True, null=True)),
                ('conclusa', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Procedure Pubblicazione',
                'db_table': 'strt_core_pubblicazione',
            },
        ),
        migrations.CreateModel(
            name='ProceduraVAS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
                ('tipologia', models.CharField(choices=[(serapide_core.modello.enums.TipologiaVAS('UNKNOWN'), 'UNKNOWN'), (serapide_core.modello.enums.TipologiaVAS('Verifica semplificata'), 'Verifica semplificata'), (serapide_core.modello.enums.TipologiaVAS('Verifica'), 'Verifica'), (serapide_core.modello.enums.TipologiaVAS('Procedura ordinaria'), 'Procedura ordinaria'), (serapide_core.modello.enums.TipologiaVAS('Procedimento semplificato'), 'Procedimento semplificato'), (serapide_core.modello.enums.TipologiaVAS('VAS non necessaria'), 'VAS non necessaria')], default=serapide_core.modello.enums.TipologiaVAS('UNKNOWN'), max_length=38)),
                ('note', models.TextField(blank=True, null=True)),
                ('data_creazione', models.DateTimeField(auto_now_add=True)),
                ('data_verifica', models.DateTimeField(blank=True, null=True)),
                ('data_procedimento', models.DateTimeField(blank=True, null=True)),
                ('data_assoggettamento', models.DateTimeField(blank=True, null=True)),
                ('data_approvazione', models.DateTimeField(blank=True, null=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('verifica_effettuata', models.BooleanField(default=False)),
                ('procedimento_effettuato', models.BooleanField(default=False)),
                ('non_necessaria', models.BooleanField(default=False)),
                ('assoggettamento', models.NullBooleanField(default=None)),
                ('pubblicazione_provvedimento_verifica_ap', models.URLField(blank=True, null=True)),
                ('pubblicazione_provvedimento_verifica_ac', models.URLField(blank=True, null=True)),
                ('conclusa', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Procedure VAS',
                'db_table': 'strt_core_vas',
            },
        ),
        migrations.CreateModel(
            name='Risorsa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
                ('nome', models.TextField()),
                ('file', models.FileField(max_length=500, upload_to='uploads/%Y/%m/%d/')),
                ('tipo', models.TextField()),
                ('dimensione', models.DecimalField(decimal_places=10, default=0.0, max_digits=19)),
                ('descrizione', models.TextField(blank=True, null=True)),
                ('data_creazione', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('fase', models.CharField(choices=[(serapide_core.modello.enums.Fase('UNKNOWN'), 'UNKNOWN'), (serapide_core.modello.enums.Fase('DRAFT'), 'DRAFT'), (serapide_core.modello.enums.Fase('ANAGRAFICA'), 'ANAGRAFICA'), (serapide_core.modello.enums.Fase('AVVIO'), 'AVVIO'), (serapide_core.modello.enums.Fase('ADOZIONE'), 'ADOZIONE'), (serapide_core.modello.enums.Fase('APPROVAZIONE'), 'APPROVAZIONE'), (serapide_core.modello.enums.Fase('PUBBLICAZIONE'), 'PUBBLICAZIONE')], default=serapide_core.modello.enums.Fase('UNKNOWN'), max_length=18)),
                ('archiviata', models.BooleanField(default=False)),
                ('valida', models.NullBooleanField(default=None)),
            ],
            options={
                'verbose_name_plural': 'Risorse',
                'db_table': 'strt_core_risorsa',
            },
        ),
        migrations.CreateModel(
            name='RisorseAdozione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'strt_core_adozione_risorse',
            },
        ),
        migrations.CreateModel(
            name='RisorseAdozioneVas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'strt_core_adozione_vas_risorse',
            },
        ),
        migrations.CreateModel(
            name='RisorseApprovazione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'strt_core_approvazione_risorse',
            },
        ),
        migrations.CreateModel(
            name='RisorseAvvio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'strt_core_avvio_risorse',
            },
        ),
        migrations.CreateModel(
            name='RisorseCopianificazione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'strt_core_risorse_copianificazione',
            },
        ),
        migrations.CreateModel(
            name='RisorsePiano',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'strt_core_piano_risorse',
            },
        ),
        migrations.CreateModel(
            name='RisorsePianoControdedotto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'strt_core_risorse_piano_controdedotto',
            },
        ),
        migrations.CreateModel(
            name='RisorsePianoRevPostCP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'strt_core_risorse_piano_rev_post_cp',
            },
        ),
        migrations.CreateModel(
            name='RisorsePubblicazione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'strt_core_pubblicazione_risorse',
            },
        ),
        migrations.CreateModel(
            name='RisorseVas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'strt_core_vas_risorse',
            },
        ),
        migrations.CreateModel(
            name='SoggettoOperante',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='id')),
                ('piano', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='so+', to='modello.Piano')),
            ],
            options={
                'db_table': 'strt_core_soggettooperante',
            },
        ),
    ]
