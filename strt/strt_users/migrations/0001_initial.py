# Generated by Django 2.2.9 on 2020-09-08 09:19

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_currentuser.db.models.fields
import django_currentuser.middleware
import strt_users.enums
import strt_users.managers
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Utente',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('fiscal_code', models.CharField(db_index=True, help_text='inserire un codice fiscale valido', max_length=16, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator(message='Codice fiscale errato.', regex='^(?i)(?:(?:[B-DF-HJ-NP-TV-Z]|[AEIOU])[AEIOU][AEIOUX]|[B-DF-HJ-NP-TV-Z]{2}[A-Z]){2}[\\dLMNP-V]{2}(?:[A-EHLMPR-T](?:[04LQ][1-9MNP-V]|[1256LMRS][\\dLMNP-V])|[DHPS][37PT][0L]|[ACELMRT][37PT][01LM])(?:[A-MZ][1-9MNP-V][\\dLMNP-V]{2}|[A-M][0L](?:[1-9MNP-V][\\dLMNP-V]|[0L][1-9MNP-V]))[A-Z]$')], verbose_name='codice fiscale')),
                ('first_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='nome')),
                ('last_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='cognome')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='indirizzo email')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='data creazione')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='data ultima modifica')),
                ('created_by', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='utente_created', to=settings.AUTH_USER_MODEL, verbose_name='creato da')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('updated_by', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='utente_updated', to=settings.AUTH_USER_MODEL, verbose_name='modificato da')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'utente',
                'verbose_name_plural': 'utenti',
                'ordering': ['date_joined'],
            },
            managers=[
                ('objects', strt_users.managers.IsideUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Ente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ipa', models.CharField(max_length=255, verbose_name='codice ipa')),
                ('nome', models.CharField(max_length=255, verbose_name='nome')),
                ('descrizione', models.TextField(blank=True, max_length=500, null=True, verbose_name='descrizione')),
                ('tipo', models.CharField(choices=[(strt_users.enums.TipoEnte('Comune'), 'Comune'), (strt_users.enums.TipoEnte('Regione'), 'Regione'), (strt_users.enums.TipoEnte('Altro'), 'Altro')], max_length=16)),
            ],
            options={
                'verbose_name': 'ente',
                'verbose_name_plural': 'enti',
            },
        ),
        migrations.CreateModel(
            name='Ufficio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('nome', models.CharField(max_length=255, verbose_name='nome')),
                ('descrizione', models.TextField(blank=True, max_length=500, null=True, verbose_name='descrizione')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='indirizzo email')),
                ('ente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='strt_users.Ente')),
            ],
            options={
                'verbose_name_plural': 'Uffici',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('key', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('expires', models.DateTimeField()),
                ('user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='QualificaUfficio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qualifica', models.CharField(
                    choices=[
                        (strt_users.enums.Qualifica('Operatore Comunale'), 'Operatore Comunale'),
                        (strt_users.enums.Qualifica('AC - Aut Competente'), 'AC - Aut Competente'),
                        (strt_users.enums.Qualifica('SCA'), 'SCA'),
                        (strt_users.enums.Qualifica('Genio Civile'), 'Genio Civile'),
                        # (strt_users.enums.Qualifica('Pianificazione'), 'Pianificazione'),
                        # (strt_users.enums.Qualifica('Urbanistica'), 'Urbanistica'),
                        (strt_users.enums.Qualifica('Sola lettura'), 'Sola lettura')],
                    max_length=18)),
                ('ufficio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='strt_users.Ufficio')),
            ],
            options={
                'verbose_name_plural': 'Qualifiche uffici',
            },
        ),
        migrations.CreateModel(
            name='ProfiloUtente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profilo', models.CharField(choices=[(strt_users.enums.Profilo('Amministratore Portale'), 'Amministratore Portale'), (strt_users.enums.Profilo('Responsabile RUP'), 'Responsabile RUP'), (strt_users.enums.Profilo('Amministratore Ente'), 'Amministratore Ente'), (strt_users.enums.Profilo('Operatore'), 'Operatore')], max_length=21)),
                ('ente', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='strt_users.Ente')),
                ('utente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Profili utente',
            },
        ),
        migrations.CreateModel(
            name='Assegnatario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qualifica_ufficio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='strt_users.QualificaUfficio')),
                ('utente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Assegnatari',
            },
        ),
        migrations.AddConstraint(
            model_name='profiloutente',
            constraint=models.CheckConstraint(check=models.Q(models.Q(_negated=True, profilo=strt_users.enums.Profilo('Amministratore Portale')), models.Q(('profilo', strt_users.enums.Profilo('Amministratore Portale')), ('ente__isnull', True)), _connector='OR'), name='No ENTE for global admins'),
        ),
        migrations.AddConstraint(
            model_name='profiloutente',
            constraint=models.CheckConstraint(check=models.Q(('profilo', strt_users.enums.Profilo('Amministratore Portale')), models.Q(models.Q(_negated=True, profilo=strt_users.enums.Profilo('Amministratore Portale')), ('ente__isnull', False)), _connector='OR'), name='ENTE required for non-admins'),
        ),
    ]
