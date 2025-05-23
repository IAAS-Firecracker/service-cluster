#!/usr/bin/env python3
import os
import sys
import pymysql
import logging
import uuid
import shutil
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from config.eureka_client import register_with_eureka, shutdown_eureka
from routes.cluster_route import router as cluster_router
from config.settings import load_config
from database import create_tables, init_database, seed_database

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement avant d'importer les autres modules
load_dotenv()

# Importer et exécuter les configurations depuis settings.py si disponible
logger.info("Chargement des configurations...")
try:
    load_config()
    logger.info("Configurations chargées avec succès")
except ImportError:
    logger.warning("Module config.settings non trouvé, utilisation des variables d'environnement par défaut")
except Exception as e:
    logger.error(f"Erreur lors du chargement des configurations: {e}")

# Initialiser l'application FastAPI
app = FastAPI(
    title="Service Cluster API",
    description="API pour gérer les clusters de services et les images système",
    version="1.0.0",
    docs_url="/swagger"
)

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    
# Eureka lifecycle events
@app.on_event("startup")
async def startup_event():
    # Initialiser la base de données
    if init_database():
        #creation de la base de donnee
        create_tables()
        seed_database()
    await register_with_eureka()

@app.on_event("shutdown")
async def shutdown_event():
    await shutdown_eureka()



# Endpoint de santé pour Eureka
@app.get('/api/service-clusters/health', tags=['Système'])
def health_check():
    """Endpoint de vérification de santé pour Eureka"""
    return {"status": "UP"}

@app.get("/api/service-clusters/info")
def info():
    return {
        "app": os.getenv('APP_NAME', 'service-cluster'),
        "version": app.version
    }

# Inclure les routers
app.include_router(cluster_router)


# Point d'entrée principal
if __name__ == '__main__':
    # Récupérer le port de l'application depuis les variables d'environnement
    app_port = int(os.getenv('APP_PORT', 5000))
    logger.info(f"Port de l'application configuré: {app_port}")
    
    # Initialiser la base de données
    if init_database():
        #creation de la base de donnee
        create_tables()
        #seed_test_data()
        # Démarrer l'application FastAPI avec uvicorn
        import uvicorn
        logger.info(f"Démarrage de l'application FastAPI sur le port {app_port}...")
        uvicorn.run("app:app", host="0.0.0.0", port=app_port, reload=True)
    else:
        logger.error("Impossible de démarrer l'application en raison d'erreurs d'initialisation.")
        sys.exit(1)
