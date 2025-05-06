import os
from py_eureka_client import eureka_client
from fastapi import FastAPI
from .eureka_config import eureka_config

async def register_with_eureka(app: FastAPI):
    try:
        eureka_url = eureka_config.eureka_url
        app_name = eureka_config.app_name
        app_port = eureka_config.app_port
        app_host = eureka_config.app_host
        
        if not eureka_url or not app_name:
            print(f"Configuration Eureka incomplète: eureka_url={eureka_url}, app_name={app_name}")
            return
            
        print(f"Enregistrement auprès d'Eureka: {app_name} vers {eureka_url}")
        
        await eureka_client.init_async(
            eureka_server=eureka_url,
            app_name=app_name,
            instance_port=app_port,
            instance_host=app_host,
            renewal_interval_in_secs=30,
            duration_in_secs=90,
            metadata={
                "zone": "primary",
                "securePortEnabled": "false",
                "securePort": "443",
                "statusPageUrl": f"http://{app_host}:{app_port}/info",
                "healthCheckUrl": f"http://{app_host}:{app_port}/health"
            }
        )
        print(f"Enregistrement auprès d'Eureka réussi")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement auprès d'Eureka: {e}")

async def shutdown_eureka():
    try:
        await eureka_client.stop_async()
        print("Désenregistrement d'Eureka réussi")
    except Exception as e:
        print(f"Erreur lors du désenregistrement d'Eureka: {e}")
