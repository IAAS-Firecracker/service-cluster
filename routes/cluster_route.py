#!/usr/bin/env python3
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.model_cluster import ClusterEntity, ClusterCreate, ClusterUpdate, ClusterResponse, VMRequirements
from dotenv import load_dotenv
# Importer les dépendances depuis le fichier dependencies.py
from dependencies import get_db, StandardResponse
import os
import requests

router = APIRouter(
    prefix="/api/service-clusters",
    tags=["Cluster"],
    responses={404: {"description": "Not found"}},
)

# Charger les variables d'environnement avant d'importer les autres modules
load_dotenv()

@router.get("/", response_model=StandardResponse)
def get_clusters(nom: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ClusterEntity)
    if nom:
        query = query.filter(ClusterEntity.nom.like(f'%{nom}%'))
    clusters = query.all()
    clusters_list = [cluster.to_dict() for cluster in clusters]

    if nom:
        message = f"Clusters trouvés pour le nom: {nom}"
    else:
        message = "Liste de tous les clusters"
    
    return StandardResponse(
        statusCode=200,
        message=message,
        data={"clusters": clusters_list}
    )

@router.get('/available', response_model=StandardResponse)
def get_available_clusters(db: Session = Depends(get_db)):
    """Obtient les clusters de service avec des ressources disponibles"""
    try:
        service_clusters = db.query(ClusterEntity).filter(
                ClusterEntity.available_rom > 0,
                ClusterEntity.available_ram > 0,
                ClusterEntity.available_processor > 0
            ).all()
        result = [cluster.to_dict() for cluster in service_clusters]
        return StandardResponse(
            statusCode=200,
            message="Clusters disponibles récupérés avec succès",
            data={"clusters": result}
        )
    except Exception as e:
        return StandardResponse(
            statusCode=500,
            message=f"Erreur lors de la récupération des clusters disponibles: {str(e)}",
            data=None
        )

@router.post("/", response_model=StandardResponse, status_code=status.HTTP_201_CREATED,
             summary="Crée un nouveau cluster",
             description="Les différents paramètres sont: \n- un nom \n- une adresse MAC \n- une IP \n- une ROM \n- une RAM \n- un processeur \n- un nombre de cœurs")
def create_cluster(cluster: ClusterCreate, db: Session = Depends(get_db)):
    """Crée un nouveau cluster"""
    try:
        # Vérifier si un cluster avec le même nom existe déjà
        # Vérifier si un cluster avec cette adresse MAC existe déjà
        existing_cluster = db.query(ClusterEntity).filter(ClusterEntity.adresse_mac == cluster.adresse_mac).first()
        if existing_cluster:
            # Mettre à jour le cluster existant
            existing_cluster.nom = cluster.nom
            existing_cluster.ip = cluster.ip
            existing_cluster.rom = cluster.rom
            existing_cluster.available_rom = cluster.available_rom
            existing_cluster.ram = cluster.ram
            existing_cluster.available_ram = cluster.available_ram
            existing_cluster.processeur = cluster.processeur
            existing_cluster.available_processor = cluster.available_processor
            existing_cluster.number_of_core = cluster.number_of_core
            
            db.add(existing_cluster)
            db.commit()
            db.refresh(existing_cluster)
            
            return StandardResponse(
                statusCode=200,
                message=f"Cluster '{cluster.nom}' mis à jour avec succès",
                data={"cluster": existing_cluster.to_dict()}
            )
        else:
            # Créer une nouvelle entité
            new_cluster = ClusterEntity(
                nom=cluster.nom,
                adresse_mac=cluster.adresse_mac,
                ip=cluster.ip,
                rom=cluster.rom,
                available_rom=cluster.available_rom,
                ram=cluster.ram,
                available_ram=cluster.available_ram,
                processeur=cluster.processeur,
                available_processor=cluster.available_processor,
                number_of_core=cluster.number_of_core
            )
        
            db.add(new_cluster)
            db.commit()
            db.refresh(new_cluster)
        
            return StandardResponse(
                statusCode=201,
                message=f"Cluster '{cluster.nom}' créé avec succès",
                data={"cluster": new_cluster.to_dict()}
            )
    except Exception as e:
        db.rollback()
        return StandardResponse(
            statusCode=400,
            message=f"Erreur lors de la création du cluster: {str(e)}",
            data=None
        )

        

@router.put("/{cluster_id}", response_model=StandardResponse,
             summary="Met à jour un cluster existant",
             description="Paramètres: \n- cluster_id (chemin): L'identifiant unique du cluster à modifier \n- corps de la requête: Un objet JSON contenant les champs à mettre à jour: \n  - nom (optionnel): Le nouveau nom du cluster \n  - adresse_mac (optionnel): La nouvelle adresse MAC \n  - ip (optionnel): La nouvelle IP \n  - rom (optionnel): La nouvelle ROM \n  - available_rom (optionnel): La ROM disponible \n  - ram (optionnel): La nouvelle RAM \n  - available_ram (optionnel): La RAM disponible \n  - processeur (optionnel): Le nouveau processeur \n  - available_processor (optionnel): Le processeur disponible \n  - number_of_core (optionnel): Le nombre de cœurs")
def update_cluster(cluster_id: int, cluster: ClusterUpdate, db: Session = Depends(get_db)):
    """Met à jour un cluster existant"""
    try:
        db_cluster = db.query(ClusterEntity).filter(ClusterEntity.id == cluster_id).first()
        if db_cluster is None:
            return StandardResponse(
                statusCode=404,
                message="Cluster non trouvé",
                data=None
            )
        
        # Mettre à jour les champs
        if cluster.nom is not None:
            db_cluster.nom = cluster.nom
        if cluster.adresse_mac is not None:
            db_cluster.adresse_mac = cluster.adresse_mac
        if cluster.ip is not None:
            db_cluster.ip = cluster.ip
        if cluster.rom is not None:
            db_cluster.rom = cluster.rom
        if cluster.available_rom is not None:
            db_cluster.available_rom = cluster.available_rom
        if cluster.ram is not None:
            db_cluster.ram = cluster.ram
        if cluster.available_ram is not None:
            db_cluster.available_ram = cluster.available_ram
        if cluster.processeur is not None:
            db_cluster.processeur = cluster.processeur
        if cluster.available_processor is not None:
            db_cluster.available_processor = cluster.available_processor
        if cluster.number_of_core is not None:
            db_cluster.number_of_core = cluster.number_of_core
        
        db.commit()
        db.refresh(db_cluster)
        
        return StandardResponse(
            statusCode=200,
            message="Cluster mise à jour avec succès",
            data={"cluster": db_cluster.to_dict()}
        )
    except Exception as e:
        db.rollback()
        return StandardResponse(
            statusCode=400,
            message=f"Erreur lors de la mise à jour du cluster: {str(e)}",
            data=None
        )


@router.delete("/{cluster_id}", response_model=StandardResponse,
               summary="Supprime un cluster existant",
               description="Paramètres: \n- cluster_id (chemin): L'identifiant unique du cluster à supprimer")
def delete_cluster(cluster_id: int, db: Session = Depends(get_db)):
    """Supprime un cluster existant"""
    try:
        db_cluster = db.query(ClusterEntity).filter(ClusterEntity.id == cluster_id).first()
        if db_cluster is None:
            return StandardResponse(
                statusCode=404,
                message="Cluster non trouvé",
                data=None
            )
        
        db.delete(db_cluster)
        db.commit()
        
        return StandardResponse(
            statusCode=200,
            message="Cluster supprimé avec succès",
            data=None
        )
    except Exception as e:
        db.rollback()
        return StandardResponse(
            statusCode=400,
            message=f"Erreur lors de la suppression du cluster: {str(e)}",
            data=None
        )

@router.get("/{cluster_id}", response_model=StandardResponse,
            summary="Récupère un cluster existant",
            description="Paramètres: \n- cluster_id (chemin): L'identifiant unique du cluster à récupérer")
def get_cluster(cluster_id: int, db: Session = Depends(get_db)):
    """Récupère un cluster existant"""
    try:
        db_cluster = db.query(ClusterEntity).filter(ClusterEntity.id == cluster_id).first()
        if db_cluster is None:
            return StandardResponse(
                statusCode=404,
                message="Cluster non trouvé",
                data=None
            )
        
        return StandardResponse(
            statusCode=200,
            message="Cluster récupéré avec succès",
            data={"cluster": db_cluster.to_dict()}
        )
    except Exception as e:
        return StandardResponse(
            statusCode=400,
            message=f"Erreur lors de la récupération du cluster: {str(e)}",
            data=None
        )


@router.post('/find-suitable-host')
def find_suitable_host(vm_requirements: VMRequirements, db: Session = Depends(get_db)):
    """Trouve un hôte approprié pour une nouvelle VM en fonction des ressources requises et transmet la demande"""
    
    # Extraire les exigences de ressources
    cpu_count = vm_requirements.cpu_count
    memory_size_mib = vm_requirements.memory_size_mib
    disk_size_gb = vm_requirements.disk_size_gb
    vm_offer_id = vm_requirements.vm_offer_id
    system_image_id = vm_requirements.system_image_id
        
    # Paramètres additionnels pour la création de VM
    vm_name = vm_requirements.name
    user_id = vm_requirements.user_id
    os_type = vm_requirements.os_type
    root_password = vm_requirements.root_password
        
    # Convertir la mémoire de MiB à GB pour la comparaison
    memory_size_gb = memory_size_mib / 1024
        
    # Calculer le pourcentage de CPU requis (estimation basée sur le nombre de cœurs)
    # Supposons qu'un cœur équivaut à environ 10% de CPU
    cpu_percentage = cpu_count * 10
        
    # Trouver les clusters qui ont suffisamment de ressources disponibles
    suitable_clusters = db.query(ClusterEntity).filter(
            ClusterEntity.available_rom >= disk_size_gb,
            ClusterEntity.available_ram >= memory_size_gb,
            ClusterEntity.available_processor >= cpu_percentage,
            ClusterEntity.number_of_core >= cpu_count
        ).order_by(
            # Trier par la somme des ressources disponibles (pour équilibrer la charge)
            (ClusterEntity.available_rom / ClusterEntity.rom + 
             ClusterEntity.available_ram / ClusterEntity.ram + 
             ClusterEntity.available_processor / 100) / 3
        ).first()
        
    if suitable_clusters:
        host_info = suitable_clusters.to_dict()
            
        # Si tous les paramètres nécessaires pour la création de VM sont présents
        if vm_name and user_id and os_type:
            try:
                # Préparer les données pour la création de VM
                vm_config = {
                    "service_cluster_id": host_info['id'],
                    "name": vm_name,
                    "user_id": user_id,
                    "os_type": os_type,
                    "cpu_count": cpu_count,
                    "memory_size_mib": memory_size_mib,
                    "disk_size_gb": disk_size_gb,
                    "vm_offer_id":vm_offer_id,
                    "system_image_id":system_image_id
                }
                    
                # Ajouter le mot de passe root s'il est fourni
                if root_password:
                    vm_config["root_password"] = root_password
                    
                # Obtenir l'URL du service-vm-host à partir de l'hôte sélectionné
                host_ip = host_info['ip']
                vm_host_port = os.getenv('SERVICE_VM_HOST_PORT', '5003')
                vm_host_url = f"http://{host_ip}:{vm_host_port}/api/service-vm-host/vm/create"
                    
                # Envoyer la requête de création de VM au service-vm-host
                
                response = requests.post(
                    vm_host_url,
                    json=vm_config,
                    headers={"Content-Type": "application/json"},
                    timeout=1500  # Timeout de 5 secondes
                )
                    
                # Vérifier la réponse
                if response.status_code in [200, 201, 202]:
                    # Retourner les informations de l'hôte et la réponse de création de VM
                    return StandardResponse(
                        statusCode=200,
                        message="VM créée avec succès",
                        data={
                            "host": host_info,
                            "vm_creation": response.json()
                        }
                    )
                else:
                    # En cas d'échec de création de VM, retourner l'erreur
                    return StandardResponse(
                        statusCode=500,
                        message=f"Erreur lors de la création de VM: {response.status_code} - {response.text}",
                        data=None
                    )
                        
            except Exception as e:
                # En cas d'erreur lors de la requête, retourner l'hôte mais avec un message d'erreur
                return StandardResponse(
                    statusCode=500,
                    message=f"Erreur lors de la communication avec le service-vm-host: {str(e)}",
                    data=None
                )
            
        else:
            return StandardResponse(
                statusCode=404,
                message="Aucun hôte avec suffisamment de ressources disponibles n'a été trouvé",
                data=None
            )

