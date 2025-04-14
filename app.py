import os
from typing_extensions import Required
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restx import Api, Resource, fields
from dotenv import load_dotenv
import pymysql

# Configurer PyMySQL pour qu'il se comporte comme mysqlclient
pymysql.install_as_MySQLdb()

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Initialiser l'application Flask
app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialiser les extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

# Initialiser Swagger avec flask-restx
api = Api(app, version='1.0', title='Service Cluster API',
          description='API pour gérer les clusters de services et les images système',
          doc='/swagger')

# Définir le modèle de données
class ServiceCluster(db.Model):
    __tablename__ = 'service_cluster'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    adresse_mac = db.Column(db.String(17), unique=True, nullable=False)
    ip = db.Column(db.String(15), unique=True, nullable=False)
    rom = db.Column(db.Integer, nullable=False)  # en GB
    available_rom = db.Column(db.Integer, nullable=False)  # en GB
    ram = db.Column(db.Integer, nullable=False)  # en GB
    available_ram = db.Column(db.Integer, nullable=False)  # en GB
    processeur = db.Column(db.String(100), nullable=False)
    available_processor = db.Column(db.Float, nullable=False)  # en pourcentage
    number_of_core = db.Column(db.Integer, nullable=False)
    
    def __init__(self, nom, adresse_mac, ip, rom, available_rom, ram, available_ram, 
                 processeur, available_processor, number_of_core):
        self.nom = nom
        self.adresse_mac = adresse_mac
        self.ip = ip
        self.rom = rom
        self.available_rom = available_rom
        self.ram = ram
        self.available_ram = available_ram
        self.processeur = processeur
        self.available_processor = available_processor
        self.number_of_core = number_of_core

# Schéma pour sérialiser/désérialiser les objets ServiceCluster
class ServiceClusterSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nom', 'adresse_mac', 'ip', 'rom', 'available_rom', 'ram', 
                  'available_ram', 'processeur', 'available_processor', 'number_of_core')

# Initialiser les schémas
service_cluster_schema = ServiceClusterSchema()
service_clusters_schema = ServiceClusterSchema(many=True)

# Modèle Swagger pour ServiceCluster
service_cluster_model = api.model('ServiceCluster', {
    'nom': fields.String(required=True, description='Nom du cluster'),
    'adresse_mac': fields.String(required=True, description='Adresse MAC'),
    'ip': fields.String(required=True, description='Adresse IP'),
    'rom': fields.Integer(required=True, description='Capacité ROM en GB'),
    'available_rom': fields.Integer(required=True, description='ROM disponible en GB'),
    'ram': fields.Integer(required=True, description='Capacité RAM en GB'),
    'available_ram': fields.Integer(required=True, description='RAM disponible en GB'),
    'processeur': fields.String(required=True, description='Type de processeur'),
    'available_processor': fields.Float(required=True, description='Processeur disponible en pourcentage'),
    'number_of_core': fields.Integer(required=True, description='Nombre de cœurs')
})

# Modèle Swagger pour les exigences de VM
vm_requirements_model = api.model('VMRequirements', {
    'cpu_count': fields.Integer(required=True, description='Nombre de cœurs CPU requis'),
    'memory_size_mib': fields.Integer(required=True, description='Taille de mémoire requise en MiB'),
    'disk_size_gb': fields.Integer(required=True, description='Taille de disque requise en GB'),
    'name': fields.String(required=False, description='Nom de la VM'),
    'user_id': fields.String(required=False, description='ID de l\'utilisateur'),
    'os_type': fields.String(required=False, description='Type de système d\'exploitation'),
    'root_password': fields.String(required=False, description='Mot de passe root'),
    'vm_offer_id': fields.String(required=True, description="Offre de la VM"),
    'system_image_id': fields.String(Required=True,description="Image system")
})

# Namespace pour les endpoints
ns = api.namespace('api/service-clusters', description='Opérations sur les clusters de services')

# Namespace pour la santé de l'application
health_ns = api.namespace('api/health', description='Vérification de la santé de l\'application')

# Endpoints CRUD
@ns.route('/')
class ServiceClusterList(Resource):
    @ns.doc('list_service_clusters')
    def get(self):
        """Liste tous les clusters de services"""
        all_service_clusters = ServiceCluster.query.all()
        result = service_clusters_schema.dump(all_service_clusters)
        return jsonify(result)
    
    @ns.doc('create_service_cluster')
    @ns.expect(service_cluster_model)
    def post(self):
        """Crée un nouveau cluster de service ou met à jour un cluster existant si l'adresse MAC existe déjà"""
        data = request.json
        
        # Vérifier si un cluster avec cette adresse MAC existe déjà
        existing_cluster = ServiceCluster.query.filter_by(adresse_mac=data['adresse_mac']).first()
        
        if existing_cluster:
            # Mettre à jour le cluster existant
            existing_cluster.nom = data['nom']
            existing_cluster.ip = data['ip']
            existing_cluster.rom = data['rom']
            existing_cluster.available_rom = data['available_rom']
            existing_cluster.ram = data['ram']
            existing_cluster.available_ram = data['available_ram']
            existing_cluster.processeur = data['processeur']
            existing_cluster.available_processor = data['available_processor']
            existing_cluster.number_of_core = data['number_of_core']
            
            service_cluster = existing_cluster
            status_code = 200  # OK - Ressource mise à jour
        else:
            # Créer un nouveau cluster
            service_cluster = ServiceCluster(
                nom=data['nom'],
                adresse_mac=data['adresse_mac'],
                ip=data['ip'],
                rom=data['rom'],
                available_rom=data['available_rom'],
                ram=data['ram'],
                available_ram=data['available_ram'],
                processeur=data['processeur'],
                available_processor=data['available_processor'],
                number_of_core=data['number_of_core']
            )
            db.session.add(service_cluster)
            status_code = 201  # Created - Nouvelle ressource créée
        
        try:
            db.session.commit()
            return service_cluster_schema.dump(service_cluster), status_code
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

@ns.route('/<int:id>')
@ns.param('id', 'L\'identifiant du cluster de service')
class ServiceClusterDetail(Resource):
    @ns.doc('get_service_cluster')
    def get(self, id):
        """Obtient un cluster de service par son ID"""
        service_cluster = ServiceCluster.query.get_or_404(id)
        return service_cluster_schema.dump(service_cluster)
    
    @ns.doc('update_service_cluster')
    @ns.expect(service_cluster_model)
    def put(self, id):
        """Met à jour un cluster de service"""
        service_cluster = ServiceCluster.query.get_or_404(id)
        data = request.json
        
        service_cluster.nom = data['nom']
        service_cluster.adresse_mac = data['adresse_mac']
        service_cluster.ip = data['ip']
        service_cluster.rom = data['rom']
        service_cluster.available_rom = data['available_rom']
        service_cluster.ram = data['ram']
        service_cluster.available_ram = data['available_ram']
        service_cluster.processeur = data['processeur']
        service_cluster.available_processor = data['available_processor']
        service_cluster.number_of_core = data['number_of_core']
        
        try:
            db.session.commit()
            return service_cluster_schema.dump(service_cluster)
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400
    
    @ns.doc('delete_service_cluster')
    def delete(self, id):
        """Supprime un cluster de service"""
        service_cluster = ServiceCluster.query.get_or_404(id)
        
        db.session.delete(service_cluster)
        
        try:
            db.session.commit()
            return {'message': f'Cluster de service {id} supprimé'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

# Routes supplémentaires pour des opérations spécifiques
@ns.route('/search/<string:nom>')
@ns.param('nom', 'Nom du cluster à rechercher')
class ServiceClusterSearch(Resource):
    @ns.doc('search_service_cluster')
    def get(self, nom):
        """Recherche des clusters de service par nom"""
        service_clusters = ServiceCluster.query.filter(ServiceCluster.nom.like(f'%{nom}%')).all()
        result = service_clusters_schema.dump(service_clusters)
        return jsonify(result)

@ns.route('/available')
class ServiceClusterAvailable(Resource):
    @ns.doc('get_available_service_clusters')
    def get(self):
        """Obtient les clusters de service avec des ressources disponibles"""
        service_clusters = ServiceCluster.query.filter(
            ServiceCluster.available_rom > 0,
            ServiceCluster.available_ram > 0,
            ServiceCluster.available_processor > 0
        ).all()
        result = service_clusters_schema.dump(service_clusters)
        return jsonify(result)
        
@ns.route('/find-suitable-host')
class ServiceClusterFindSuitableHost(Resource):
    @ns.doc('find_suitable_host')
    @ns.expect(vm_requirements_model)
    def post(self):
        """Trouve un hôte approprié pour une nouvelle VM en fonction des ressources requises et transmet la demande"""
        data = request.json
        
        # Extraire les exigences de ressources
        cpu_count = data.get('cpu_count', 0)
        memory_size_mib = data.get('memory_size_mib', 0)
        disk_size_gb = data.get('disk_size_gb', 0)
        vm_offer_id = data.get('vm_offer_id')
        system_image_id = data.get('system_image_id')
        
        # Paramètres additionnels pour la création de VM
        vm_name = data.get('name')
        user_id = data.get('user_id')
        os_type = data.get('os_type')
        root_password = data.get('root_password')
        
        # Convertir la mémoire de MiB à GB pour la comparaison
        memory_size_gb = memory_size_mib / 1024
        
        # Calculer le pourcentage de CPU requis (estimation basée sur le nombre de cœurs)
        # Supposons qu'un cœur équivaut à environ 10% de CPU
        cpu_percentage = cpu_count * 10
        
        # Trouver les clusters qui ont suffisamment de ressources disponibles
        suitable_clusters = ServiceCluster.query.filter(
            ServiceCluster.available_rom >= disk_size_gb,
            ServiceCluster.available_ram >= memory_size_gb,
            ServiceCluster.available_processor >= cpu_percentage,
            ServiceCluster.number_of_core >= cpu_count
        ).order_by(
            # Trier par la somme des ressources disponibles (pour équilibrer la charge)
            (ServiceCluster.available_rom / ServiceCluster.rom + 
             ServiceCluster.available_ram / ServiceCluster.ram + 
             ServiceCluster.available_processor / 100) / 3
        ).first()
        
        if suitable_clusters:
            host_info = service_cluster_schema.dump(suitable_clusters)
            
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
                    vm_host_url = f"http://{host_ip}:{vm_host_port}/vm/create"
                    
                    # Envoyer la requête de création de VM au service-vm-host
                    import requests
                    response = requests.post(
                        vm_host_url,
                        json=vm_config,
                        headers={"Content-Type": "application/json"},
                        timeout=15  # Timeout de 5 secondes
                    )
                    
                    # Vérifier la réponse
                    if response.status_code in [200, 201, 202]:
                        # Retourner les informations de l'hôte et la réponse de création de VM
                        return {
                            "host": host_info,
                            "vm_creation": response.json()
                        }
                    else:
                        # En cas d'échec de création de VM, retourner l'erreur
                        return {
                            "host": host_info,
                            "error": f"Erreur lors de la création de VM: {response.status_code} - {response.text}"
                        }, 500
                        
                except Exception as e:
                    # En cas d'erreur lors de la requête, retourner l'hôte mais avec un message d'erreur
                    return {
                        "host": host_info,
                        "error": f"Erreur lors de la communication avec le service-vm-host: {str(e)}"
                    }, 500
            
            # Si les paramètres pour la création de VM ne sont pas tous présents, retourner uniquement l'hôte
            return jsonify(host_info)
        else:
            return {'message': 'Aucun hôte avec suffisamment de ressources disponibles n\'a été trouvé'}, 404



# Endpoint de santé pour le service proxy
@health_ns.route('/')
class HealthCheck(Resource):
    @health_ns.doc('health_check')
    def get(self):
        """Vérifie la santé de l'application"""
        return {'status': 'UP', 'service': 'SERVICE-CLUSTER'}, 200
# Nous utilisons plutôt une fonction qui sera appelée manuellement
def create_tables():
    with app.app_context():
        db.create_all()
        print("Tables créées avec succès.")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv('APP_PORT'))
