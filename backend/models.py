# ======================================================
# MODELS - AL SAMADIYA IMMO PRO
# ======================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


# ======================================================
# UTILISATEURS
# ======================================================

class Utilisateur(Base):

    __tablename__ = "utilisateurs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------
    # INFORMATIONS PERSONNELLES
    # --------------------------------------------------

    nom = Column(
        String(100),
        nullable=False
    )

    prenom = Column(
        String(100),
        nullable=True
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    telephone = Column(
        String(30),
        nullable=True
    )

    # --------------------------------------------------
    # AUTHENTIFICATION
    # --------------------------------------------------

    mot_de_passe = Column(
        String(255),
        nullable=False
    )

    # client / proprietaire / agence / admin
    role = Column(
        String(30),
        default="client",
        nullable=False
    )

    actif = Column(
        Boolean,
        default=True,
        nullable=False
    )

    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # ==================================================
    # RELATION AVEC LES ANNONCES
    # ==================================================

    annonces = relationship(
        "Annonce",
        back_populates="utilisateur",
        cascade="all, delete-orphan"
    )

    # ==================================================
    # RELATION AVEC LES FAVORIS
    # ==================================================

    favoris = relationship(
        "Favori",
        back_populates="utilisateur",
        cascade="all, delete-orphan"
    )

    # ==================================================
    # RELATION AVEC LES PAIEMENTS
    # ==================================================

    paiements = relationship(
        "Paiement",
        back_populates="utilisateur",
        cascade="all, delete-orphan"
    )


# ======================================================
# ANNONCES
# ======================================================

class Annonce(Base):

    __tablename__ = "annonces"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------
    # INFORMATIONS DE L'ANNONCE
    # --------------------------------------------------

    titre = Column(
        String(200),
        nullable=False
    )

    description = Column(
        String(5000),
        nullable=True
    )

    categorie = Column(
        String(100),
        nullable=True
    )

    type_bien = Column(
        String(100),
        nullable=False
    )

    prix = Column(
        Float,
        nullable=False
    )

    surface = Column(
        Float,
        nullable=True
    )

    # --------------------------------------------------
    # LOCALISATION
    # --------------------------------------------------

    region = Column(
        String(100),
        nullable=True
    )

    ville = Column(
        String(100),
        nullable=True
    )

    quartier = Column(
        String(150),
        nullable=True
    )

    localisation = Column(
        String(255),
        nullable=True
    )

    adresse = Column(
        String(255),
        nullable=True
    )

    # --------------------------------------------------
    # GPS
    # --------------------------------------------------

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    # --------------------------------------------------
    # INFORMATIONS COMPLEMENTAIRES
    # --------------------------------------------------

    chambres = Column(
        Integer,
        nullable=True
    )

    salles_bain = Column(
        Integer,
        nullable=True
    )

    meuble = Column(
        Boolean,
        default=False
    )

    # --------------------------------------------------
    # CONTACT PLATEFORME
    # --------------------------------------------------

    telephone = Column(
        String(30),
        nullable=True
    )

    whatsapp = Column(
        String(30),
        nullable=True
    )

    email = Column(
        String(150),
        nullable=True
    )

    # --------------------------------------------------
    # STATISTIQUES / PAIEMENT
    # --------------------------------------------------

    vues = Column(
        Integer,
        default=0
    )

    premium = Column(
        Boolean,
        default=False
    )

    statut = Column(
        String(50),
        default="brouillon",
        nullable=False
    )

    paiement_confirme = Column(
        Boolean,
        default=False
    )

    date_creation = Column(
        DateTime,
        nullable=True
    )

    # --------------------------------------------------
    # VUES
    # --------------------------------------------------

    vues = Column(
        Integer,
        default=0,
        nullable=False
    )

    # --------------------------------------------------
    # PROPRIETAIRE
    # --------------------------------------------------

    utilisateur_id = Column(
        Integer,
        ForeignKey("utilisateurs.id"),
        nullable=True
    )

    utilisateur = relationship(
        "Utilisateur",
        back_populates="annonces"
    )

    # --------------------------------------------------
    # PAIEMENT
    # --------------------------------------------------

    paiement_confirme = Column(
        Boolean,
        default=False,
        nullable=False
    )

    # --------------------------------------------------
    # ANNONCE PREMIUM
    # --------------------------------------------------

    premium = Column(
        Boolean,
        default=False,
        nullable=False
)

    # --------------------------------------------------
    # RELATION AVEC LES PAIEMENTS
    # --------------------------------------------------

    paiements = relationship(
        "Paiement",
        back_populates="annonce",
        cascade="all, delete-orphan"
    )

    # --------------------------------------------------
    # DATE
    # --------------------------------------------------

    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


# ======================================================
# FAVORIS
# ======================================================

class Favori(Base):

    __tablename__ = "favoris"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    utilisateur_id = Column(
        Integer,
        ForeignKey("utilisateurs.id"),
        nullable=False
    )

    annonce_id = Column(
        Integer,
        ForeignKey("annonces.id"),
        nullable=False
    )

    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # --------------------------------------------------
    # RELATION UTILISATEUR
    # --------------------------------------------------

    utilisateur = relationship(
        "Utilisateur",
        back_populates="favoris"
    )

    # --------------------------------------------------
    # RELATION ANNONCE
    # --------------------------------------------------

    annonce = relationship(
        "Annonce"
    )


# ======================================================
# IMAGES DES ANNONCES
# ======================================================

class ImageAnnonce(Base):

    __tablename__ = "images_annonces"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    annonce_id = Column(
        Integer,
        ForeignKey("annonces.id"),
        nullable=False
    )

    nom_fichier = Column(
        String(255),
        nullable=False
    )

    chemin = Column(
        String(500),
        nullable=True
    )

    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    annonce = relationship(
        "Annonce"
    )


# ======================================================
# PAIEMENTS
# ======================================================

class Paiement(Base):

    __tablename__ = "paiements"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------
    # UTILISATEUR QUI PAYE
    # --------------------------------------------------

    utilisateur_id = Column(
        Integer,
        ForeignKey("utilisateurs.id"),
        nullable=False
    )

    # --------------------------------------------------
    # ANNONCE CONCERNEE
    # --------------------------------------------------

    annonce_id = Column(
        Integer,
        ForeignKey("annonces.id"),
        nullable=False
    )

    # --------------------------------------------------
    # MONTANT
    # --------------------------------------------------

    montant = Column(
        Float,
        nullable=False
    )

    # --------------------------------------------------
    # OPERATEUR DE PAIEMENT
    # --------------------------------------------------

    operateur = Column(
        String(30),
        nullable=False
    )

    # wave / orange_money

    # --------------------------------------------------
    # REFERENCE DU PAIEMENT
    # --------------------------------------------------

    reference = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    # --------------------------------------------------
    # IDENTIFIANT DE TRANSACTION
    # --------------------------------------------------

    transaction_id = Column(
        String(150),
        nullable=True
    )

    # --------------------------------------------------
    # STATUT
    # --------------------------------------------------

    statut = Column(
        String(50),
        default="en_attente",
        nullable=False
    )

    # en_attente / reussi / echoue / annule

    # --------------------------------------------------
    # MODE TEST
    # --------------------------------------------------

    mode_test = Column(
        Boolean,
        default=True,
        nullable=False
    )

    # True = paiement simulé
    # False = vrai paiement

    # --------------------------------------------------
    # DATES
    # --------------------------------------------------

    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    date_confirmation = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # ==================================================
    # RELATION UTILISATEUR
    # ==================================================

    utilisateur = relationship(
        "Utilisateur",
        back_populates="paiements"
    )

    # ==================================================
    # RELATION ANNONCE
    # ==================================================

    annonce = relationship(
        "Annonce",
        back_populates="paiements"
    )