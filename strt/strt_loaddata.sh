#!/bin/bash
set -x

./manage.sh loaddata fixtures/strt_enti.json
./manage.sh loaddata fixtures/strt_tipi_di_ente.json
./manage.sh loaddata fixtures/strt_tipi_di_ruolo.json
./manage.sh loaddata fixtures/strt_utenti_di_test.json
./manage.sh loaddata fixtures/serapide_core_modello_fase.json
./manage.sh loaddata fixtures/serapide_core_modello_contatto.json
