#!/usr/bin/env bash
# build.sh
set -o errexit

pip install -r requirements.txt

# Inicializar base de datos
python -c "
from app import create_app
from app.models.models import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Base de datos inicializada')
"