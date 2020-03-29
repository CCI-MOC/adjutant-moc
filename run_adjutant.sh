#!/usr/bin/env bash
set -e

cd /app

while ! mysqladmin ping -h $DB_HOST --silent; do
    >&2 echo "Waiting for database"
    sleep 1
done

>&2 echo "Database is up - Starting"

adjutant-api migrate
adjutant-api runserver 0.0.0.0:8080
