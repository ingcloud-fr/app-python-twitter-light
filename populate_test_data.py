# source venv/bin/activate  # Activez votre environnement virtuel
# python populate_test_data.py

from werkzeug.security import generate_password_hash
from app import db, User, Article, app  # Assurez-vous d'importer `app`
from datetime import datetime, timezone

# Définir les auteurs
authors = [
    {"username": "author1", "email": "author1@example.com", "password": "author1@example.com"},
    {"username": "author2", "email": "author2@example.com", "password": "author2@example.com"},
    {"username": "author3", "email": "author3@example.com", "password": "author3@example.com"},
    {"username": "author4", "email": "author4@example.com", "password": "author4@example.com"},
    {"username": "author5", "email": "author5@example.com", "password": "author5@example.com"},
    {"username": "author6", "email": "author6@example.com", "password": "author6@example.com"},
]

# Définir les articles
articles = [
    {"title": "Article 1", "category": "Sciences", "content": "Contenu de l'article 1", "author_email": "author1@example.com"},
    {"title": "Article 2", "category": "Histoire", "content": "Contenu de l'article 2", "author_email": "author2@example.com"},
    {"title": "Article 3", "category": "Nature", "content": "Contenu de l'article 3", "author_email": "author3@example.com"},
    {"title": "Article 4", "category": "People", "content": "Contenu de l'article 4", "author_email": "author4@example.com"},
    {"title": "Article 5", "category": "Sciences", "content": "Contenu de l'article 5", "author_email": "author5@example.com"},
    {"title": "Article 6", "category": "Histoire", "content": "Contenu de l'article 6", "author_email": "author6@example.com"},
    {"title": "Article 7", "category": "Nature", "content": "Contenu de l'article 7", "author_email": "author1@example.com"},
    {"title": "Article 8", "category": "People", "content": "Contenu de l'article 8", "author_email": "author2@example.com"},
    {"title": "Article 9", "category": "Sciences", "content": "Contenu de l'article 9", "author_email": "author3@example.com"},
    {"title": "Article 10", "category": "Histoire", "content": "Contenu de l'article 10", "author_email": "author4@example.com"},
]

with app.app_context():  # Utiliser le contexte de l'application
    # Ajouter les auteurs à la base de données
    for author in authors:
        hashed_password = generate_password_hash(author["password"], method='pbkdf2:sha256')
        user = User(username=author["username"], email=author["email"], password=hashed_password)
        db.session.add(user)

    db.session.commit()

    # Ajouter les articles à la base de données
    for article in articles:
        author = User.query.filter_by(email=article["author_email"]).first()
        new_article = Article(title=article["title"], category=article["category"], content=article["content"], author_id=author.id, created_at=datetime.now(timezone.utc))
        db.session.add(new_article)

    db.session.commit()
