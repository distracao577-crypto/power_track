from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# No Docker Compose, o nome do serviço de banco é 'db'.
# Se não houver uma variável de ambiente definida, ele usará 'db' por padrão.
DB_HOST = os.getenv("DB_HOST", "db") 
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_NAME = os.getenv("DB_NAME", "financeiro")

# Montando a URL de conexão (ajustada para os padrões comuns do Postgres no Docker)
# No backend/database.py
SQLALCHEMY_DATABASE_URL = "postgresql://user_power:senha_forte@db:5432/powertrack_db"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

