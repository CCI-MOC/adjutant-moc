#!/usr/bin/env bash
set -e

cd /app

>&2 echo "Waiting for database..."

while ! echo exit | nc $DB_HOST 3306; do sleep 5; done

>&2 echo "Database is up - Starting"

adjutant-api migrate
adjutant-api runserver 0.0.0.0:8080
