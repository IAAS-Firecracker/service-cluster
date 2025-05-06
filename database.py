#!/usr/bin/env python3
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging
import pymysql
from models import *
from sqlalchemy.orm import Session
from dependencies import get_db, StandardResponse


# Charger les variables d'environnement
load_dotenv()

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration de la base de données
DATABASE_URL = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB', 'service_procedure_workflow_courrier_db')}"

# Créer le moteur SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Fonction pour créer les tables dans la base de données
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès")

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Fonction pour initialiser la base de données
def init_database():
    try:
        logger.info("Initialisation de la base de données...")
        # Récupérer les informations de connexion depuis les variables d'environnement
        mysql_host = os.getenv('MYSQL_HOST')
        mysql_port = int(os.getenv('MYSQL_PORT'))
        mysql_user = os.getenv('MYSQL_USER')
        mysql_password = os.getenv('MYSQL_PASSWORD')
        mysql_database = os.getenv('MYSQL_DB', 'service_cluster_db')
        
        logger.info(f"Connexion à MySQL: {mysql_host}:{mysql_port} avec l'utilisateur {mysql_user}")
        
        # Créer la base de données si elle n'existe pas
        conn = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password
        )
        
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {mysql_database}")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_database}")
        conn.commit()
        
        logger.info(f"Base de données '{mysql_database}' créée ou déjà existante.")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        return False


# Fonction pour ajouter des données de test
def seed_database():
    try:
        logger.info("Ajout des données de test...")
        db = get_db()
        
        
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
        
        with db():
            # Vérifier si des données existent déjà
            existing_count = ClusterEntity.query.count()
            if existing_count > 0:
                logger.info(f"{existing_count} clusters existent déjà dans la base de données.")
                return True
            
            # Ajouter les clusters de test
            for cluster_data in test_clusters:
                cluster = ClusterEntity(**cluster_data)
                db.session.add(cluster)
            
            # Sauvegarder les changements
            db.session.commit()
            logger.info(f"{len(test_clusters)} clusters ajoutés avec succès.")
            
            return True
            
    except Exception as e:
        print(f"Erreur lors de l'ajout des données de test: {e}")
        return False
