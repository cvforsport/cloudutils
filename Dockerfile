# Utiliser une image de base officielle de Python
FROM python:3.8-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de configuration dans le conteneur
COPY requirements.txt requirements.txt

# Installer les dépendances nécessaires
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Installer AWS CLI
RUN apt-get update && \
    apt-get install -y awscli

# Copier le script d'entraînement dans le conteneur
COPY train.py train.py

# Spécifier le point d'entrée du conteneur
ENTRYPOINT ["python", "train.py"]