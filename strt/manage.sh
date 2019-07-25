source <(sed -e /^$/d -e /^#/d -e 's/.*/declare -x "&"/g' /opt/StatutoTerritorioRT/strt/.env); /home/geosolutions/Envs/strt/bin/python /opt/StatutoTerritorioRT/strt/manage.py $@
