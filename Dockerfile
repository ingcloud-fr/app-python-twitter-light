# Utiliser une image de base officielle de Python
FROM python:3.12-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY . .

# Exposer le port sur lequel l'application va s'exécuter
EXPOSE 5000

# Définir la commande par défaut pour exécuter l'application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]