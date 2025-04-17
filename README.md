# Epic Events CRM

Une application CRM en ligne de commande pour gérer les clients, contrats et événements d'une entreprise d'organisation d'événements.

## Sommaire
- [Présentation](#présentation)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancer l'application](#lancer-lapplication)
- [Fonctionnalités](#fonctionnalités)
- [Structure du projet](#structure-du-projet)
- [Schéma de la base de données](#schéma-de-la-base-de-données)

## Présentation

Cette application respecte le cahier des charges d'Epic Events et implémente une architecture MVC (Modèle-Vue-Contrôleur).

## Installation

1. Clonez le dépôt :
    ```bash
    git clone https://github.com/ThomasDpr/epic_events_crm.git
    cd epic_events_crm
    ```

2. Créez et activez un environnement virtuel avec pipenv :
    ```bash
    pipenv install
    pipenv shell
    ```

## Configuration

1. Démarrez la base de données PostgreSQL avec Docker :
    ```bash
    docker-compose up -d
    ```

2. Créez un fichier `.env.db` dans le dossier `src/database/` avec le contenu suivant :
    ```
    DATABASE_URL=postgresql://postgres:password@localhost:5432/epic_events
    ```

4. Initialisez la base de données avec Alembic :
    ```bash
    cd src
    alembic upgrade head
    ```

## Lancer l'application

1. Assurez-vous que la base de données est active :
    ```bash
    docker-compose ps
    ```

2. Lancez l'application :
    ```bash
    cd src
    python main.py
    ```

3. À la première utilisation, vous devrez créer un compte administrateur (département gestion).

## Fonctionnalités

### Besoins généraux
- Authentification des utilisateurs
- Gestion des rôles par département
- Stockage et mise à jour des informations clients, contrats et événements
- Accès en lecture seule à toutes les données pour tous les utilisateurs

### Département Gestion
- Création, mise à jour et suppression des utilisateurs
- Création et modification de tous les contrats
- Filtrage des événements sans support assigné
- Assignation de collaborateurs support aux événements

### Département Commercial
- Création et gestion de clients
- Mise à jour des contrats de leurs clients
- Filtrage des contrats non signés ou non payés
- Création d'événements pour les clients avec contrats signés

### Département Support
- Filtrage pour voir uniquement leurs événements assignés
- Mise à jour des événements dont ils sont responsables

## Structure du projet

```
epic_events_crm/
├── docker-compose.yml          # Configuration Docker
├── requirements.txt            # Dépendances Python
└── src/
    ├── app.py                  # Classe principale de l'application
    ├── main.py                 # Point d'entrée de l'application
    ├── components/             # Composants réutilisables
    ├── controllers/            # Contrôleurs pour chaque entité
    ├── core/                   # Fonctionnalités centrales (sécurité, logging)
    ├── database/               # Configuration de la base de données
    │   ├── config.py           # Configuration SQLAlchemy
    │   ├── migrations/         # Migrations Alembic
    │   └── alembic.ini
    ├── models/                 # Modèles SQLAlchemy (User, Client, Contract, Event)
    ├── services/               # Services métier
    ├── tests/                  # Tests unitaires
    ├── utils/                  # Utilitaires divers
    └── views/                  # Vues et interfaces utilisateur
```

## Schéma de la base de données

Voici le schéma relationnel de la base de données, montrant les principales entités et leurs relations :

![Schéma de la base de données](CRM.png)
