for table in utente ente ufficio qualificaufficio assegnatario profiloutente ; do echo DUMPING $table ;   python ../manage.py dumpdata  strt_users.${table}  --indent 3 >  ${table}.json ; done
