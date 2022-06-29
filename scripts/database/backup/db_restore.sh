#!/bin/bash
# db_blockchain database restoration script

################################################################
################## CONSTANTS DECLARATION  ######################
 
DB_BACKUP_PATH='/Users/marcoscharalambous/thesis_test/db_blockchain/<INSERT DATE>'
MYSQL_HOST='127.0.0.1'
MYSQL_PORT='3333'
MYSQL_USER='root'
MYSQL_PASSWORD='Fm)4dj'
DATABASE_NAME='db_blockchain'

#################################################################

echo "Restore backup to database - ${DATABASE_NAME}"

myloader -h ${MYSQL_HOST} \
   -P ${MYSQL_PORT} \
   -u ${MYSQL_USER} \
   --password ${MYSQL_PASSWORD} \
   --threads=8 \
   --directory=${DB_BACKUP_PATH}

if [ $? -eq 0 ]; then
  echo "Database restoration successfully completed"
else
  echo "Error found during restoration"
  exit 1
fi