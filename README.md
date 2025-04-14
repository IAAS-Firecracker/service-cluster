# Service Cluster API

Une API Flask pour gérer les clusters de services dans le cadre du projet Tsore-Iaas-Firecracker.

## Fonctionnalités

- API RESTful complète pour gérer les clusters de services
- Documentation Swagger intégrée
- Connexion à une base de données MySQL
- Gestion des ressources (RAM, ROM, processeur)

## Structure de la base de données

Table `service_cluster` avec les champs suivants :
- `id` : Identifiant unique
- `nom` : Nom du cluster
- `adresse_mac` : Adresse MAC du cluster
- `ip` : Adresse IP du cluster
- `rom` : Capacité ROM totale (en GB)
- `available_rom` : ROM disponible (en GB)
- `ram` : Capacité RAM totale (en GB)
- `available_ram` : RAM disponible (en GB)
- `processeur` : Type de processeur
- `available_processor` : Processeur disponible (en pourcentage)
- `number_of_core` : Nombre de cœurs

## Installation

1. Cloner le dépôt :
```
git clone <repository-url>
cd Tsore-Iaas-Firecracker/service-cluster
```

2. Créer un environnement virtuel et l'activer :
```
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

3. Installer les dépendances :
```
pip install -r requirements.txt
```

4. Configurer la base de données :
   - Créer une base de données MySQL nommée `service_cluster_db`
   - Modifier le fichier `.env` avec vos informations de connexion

5. Initialiser la base de données :
```
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Utilisation

1. Démarrer le serveur :
```
python3 app.py
```

2. Accéder à l'API :
   - API : http://localhost:5000/api/service-clusters
   - Documentation Swagger : http://localhost:5000/swagger

## Endpoints API

- `GET /api/service-clusters` : Liste tous les clusters de services
- `POST /api/service-clusters` : Crée un nouveau cluster de service
- `GET /api/service-clusters/<id>` : Obtient un cluster de service par son ID
- `PUT /api/service-clusters/<id>` : Met à jour un cluster de service
- `DELETE /api/service-clusters/<id>` : Supprime un cluster de service
- `GET /api/service-clusters/search/<nom>` : Recherche des clusters de service par nom
- `GET /api/service-clusters/available` : Obtient les clusters de service avec des ressources disponibles
