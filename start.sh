#!/bin/bash
# Script de démarrage pour Render

# Exécuter le seeding de la base de données
echo "Initializing database..."
python seed_data.py

# Ajouter les lectures de test
echo "Adding sample readings..."
python seed_readings.py

# Démarrer le serveur uvicorn
echo "Starting server..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
