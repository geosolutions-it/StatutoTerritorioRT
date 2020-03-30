#!/bin/bash
set -x

rm -Rf _tmp_
mkdir _tmp_

./manage.sh dumpdata fixtures/utente.json > _tmp_/utente.json
./manage.sh dumpdata fixtures/ente.json > _tmp_/ente.json
./manage.sh dumpdata fixtures/ufficio.json > _tmp_/ufficio.json
./manage.sh dumpdata fixtures/qualificaufficio.json.json > _tmp_/qualificaufficio.json.json
./manage.sh dumpdata fixtures/assegnatario.json > _tmp_/assegnatario.json
./manage.sh dumpdata fixtures/profiloutente.json > _tmp_/profiloutente.json

python -m json.tool _tmp_/utente.json > fixtures/utente.json
python -m json.tool _tmp_/ente.json > fixtures/ente.json
python -m json.tool _tmp_/ufficio.json > fixtures/ufficio.json
python -m json.tool _tmp_/qualificaufficio.json.json > fixtures/qualificaufficio.json.json
python -m json.tool _tmp_/assegnatario.json > fixtures/assegnatario.json
python -m json.tool _tmp_/profiloutente.json > fixtures/profiloutente.json

