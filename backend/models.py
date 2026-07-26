from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from backend.database import Base


class Utilisateur(Base):

    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)

    nom = Column(String(100))

    prenom = Column(String(100))

    telephone = Column(String(30), unique=True)

    email = Column(String(150), unique=True)

    mot_de_passe = Column(String(255))

    role = Column(String(30))

    actif = Column(Boolean, default=True)

    date_creation = Column(DateTime(timezone=True), server_default=func.now())


class Annonce(Base):

    __tablename__ = "annonces"

    id = Column(Integer, primary_key=True, index=True)

    titre = Column(String(250))

    description = Column(String(1000))

    categorie = Column(String(100))

    prix = Column(Float)

    superficie = Column(Float)

    region = Column(String(100))

    ville = Column(String(100))

    quartier = Column(String(100))

    telephone = Column(String(30))

    whatsapp = Column(String(30))

    image = Column(String(255))

    statut = Column(String(50), default="En attente")

    date_creation = Column(DateTime(timezone=True), server_default=func.now())