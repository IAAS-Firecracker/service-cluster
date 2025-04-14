import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import request, jsonify, current_app
from flask_restx import Namespace, Resource, fields
from app import db, ma

# Définir le modèle de données pour les images système
class SystemImage(db.Model):
    __tablename__ = 'system_images'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    os_type = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name, os_type, version, description=None, image_path=None):
        self.name = name
        self.os_type = os_type
        self.version = version
        self.description = description
        self.image_path = image_path
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

# Schéma pour sérialiser/désérialiser les objets SystemImage
class SystemImageSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'os_type', 'version', 'description', 'image_path', 'created_at', 'updated_at')

# Initialiser les schémas
system_image_schema = SystemImageSchema()
system_images_schema = SystemImageSchema(many=True)

# Définir le chemin de stockage des images
IMAGE_UPLOAD_FOLDER = os.path.join('static', 'img', 'system')

# Fonction pour s'assurer que le dossier de stockage existe
def ensure_upload_folder_exists():
    os.makedirs(os.path.join(current_app.root_path, IMAGE_UPLOAD_FOLDER), exist_ok=True)

# Fonction pour gérer l'upload d'image
def handle_image_upload(file):
    if file:
        # Générer un nom de fichier unique
        filename = secure_filename(file.filename)
        # Ajouter un UUID pour éviter les collisions de noms
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        # S'assurer que le dossier existe
        ensure_upload_folder_exists()
        # Chemin complet pour sauvegarder le fichier
        file_path = os.path.join(current_app.root_path, IMAGE_UPLOAD_FOLDER, unique_filename)
        # Sauvegarder le fichier
        file.save(file_path)
        # Retourner le chemin relatif pour stocker en BD
        return os.path.join(IMAGE_UPLOAD_FOLDER, unique_filename)
    return None

# Fonction pour supprimer une image existante
def delete_image_file(image_path):
    if image_path and os.path.exists(os.path.join(current_app.root_path, image_path)):
        os.remove(os.path.join(current_app.root_path, image_path))

# Créer un namespace pour les routes d'API des images système
ns = Namespace('system-images', description='Opérations sur les images système')

# Définir le modèle pour la documentation Swagger
system_image_model = ns.model('SystemImage', {
    'name': fields.String(required=True, description='Nom de l\'image système'),
    'os_type': fields.String(required=True, description='Type de système d\'exploitation'),
    'version': fields.String(required=True, description='Version du système d\'exploitation'),
    'description': fields.String(required=False, description='Description de l\'image système'),
    'image_path': fields.String(required=False, description='Chemin vers l\'image')
})

@ns.route('/')
class SystemImageList(Resource):
    @ns.doc('list_system_images')
    def get(self):
        """Liste toutes les images système"""
        all_system_images = SystemImage.query.all()
        result = system_images_schema.dump(all_system_images)
        return jsonify(result)
    
    @ns.doc('create_system_image')
    @ns.expect(system_image_model)
    def post(self):
        """Crée une nouvelle image système"""
        # Vérifier si une image a été envoyée
        image_path = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename:
                image_path = handle_image_upload(image_file)
        
        # Récupérer les données JSON ou form-data
        if request.is_json:
            data = request.json
        else:
            data = request.form
        
        new_system_image = SystemImage(
            name=data['name'],
            os_type=data['os_type'],
            version=data['version'],
            description=data.get('description'),
            image_path=image_path
        )
        
        db.session.add(new_system_image)
        
        try:
            db.session.commit()
            return system_image_schema.dump(new_system_image), 201
        except Exception as e:
            # En cas d'erreur, supprimer l'image si elle a été uploadée
            if image_path:
                delete_image_file(image_path)
            db.session.rollback()
            return {'message': str(e)}, 400

@ns.route('/<int:id>')
@ns.param('id', 'L\'identifiant de l\'image système')
class SystemImageDetail(Resource):
    @ns.doc('get_system_image')
    def get(self, id):
        """Obtient une image système par son ID"""
        system_image = SystemImage.query.get_or_404(id)
        return system_image_schema.dump(system_image)
    
    @ns.doc('update_system_image')
    @ns.expect(system_image_model)
    def put(self, id):
        """Met à jour une image système"""
        system_image = SystemImage.query.get_or_404(id)
        
        # Vérifier si une nouvelle image a été envoyée
        old_image_path = system_image.image_path
        new_image_path = old_image_path
        
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename:
                new_image_path = handle_image_upload(image_file)
                # Supprimer l'ancienne image si elle existe
                if old_image_path:
                    delete_image_file(old_image_path)
        
        # Récupérer les données JSON ou form-data
        if request.is_json:
            data = request.json
        else:
            data = request.form
        
        system_image.name = data['name']
        system_image.os_type = data['os_type']
        system_image.version = data['version']
        if 'description' in data:
            system_image.description = data.get('description')
        system_image.image_path = new_image_path
        system_image.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return system_image_schema.dump(system_image)
        except Exception as e:
            # En cas d'erreur, si une nouvelle image a été uploadée, la supprimer
            if new_image_path != old_image_path:
                delete_image_file(new_image_path)
            db.session.rollback()
            return {'message': str(e)}, 400
    
    @ns.doc('delete_system_image')
    def delete(self, id):
        """Supprime une image système"""
        system_image = SystemImage.query.get_or_404(id)
        
        # Sauvegarder le chemin de l'image pour la supprimer après
        image_path = system_image.image_path
        
        try:
            db.session.delete(system_image)
            db.session.commit()
            
            # Supprimer le fichier image si il existe
            if image_path:
                delete_image_file(image_path)
                
            return {'message': 'Image système supprimée avec succès'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

@ns.route('/search/<string:name>')
@ns.param('name', 'Nom de l\'image système à rechercher')
class SystemImageSearch(Resource):
    @ns.doc('search_system_images')
    def get(self, name):
        """Recherche des images système par nom"""
        system_images = SystemImage.query.filter(SystemImage.name.like(f'%{name}%')).all()
        return system_images_schema.dump(system_images)

@ns.route('/os-type/<string:os_type>')
@ns.param('os_type', 'Type de système d\'exploitation')
class SystemImageByOsType(Resource):
    @ns.doc('get_system_images_by_os_type')
    def get(self, os_type):
        """Obtient les images système par type de système d'exploitation"""
        system_images = SystemImage.query.filter_by(os_type=os_type).all()
        return system_images_schema.dump(system_images)

# Fonction pour initialiser les données de test
def seed_system_images():
    try:
        # Vérifier si des données existent déjà
        existing_count = SystemImage.query.count()
        if existing_count > 0:
            print(f"{existing_count} images système existent déjà dans la base de données.")
            return True
        
        # Données de test
        test_images = [
            {
                'name': 'Ubuntu 22.04 LTS',
                'os_type': 'ubuntu-22.04',
                'version': '22.04',
                'description': 'Ubuntu 22.04 LTS (Jammy Jellyfish) est une version LTS (Long Term Support) d\'Ubuntu, offrant 5 ans de support et de mises à jour de sécurité.',
                'image_path': '/images/system/ubuntu-22.04.png'
            },
            {
                'name': 'Ubuntu 24.04 LTS',
                'os_type': 'ubuntu-24.04',
                'version': '24.04',
                'description': 'Ubuntu 24.04 LTS est la dernière version LTS d\'Ubuntu, offrant les dernières fonctionnalités et améliorations.',
                'image_path': '/images/system/ubuntu-24.04.png'
            }
        ]
        
        # Ajouter les images système de test
        for image_data in test_images:
            image = SystemImage(**image_data)
            db.session.add(image)
        
        # Sauvegarder les changements
        db.session.commit()
        print(f"{len(test_images)} images système ajoutées avec succès.")
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'ajout des images système de test: {e}")
        db.session.rollback()
        return False

# Fonction pour enregistrer le namespace dans l'API
def register_routes(api):
    api.add_namespace(ns)


# Nous utilisons plutôt une fonction qui sera appelée manuellement
def create_system_image_tables():
    with app.app_context():
        db.create_all()
        print("Tables créées avec succès system images.")
