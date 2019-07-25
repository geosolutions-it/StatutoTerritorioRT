#!/bin/bash
set -x

rm -Rf _tmp_
mkdir _tmp_

./manage.sh dumpdata strt_users.organization > _tmp_/strt_enti.json
./manage.sh dumpdata strt_users.organizationType > _tmp_/strt_tipi_di_ente.json
./manage.sh dumpdata strt_users.membershipType > _tmp_/strt_tipi_di_ruolo.json
./manage.sh dumpdata strt_users.appUser strt_users.userMembership > _tmp_/strt_utenti_di_test.json
./manage.sh dumpdata modello.fase > _tmp_/serapide_core_modello_fase.json
./manage.sh dumpdata modello.contatto > _tmp_/serapide_core_modello_contatto.json
 
python -m json.tool _tmp_/strt_enti.json > fixtures/strt_enti.json
python -m json.tool _tmp_/strt_tipi_di_ente.json > fixtures/strt_tipi_di_ente.json
python -m json.tool _tmp_/strt_tipi_di_ruolo.json > fixtures/strt_tipi_di_ruolo.json
python -m json.tool _tmp_/strt_utenti_di_test.json > fixtures/strt_utenti_di_test.json
python -m json.tool _tmp_/serapide_core_modello_fase.json > fixtures/serapide_core_modello_fase.json
python -m json.tool _tmp_/serapide_core_modello_contatto.json > fixtures/serapide_core_modello_contatto.json
