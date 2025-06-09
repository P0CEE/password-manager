# Password Manager

Une application sécurisée de gestion de mots de passe développée avec Flask, permettant aux utilisateurs de stocker, générer et partager leurs mots de passe de manière sécurisée.

## Fonctionnalités

- **Stockage sécurisé**: Tous les mots de passe sont chiffrés avec AES-256
- **Générateur de mots de passe**: Créez des mots de passe aléatoires et robustes
- **Partage sécurisé**: Partagez vos mots de passe via des liens temporaires
- **Interface intuitive**: Interface utilisateur simple et efficace

## Prérequis

- Python 
- Docker
- pip 

## Installation et démarrage

### Étape préalable: Configuration du fichier .env

1. Copiez le fichier `.env.dist` en `.env`

2. Générez une clé secrète pour votre application

   ```bash
   openssl rand -base64 32
   ```

   Copiez la clé générée et collez-la dans votre fichier `.env` :

   ```env
   SECRET_KEY=secret_key
   ```

### macOS et Linux

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votre-utilisateur/password-manager.git
   cd password-manager
   ```

2. **Créer et activer un environnement virtuel**
   ```bash
   python -m venv env
   source env/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Démarrer la base de données PostgreSQL avec Docker**
   ```bash
   chmod +x start-database.sh  
   ./start-database.sh
   ```
   Ce script va:
   - Démarrer un conteneur Docker PostgreSQL
   - Créer une base de données `password-manager`
   - Configurer les identifiants de connexion

5. **Initialiser la base de données**
   ```bash
   flask db upgrade
   ```

6. **Lancer l'application**
   ```bash
   flask run
   ```

7. **Accéder à l'application**
   Ouvrez votre navigateur et accédez à `http://127.0.0.1:5000`

## Sécurité

Cette application utilise:
- Chiffrement AES-256 pour les mots de passe stockés
- Génération de tokens sécurisés pour les liens de partage
- Hachage des mots de passe utilisateurs (authentification)
- Sessions sécurisées

## Structure du projet

```
password-manager/
├── app/                    # Code principal de l'application
│   ├── models/             # Modèles de données
│   ├── routes/             # Routes de l'application
│   ├── services/           # Services et logiques métier
│   ├── static/             # Assets statiques (CSS, JS)
│   └── templates/          # Templates HTML
├── migrations/             # Migrations de base de données
├── .env                    # Variables d'environnement
├── app.py                  # Point d'entrée de l'application
├── requirements.txt        # Dépendances du projet
└── start-database.sh       # Script de démarrage de la base de données
```

