#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input

# Retry migrations to handle transient DB startup/network issues.
for i in 1 2 3 4 5; do
  if python manage.py migrate --no-input; then
    break
  fi
  echo "Migration attempt $i failed, retrying..."
  sleep 5
done
