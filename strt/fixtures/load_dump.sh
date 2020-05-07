for table in utente ente ufficio qualificaufficio assegnatario profiloutente ; do  python ../manage.py loaddata ${table}.json ; done
