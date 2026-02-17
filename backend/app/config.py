from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://job_portal_db:job_portal_db@jobportaldb.c1swawyaiteb.us-east-2.rds.amazonaws.com:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your-secret-key'  
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

