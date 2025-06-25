#!/usr/bin/env python3
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, func, Enum, Float
from pydantic import BaseModel
from database import Base


# Définir le modèle de données
class ClusterEntity(Base):
    __tablename__ = 'service_cluster'
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    adresse_mac = Column(String(17), unique=True, nullable=False)
    ip = Column(String(15), unique=True, nullable=False)
    rom = Column(Integer, nullable=False)  # en GB
    available_rom = Column(Integer, nullable=False)  # en GB
    ram = Column(Integer, nullable=False)  # en GB
    available_ram = Column(Integer, nullable=False)  # en GB
    processeur = Column(String(100), nullable=False)
    available_processor = Column(Float, nullable=False)  # en pourcentage
    number_of_core = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'adresse_mac': self.adresse_mac,
            'ip': self.ip,
            'rom': self.rom,
            'available_rom': self.available_rom,
            'ram': self.ram,
            'available_ram': self.available_ram,
            'processeur': self.processeur,
            'available_processor': self.available_processor,
            'number_of_core': self.number_of_core
        }

class VMRequirements(BaseModel):
    cpu_count: int =2 # nombre de cœurs
    memory_size_mib: int =2048 # en Mo
    disk_size_gb: int =5 # en Go
    name: Optional[str] = "" # nom de la VM
    user_id: Optional[str] = "1" # id de l'utilisateur
    os_type: Optional[str] = "ubuntu-24.04" # type d'OS
    root_password: Optional[str] = "password" # mot de passe root
    vm_offer_id: int = 1 # id de l'offre de VM
    system_image_id: int = 2 # id de l'image de système
    
class ClusterBase(BaseModel):
    nom: str
    adresse_mac: str
    ip: str
    rom: int
    available_rom: int
    ram: int
    available_ram: int
    processeur: str
    available_processor: float
    number_of_core: int
    

class ClusterCreate(ClusterBase):
    pass

class ClusterUpdate(ClusterBase):
    nom: Optional[str] = "" # nom du cluster
    adresse_mac: Optional[str] = "" # adresse MAC du cluster
    ip: Optional[str] = "" # IP du cluster
    rom: Optional[int] = 0 # ROM du cluster
    available_rom: Optional[int] = 0 # ROM disponible du cluster
    ram: Optional[int] = 0 # RAM du cluster
    available_ram: Optional[int] = 0 # RAM disponible du cluster
    processeur: Optional[str] = "" # processeur du cluster
    available_processor: Optional[float] = 0 # processeur disponible du cluster
    number_of_core: Optional[int] = 0 # nombre de cœurs du cluster
    

class ClusterResponse(ClusterBase):
    id: int
    
    class Config:
        from_attributes = True

