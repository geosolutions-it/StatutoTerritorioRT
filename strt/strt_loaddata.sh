#!/bin/bash
set -x

./manage.sh loaddata fixtures/utente.json
./manage.sh loaddata fixtures/ente.json
./manage.sh loaddata fixtures/ufficio.json
./manage.sh loaddata fixtures/qualificaufficio.json.json
./manage.sh loaddata fixtures/assegnatario.json
./manage.sh loaddata fixtures/profiloutente.json
