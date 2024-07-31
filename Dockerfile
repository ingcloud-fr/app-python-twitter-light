# Utilisez l'image officielle de Python comme image de base
FROM python:3.12-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de l'application dans le répertoire de travail
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port sur lequel l'application va fonctionner
EXPOSE 5000

# Définir la commande par défaut pour exécuter l'application
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:5000", "app:app"]
