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
    cpu_count: int
    memory_size_mib: int
    disk_size_gb: int
    name: Optional[str] = None
    user_id: Optional[str] = None
    os_type: Optional[str] = None
    root_password: Optional[str] = None
    vm_offer_id: str
    system_image_id: str
    
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
    nom: Optional[str] = None
    adresse_mac: Optional[str] = None
    ip: Optional[str] = None
    rom: Optional[int] = None
    available_rom: Optional[int] = None
    ram: Optional[int] = None
    available_ram: Optional[int] = None
    processeur: Optional[str] = None
    available_processor: Optional[float] = None
    number_of_core: Optional[int] = None
    

class ClusterResponse(ClusterBase):
    id: int
    
    class Config:
        from_attributes = True

