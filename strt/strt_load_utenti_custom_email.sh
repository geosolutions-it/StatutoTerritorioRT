#!/bin/bash
set -x

sed -e 's/"email": "\(.*\)",/"email": "'$1'",/g' fixtures/strt_utenti_di_test.json > tmp.json

./manage.sh loaddata tmp.json
