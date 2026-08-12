# ============================================================
# AL SAMADIYA IMMO PRO
# backend/main.py
# ============================================================

import os
import hashlib
import secrets
import shutil

from fastapi import (
    FastAPI,
    Request,
    Form,
    Depends,
    UploadFile,
    File,
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from sqlalchemy import text, or_
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend.models import (
    Utilisateur,
    Annonce,
    Favori,
    ImageAnnonce,
    Paiement,
)


# ============================================================
# DOSSIERS
# ============================================================

UPLOAD_DIR = os.path.join("uploads", "annonces")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# APPLICATION FASTAPI
# IMPORTANT : app doit être créé AVANT @app.get / @app.post
# ============================================================

app = FastAPI(
    title="AL SAMADIYA IMMO PRO",
    description="Plateforme immobilière AL SAMADIYA IMMO",
    version="1.0.0",
)


# ============================================================
# SESSION
# ============================================================

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv(
        "SESSION_SECRET",
        "al-samadiya-immo-secret-change-me",
    ),
)


# ============================================================
# FICHIERS STATIQUES / IMAGES
# ============================================================

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory="templates"
)


# ============================================================
# CRÉATION DES TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# MISE À JOUR DE LA TABLE ANNONCES
# Ajoute type_bien si l'ancienne base ne possède pas encore
# cette colonne.
# ============================================================

if engine.dialect.name == "sqlite":
    try:
        with engine.connect() as connection:

            colonnes = connection.execute(
                text("PRAGMA table_info(annonces)")
            ).fetchall()

            noms_colonnes = [
                colonne[1]
                for colonne in colonnes
            ]

            if "type_bien" not in noms_colonnes:

                connection.execute(
                    text(
                        "ALTER TABLE annonces "
                        "ADD COLUMN type_bien VARCHAR(100)"
                    )
                )

                connection.commit()

                print(
                    "✅ Colonne annonces.type_bien ajoutée."
                )

    except Exception as e:

        print(
            "⚠️ Migration type_bien :",
            repr(e)
        )


# ============================================================
# PAGE D'ACCUEIL
# ============================================================

@app.get("/")
def accueil(
    request: Request,
    db: Session = Depends(get_db),
):

    annonces = (
        db.query(Annonce)
        .filter(Annonce.statut != "brouillon")
        .order_by(
            Annonce.premium.desc(),
            Annonce.date_creation.desc(),
        )
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "annonces": annonces,
        },
    )


# ============================================================
# RECHERCHE DE BIENS
# ============================================================

@app.get("/recherche")
def recherche_biens(
    request: Request,
    type_bien: str = "",
    region: str = "",
    ville: str = "",
    quartier: str = "",
    prix_min: float = 0,
    prix_max: float = 0,
    db: Session = Depends(get_db),
):

    query = (
        db.query(Annonce)
        .filter(Annonce.statut != "brouillon")
    )

    if type_bien:
        query = query.filter(
            Annonce.type_bien == type_bien
        )

    if region:
        query = query.filter(
            Annonce.region.ilike(
                f"%{region}%"
            )
        )

    if ville:
        query = query.filter(
            Annonce.ville.ilike(
                f"%{ville}%"
            )
        )

    if quartier:
        query = query.filter(
            Annonce.quartier.ilike(
                f"%{quartier}%"
            )
        )

    if prix_min > 0:
        query = query.filter(
            Annonce.prix >= prix_min
        )

    if prix_max > 0:
        query = query.filter(
            Annonce.prix <= prix_max
        )

    annonces = (
        query
        .order_by(
            Annonce.premium.desc(),
            Annonce.date_creation.desc(),
        )
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="resultats.html",
        context={
            "request": request,
            "annonces": annonces,
            "type_bien": type_bien,
            "region": region,
            "ville": ville,
            "quartier": quartier,
            "prix_min": prix_min,
            "prix_max": prix_max,
            "nombre_resultats": len(annonces),
        },
    )


# ============================================================
# RECHERCHE AVANCÉE
# ============================================================

@app.get("/recherche-avancee")
def recherche_avancee(
    request: Request,
    type_bien: str = "",
    localisation: str = "",
    prix_min: float = 0,
    prix_max: float = 0,
    db: Session = Depends(get_db),
):

    query = (
        db.query(Annonce)
        .filter(Annonce.statut != "brouillon")
    )

    if type_bien:
        query = query.filter(
            Annonce.type_bien == type_bien
        )

    if prix_min > 0:
        query = query.filter(
            Annonce.prix >= prix_min
        )

    if prix_max > 0:
        query = query.filter(
            Annonce.prix <= prix_max
        )

    if localisation:

        recherche_localisation = (
            f"%{localisation}%"
        )

        query = query.filter(
            or_(
                Annonce.localisation.ilike(
                    recherche_localisation
                ),
                Annonce.region.ilike(
                    recherche_localisation
                ),
                Annonce.ville.ilike(
                    recherche_localisation
                ),
                Annonce.quartier.ilike(
                    recherche_localisation
                ),
                Annonce.adresse.ilike(
                    recherche_localisation
                ),
            )
        )

    annonces = (
        query
        .order_by(
            Annonce.premium.desc(),
            Annonce.date_creation.desc(),
        )
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="resultats.html",
        context={
            "request": request,
            "annonces": annonces,
            "type_bien": type_bien,
            "localisation": localisation,
            "prix_min": prix_min,
            "prix_max": prix_max,
            "nombre_resultats": len(annonces),
        },
    )


# ============================================================
# CONNEXION
# ============================================================

@app.get("/login")
def login(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
        },
    )


@app.post("/login")
def traiter_login(
    request: Request,
    identifiant: str = Form(...),
    mot_de_passe: str = Form(...),
    db: Session = Depends(get_db),
):

    utilisateur = (
        db.query(Utilisateur)
        .filter(
            or_(
                Utilisateur.email == identifiant,
                Utilisateur.telephone == identifiant,
            )
        )
        .first()
    )

    if not utilisateur:

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "erreur": (
                    "E-mail ou numéro de téléphone "
                    "incorrect."
                ),
            },
            status_code=401,
        )

    try:

        sel_hex, hash_hex = (
            utilisateur.mot_de_passe.split("$", 1)
        )

        sel = bytes.fromhex(sel_hex)
        hash_enregistre = bytes.fromhex(hash_hex)

    except (
        ValueError,
        TypeError,
        AttributeError,
    ):

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "erreur": (
                    "Impossible de vérifier "
                    "les identifiants."
                ),
            },
            status_code=500,
        )

    hash_verification = hashlib.pbkdf2_hmac(
        "sha256",
        mot_de_passe.encode("utf-8"),
        sel,
        200_000,
    )

    if not secrets.compare_digest(
        hash_verification,
        hash_enregistre,
    ):

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "erreur": (
                    "E-mail ou numéro de téléphone "
                    "incorrect."
                ),
            },
            status_code=401,
        )

    request.session["user_id"] = utilisateur.id
    request.session["role"] = utilisateur.role

    return RedirectResponse(
        "/dashboard",
        status_code=303,
    )


# ============================================================
# INSCRIPTION
# ============================================================

@app.get("/inscription")
def inscription(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="inscription.html",
        context={
            "request": request,
        },
    )


@app.post("/inscription")
def enregistrer_utilisateur(
    request: Request,
    nom: str = Form(...),
    prenom: str = Form(""),
    email: str = Form(...),
    telephone: str = Form(""),
    role: str = Form("client"),
    mot_de_passe: str = Form(...),
    confirmation: str = Form(...),
    db: Session = Depends(get_db),
):

    if mot_de_passe != confirmation:

        return templates.TemplateResponse(
            request=request,
            name="inscription.html",
            context={
                "request": request,
                "erreur": (
                    "Les deux mots de passe "
                    "ne correspondent pas."
                ),
            },
            status_code=400,
        )

    roles_autorises = [
        "client",
        "proprietaire",
        "agence",
    ]

    if role not in roles_autorises:
        role = "client"

    utilisateur_existant = (
        db.query(Utilisateur)
        .filter(
            Utilisateur.email == email
        )
        .first()
    )

    if utilisateur_existant:

        return templates.TemplateResponse(
            request=request,
            name="inscription.html",
            context={
                "request": request,
                "erreur": (
                    "Cette adresse e-mail "
                    "est déjà utilisée."
                ),
            },
            status_code=400,
        )

    sel = secrets.token_bytes(16)

    hash_mot_de_passe = hashlib.pbkdf2_hmac(
        "sha256",
        mot_de_passe.encode("utf-8"),
        sel,
        200_000,
    )

    mot_de_passe_securise = (
        sel.hex()
        + "$"
        + hash_mot_de_passe.hex()
    )

    utilisateur = Utilisateur(
        nom=nom,
        prenom=prenom,
        email=email,
        telephone=telephone,
        mot_de_passe=mot_de_passe_securise,
        role=role,
        actif=True,
    )

    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)

    return RedirectResponse(
        "/login",
        status_code=303,
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/dashboard")
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
        },
    )


# ============================================================
# AJOUTER UNE ANNONCE - FORMULAIRE
# ============================================================

@app.get("/ajouter-annonce")
def ajouter_annonce(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="ajouter_annonce.html",
        context={
            "request": request,
        },
    )


# ============================================================
# AJOUTER UNE ANNONCE - TRAITEMENT
# ============================================================

@app.post("/ajouter-annonce")
async def enregistrer_annonce(
    titre: str = Form(""),
    description: str = Form(""),
    categorie: str = Form(""),
    type_bien: str = Form(""),
    prix: float = Form(0),
    superficie: float = Form(0),
    region: str = Form(""),
    ville: str = Form(""),
    quartier: str = Form(""),
    localisation: str = Form(""),
    adresse: str = Form(""),
    nombre_chambres: int = Form(0),
    nombre_salles_bain: int = Form(0),
    meuble: bool = Form(False),
    telephone: str = Form(""),
    whatsapp: str = Form(""),
    email: str = Form(""),
    latitude: float = Form(0),
    longitude: float = Form(0),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):

    # Si le formulaire ne contient pas type_bien,
    # on utilise la catégorie comme solution de secours.
    type_bien_final = (
        type_bien.strip()
        or categorie.strip()
        or "Autre"
    )

    # Sécurisation des valeurs numériques
    prix = max(float(prix or 0), 0)
    superficie = max(float(superficie or 0), 0)

    nombre_chambres = max(
        int(nombre_chambres or 0),
        0,
    )

    nombre_salles_bain = max(
        int(nombre_salles_bain or 0),
        0,
    )

    # --------------------------------------------------------
    # Création de l'annonce
    # --------------------------------------------------------

    annonce = Annonce(
        titre=titre,
        description=description,
        categorie=categorie,
        type_bien=type_bien_final,
        prix=prix,
        surface=superficie,
        region=region,
        ville=ville,
        quartier=quartier,
        localisation=(
            localisation
            or quartier
            or ville
        ),
        adresse=adresse,
        chambres=nombre_chambres,
        salles_bain=nombre_salles_bain,
        meuble=meuble,
        telephone=telephone,
        whatsapp=whatsapp,
        email=email,
        latitude=latitude,
        longitude=longitude,
        statut="en_attente",
    )

    db.add(annonce)
    db.flush()

    # --------------------------------------------------------
    # Sauvegarde de l'image
    # --------------------------------------------------------

    if image and image.filename:

        nom_original = os.path.basename(
            image.filename
        )

        extension = os.path.splitext(
            nom_original
        )[1].lower()

        extensions_autorisees = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }

        if extension in extensions_autorisees:

            nom_fichier = (
                secrets.token_hex(12)
                + extension
            )

            chemin_complet = os.path.join(
                UPLOAD_DIR,
                nom_fichier,
            )

            with open(
                chemin_complet,
                "wb",
            ) as buffer:

                shutil.copyfileobj(
                    image.file,
                    buffer,
                )

            image_annonce = ImageAnnonce(
                annonce_id=annonce.id,
                nom_fichier=nom_fichier,
                chemin=(
                    f"/uploads/annonces/"
                    f"{nom_fichier}"
                ),
            )

            db.add(image_annonce)

    db.commit()
    db.refresh(annonce)

    return RedirectResponse(
        f"/annonce/{annonce.id}",
        status_code=303,
    )


# ============================================================
# DÉTAIL D'UNE ANNONCE
# ============================================================

@app.get("/annonce/{id}")
def detail_annonce(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
):

    annonce = (
        db.query(Annonce)
        .filter(Annonce.id == id)
        .first()
    )

    if not annonce:

        return templates.TemplateResponse(
            request=request,
            name="detail_annonce.html",
            context={
                "request": request,
                "annonce": None,
                "erreur": (
                    "Cette annonce "
                    "n'existe pas."
                ),
            },
            status_code=404,
        )

    annonce.vues = (
        (annonce.vues or 0) + 1
    )

    db.commit()

    images = (
        db.query(ImageAnnonce)
        .filter(
            ImageAnnonce.annonce_id == annonce.id
        )
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="detail_annonce.html",
        context={
            "request": request,
            "annonce": annonce,
            "images": images,
        },
    )


# ============================================================
# SANTÉ DE L'APPLICATION
# Permet de tester rapidement Render.
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "AL SAMADIYA IMMO PRO",
    }
