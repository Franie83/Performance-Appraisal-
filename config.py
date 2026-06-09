import os 
 
class Config: 
    SECRET_KEY = 'dev-secret-key' 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///appraisal.db' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
 
class DevelopmentConfig(Config): 
    DEBUG = True 
 
class ProductionConfig(Config): 
    DEBUG = False 
 
config = { 
    'development': DevelopmentConfig, 
    'production': ProductionConfig, 
    'default': DevelopmentConfig 
} 
