#!/usr/bin/env python3
import os
import sys
import dotenv
import pymysql
import logging

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement avant d'importer les autres modules
dotenv.load_dotenv()

# Importer et exécuter les configurations depuis settings.py
logger.info("Chargement des configurations depuis settings.py...")
try:
    from config import settings
    logger.info("Configurations chargées avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement des configurations: {e}")

# Fonction pour initialiser la base de données
def init_database():
    try:
        logger.info("Initialisation de la base de données...")
        # Récupérer les informations de connexion depuis les variables d'environnement
        # Ces variables ont été mises à jour par settings.py
        mysql_host = os.getenv('MYSQL_HOST')
        mysql_port = int(os.getenv('MYSQL_PORT'))
        mysql_user = os.getenv('MYSQL_USER')
        mysql_password = os.getenv('MYSQL_PASSWORD')
        mysql_db = os.getenv('MYSQL_DB')
        
        logger.info(f"Connexion à MySQL: {mysql_host}:{mysql_port} avec l'utilisateur {mysql_user}")
        
        # Créer la base de données si elle n'existe pas
        conn = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password
        )
        
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_db}")
        conn.commit()
        
        logger.info(f"Base de données '{mysql_db}' créée ou déjà existante.")
        
        cursor.close()
        conn.close()

        from app import create_tables
        
        # Utiliser la fonction create_tables définie dans app.py
        create_tables()
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")
        return False

# Fonction pour ajouter des données de test
def seed_database():
    try:
        logger.info("Ajout des données de test...")
        from app import app, db, ServiceCluster
        
        # Données de test
        test_clusters = [
            {
                'nom': 'Cluster-1',
                'adresse_mac': '00:1A:2B:3C:4D:5E',
                'ip': '192.168.1.100',
                'rom': 1000,
                'available_rom': 800,
                'ram': 64,
                'available_ram': 48,
                'processeur': 'Intel Xeon E5-2680',
                'available_processor': 75.5,
                'number_of_core': 12
            },
            {
                'nom': 'Cluster-2',
                'adresse_mac': '00:1A:2B:3C:4D:5F',
                'ip': '192.168.1.101',
                'rom': 2000,
                'available_rom': 1500,
                'ram': 128,
                'available_ram': 96,
                'processeur': 'AMD EPYC 7742',
                'available_processor': 85.0,
                'number_of_core': 64
            },
            {
                'nom': 'Cluster-3',
                'adresse_mac': '00:1A:2B:3C:4D:60',
                'ip': '192.168.1.102',
                'rom': 500,
                'available_rom': 200,
                'ram': 32,
                'available_ram': 16,
                'processeur': 'Intel Xeon E7-8890',
                'available_processor': 50.0,
                'number_of_core': 24
            }
        ]
        
        with app.app_context():
            # Vérifier si des données existent déjà
            existing_count = ServiceCluster.query.count()
            if existing_count > 0:
                logger.info(f"{existing_count} clusters existent déjà dans la base de données.")
                return True
            
            # Ajouter les clusters de test
            for cluster_data in test_clusters:
                cluster = ServiceCluster(**cluster_data)
                db.session.add(cluster)
            
            # Sauvegarder les changements
            db.session.commit()
            logger.info(f"{len(test_clusters)} clusters ajoutés avec succès.")
            
            return True
            
    except Exception as e:
        print(f"Erreur lors de l'ajout des données de test: {e}")
        return False

# Point d'entrée principal
if __name__ == '__main__':
    # Les configurations ont déjà été chargées depuis settings.py
    # Récupérer le port de l'application depuis les variables d'environnement
    app_port = int(os.getenv('APP_PORT', 5000))
    logger.info(f"Port de l'application configuré: {app_port}")
    
    # Initialiser la base de données
    if init_database():
        # Ajouter des données de test
        seed_database()
        
        # Importer l'application Flask et la démarrer
        from app import app
        logger.info(f"Démarrage de l'application sur le port {app_port}...")
        app.run(debug=True, host='0.0.0.0', port=app_port)
    else:
        logger.error("Impossible de démarrer l'application en raison d'erreurs d'initialisation.")
        sys.exit(1)
