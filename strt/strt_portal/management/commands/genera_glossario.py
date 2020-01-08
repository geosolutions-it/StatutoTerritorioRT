import os
import json
from django.conf import settings
from django.template.loader import render_to_string
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    args = ""
    help = """Genera HTML dei termini glossario"""

    def handle(self, *args, **options):
        glossario_dir = os.path.join(settings.BASE_DIR,'templates/strt_portal/glossary')
        glossario_file = os.path.join(glossario_dir,"glossario.json")
        template_input = "strt_portal/glossary/termini_template.html"
        template_output = os.path.join(glossario_dir,'termini.html')

        glossario = None

        with open(glossario_file,'r') as glossario_json:
            glossario = json.load(glossario_json)

        context = {
            'denominazione': "Abaco delle invarianti",
            'definizione': 'Le quattro invarianti strutturali, definita all\'art.6 della Disciplina del PIT-PPR, sono descritte nel documento "Abachi delle invarianti", ' +
                           'attraverso l\'individuazione dei caratteri, dei valori, delle criticità e con indicazioni per le azioni con riferimento ad ogni morfotipo ' +
                           'in cui esse risultano articolate, e sono contestualizzate nelle schede d\'ambito.' +
                           'Gli abachi delle invarianti rappresentano lo strumento conoscitivo e il riferimento tecnico-operativo per l\'elaborazione degli strumenti della pianificazione territoriale e urbanistica. (art. 6 commi 4 e 5 della Disciplina del PIT-PPR).',
            'glossario': glossario
        }
        message = render_to_string(
            template_input,
            context
        )
        with open(template_output,"w") as fout:
            fout.write(message)

        print(f"Generato {template_output}")
