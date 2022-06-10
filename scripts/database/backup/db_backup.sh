#!/bin/bash
# db_blockchain database backup script

################################################################
################## CONSTANTS DECLARATION  ######################
 
DB_BACKUP_PATH='/Users/marcoscharalambous/testing/db_blockchain'
MYSQL_HOST='127.0.0.1'
MYSQL_PORT='3333'
MYSQL_USER='root'
MYSQL_PASSWORD='Fm)4dj'
DATABASE_NAME='db_blockchain'
TODAY=`date +"%d_%b_%Y"`

#################################################################

mkdir -p ${DB_BACKUP_PATH}/${TODAY}
echo "Backup started for database - ${DATABASE_NAME}"

mysqldump -h ${MYSQL_HOST} \
   -P ${MYSQL_PORT} \
   -u ${MYSQL_USER} \
   -p${MYSQL_PASSWORD} \
   ${DATABASE_NAME} | gzip > ${DB_BACKUP_PATH}/${TODAY}/${DATABASE_NAME}-${TODAY}.sql.gz

if [ $? -eq 0 ]; then
  echo "Database backup successfully completed"
else
  echo "Error found during backup"
  exit 1
fi