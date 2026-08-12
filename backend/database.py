import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Charger les variables d'environnement
load_dotenv()

# Base de données
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///database/alsamadiya.db"
)

# Options SQLite
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }

# Création du moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    future=True,
    echo=False
)

# Création de la session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base des modèles
Base = declarative_base()


# Dépendance FastAPI
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()