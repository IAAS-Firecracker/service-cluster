import os
import dotenv
import sys
import logging
from pydantic_settings import BaseSettings

dotenv.load_dotenv()

class EurekaConfig(BaseSettings):
    app_name: str = os.getenv('APP_NAME', 'service-cluster')
    app_host: str = os.getenv('APP_HOST', '0.0.0.0')
    app_port: int = int(os.getenv('APP_PORT', '5000'))
    eureka_url: str = os.getenv('EUREKA_SERVER', 'http://localhost:8761/eureka/')
    
    class Config:
        env_file = ".env"
        extra = "allow"

eureka_config = EurekaConfig()