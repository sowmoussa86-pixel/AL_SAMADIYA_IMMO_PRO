from fastapi import (
    FastAPI,
    Request,
    Depends,
    Form,
    File,
    UploadFile
)

from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy import or_, text

import os
import shutil
import hashlib
import secrets

from backend.database import Base, engine, get_db
from backend.models import (
    Utilisateur,
    Annonce,
    Favori,
    ImageAnnonce,
    Paiement
)

# ======================================================
# CRÉATION DES TABLES
# ======================================================

Base.metadata.create_all(bind=engine)


# ======================================================
# MISE À JOUR DE LA TABLE ANNONCES
# ======================================================

from sqlalchemy import text

with engine.connect() as connection:

    colonnes = connection.execute(
        text("PRAGMA table_info(annonces)")
    ).fetchall()

    noms_colonnes = [colonne[1] for colonne in colonnes]

    if "type_bien" not in noms_colonnes:

        connection.execute(
            text(
                "ALTER TABLE annonces "
                "ADD COLUMN type_bien VARCHAR(100)"
            )
        )

        connection.commit()


# ======================================================
# PAGE D'ACCUEIL
# ======================================================

@app.get("/")
def accueil(
    request: Request,
    db: Session = Depends(get_db)
):

    annonces = (
        db.query(Annonce)
        .filter(Annonce.statut != "brouillon")
        .order_by(
            Annonce.premium.desc(),
            Annonce.date_creation.desc()
        )
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "annonces": annonces
        }
    )


# ======================================================
# RECHERCHE DE BIENS
# ======================================================

@app.get("/recherche")
def recherche_biens(
    request: Request,
    type_bien: str = "",
    region: str = "",
    ville: str = "",
    prix_min: float = 0,
    prix_max: float = 0,
    db: Session = Depends(get_db)
):

    requete = db.query(Annonce)

    # --------------------------------------------------
    # TYPE DE BIEN
    # --------------------------------------------------

    if type_bien:

        requete = requete.filter(
            Annonce.type_bien == type_bien
        )


    # --------------------------------------------------
    # REGION
    # --------------------------------------------------

    if region:

        requete = requete.filter(
            Annonce.region == region
        )


    # --------------------------------------------------
    # VILLE
    # --------------------------------------------------

    if ville:

        requete = requete.filter(
            Annonce.ville == ville
        )


    # --------------------------------------------------
    # PRIX MINIMUM
    # --------------------------------------------------

    if prix_min and prix_min > 0:

        requete = requete.filter(
            Annonce.prix >= prix_min
        )


    # --------------------------------------------------
    # PRIX MAXIMUM
    # --------------------------------------------------

    if prix_max and prix_max > 0:

        requete = requete.filter(
            Annonce.prix <= prix_max
        )


    # --------------------------------------------------
    # UNIQUEMENT LES ANNONCES VALIDES
    # --------------------------------------------------

    requete = requete.filter(
        Annonce.statut != "brouillon"
    )


    # --------------------------------------------------
    # TRI
    # --------------------------------------------------

    annonces = (
        requete
        .order_by(
            Annonce.premium.desc(),
            Annonce.date_creation.desc()
        )
        .all()
    )


    # --------------------------------------------------
    # AFFICHAGE
    # --------------------------------------------------

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "request": request,
            "annonces": annonces,
            "type_bien": type_bien,
            "region": region,
            "ville": ville,
            "prix_min": prix_min,
            "prix_max": prix_max
        }
    )

    # --------------------------------------------------
    # EXECUTION
    # --------------------------------------------------

    annonces = query.order_by(
        Annonce.date_creation.desc()
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="resultats.html",
        context={
            "request": request,
            "annonces": annonces,
            "type_bien": type_bien,
            "prix_min": prix_min,
            "prix_max": prix_max,
            "region": region,
            "zone": zone
        }
    )

    # --------------------------------------------------
    # RESULTATS
    # --------------------------------------------------

    annonces = query.order_by(
        Annonce.date_creation.desc()
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="resultats.html",
        context={
            "request": request,
            "annonces": annonces,
            "type_bien": type_bien,
            "prix_min": prix_min,
            "prix_max": prix_max,
            "region": region,
            "zone": zone,
        }
    )

    # =================================================
    # VERIFICATION DU TYPE DE BIEN
    # =================================================

    if not categorie:

        return templates.TemplateResponse(
            request=request,
            name="resultats.html",
            context={
                "request": request,
                "annonces": [],
                "erreur": "Veuillez sélectionner un type de bien.",
                "categorie": categorie,
                "prix_min": prix_min,
                "prix_max": prix_max,
                "region": region,
                "localisation": localisation
            },
            status_code=400
        )

    # =================================================
    # VERIFICATION DES PRIX
    # =================================================

    try:

        prix_min_float = float(prix_min)
        prix_max_float = float(prix_max)

    except (ValueError, TypeError):

        return templates.TemplateResponse(
            request=request,
            name="resultats.html",
            context={
                "request": request,
                "annonces": [],
                "erreur": "Veuillez saisir une fourchette de prix valide.",
                "categorie": categorie,
                "prix_min": prix_min,
                "prix_max": prix_max,
                "region": region,
                "localisation": localisation
            },
            status_code=400
        )

    # =================================================
    # VERIFICATION COHERENCE DES PRIX
    # =================================================

    if prix_min_float < 0 or prix_max_float < 0:

        return templates.TemplateResponse(
            request=request,
            name="resultats.html",
            context={
                "request": request,
                "annonces": [],
                "erreur": "Les prix doivent être positifs.",
                "categorie": categorie,
                "prix_min": prix_min,
                "prix_max": prix_max,
                "region": region,
                "localisation": localisation
            },
            status_code=400
        )

    if prix_min_float > prix_max_float:

        return templates.TemplateResponse(
            request=request,
            name="resultats.html",
            context={
                "request": request,
                "annonces": [],
                "erreur": "Le prix minimum ne peut pas être supérieur au prix maximum.",
                "categorie": categorie,
                "prix_min": prix_min,
                "prix_max": prix_max,
                "region": region,
                "localisation": localisation
            },
            status_code=400
        )

    # =================================================
    # CONSTRUCTION DE LA REQUETE
    # =================================================

    query = db.query(Annonce)

    # -------------------------------------------------
    # TYPE DE BIEN
    # -------------------------------------------------

    query = query.filter(
        Annonce.categorie == categorie
    )

    # -------------------------------------------------
    # PRIX MINIMUM
    # -------------------------------------------------

    query = query.filter(
        Annonce.prix >= prix_min_float
    )

    # -------------------------------------------------
    # PRIX MAXIMUM
    # -------------------------------------------------

    query = query.filter(
        Annonce.prix <= prix_max_float
    )

    # -------------------------------------------------
    # REGION
    # -------------------------------------------------

    if region:

        query = query.filter(
            Annonce.region.ilike(
                f"%{region}%"
            )
        )

    # -------------------------------------------------
    # COMMUNE / QUARTIER / LOCALISATION
    # -------------------------------------------------

    if localisation:

        recherche_localisation = (
            f"%{localisation}%"
        )

        query = query.filter(
            (Annonce.localisation.ilike(
                recherche_localisation
            ))
            |
            (Annonce.ville.ilike(
                recherche_localisation
            ))
            |
            (Annonce.quartier.ilike(
                recherche_localisation
            ))
            |
            (Annonce.adresse.ilike(
                recherche_localisation
            ))
        )

    # =================================================
    # EXECUTION
    # =================================================

    annonces = (
        query
        .order_by(
            Annonce.premium.desc(),
            Annonce.date_creation.desc()
        )
        .all()
    )

    # =================================================
    # RESULTATS
    # =================================================

    return templates.TemplateResponse(
        request=request,
        name="resultats.html",
        context={
            "request": request,
            "annonces": annonces,
            "categorie": categorie,
            "prix_min": prix_min,
            "prix_max": prix_max,
            "region": region,
            "localisation": localisation,
            "nombre_resultats": len(annonces)
        }
    )

# =====================================================
# LOGIN
# =====================================================

@app.get("/login")
def login(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request
        }
    )
@app.post("/login")
def traiter_login(
    request: Request,
    identifiant: str = Form(...),
    mot_de_passe: str = Form(...),
    db: Session = Depends(get_db)
):

    # Recherche par e-mail OU numéro de téléphone
    utilisateur = (
        db.query(Utilisateur)
        .filter(
            or_(
                Utilisateur.email == identifiant,
                Utilisateur.telephone == identifiant
            )
        )
        .first()
    )

    # Utilisateur inexistant
    if not utilisateur:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "erreur": "E-mail ou numéro de téléphone incorrect."
            },
            status_code=401
        )

    # Vérification du mot de passe PBKDF2
    try:

        sel_hex, hash_hex = utilisateur.mot_de_passe.split("$", 1)

        sel = bytes.fromhex(sel_hex)
        hash_enregistre = bytes.fromhex(hash_hex)

    except (ValueError, TypeError):

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "erreur": "Impossible de vérifier les identifiants."
            },
            status_code=500
        )

    # Recalcul du hash avec le même sel
    hash_verification = hashlib.pbkdf2_hmac(
        "sha256",
        mot_de_passe.encode("utf-8"),
        sel,
        200_000
    )

    # Comparaison sécurisée
    if not secrets.compare_digest(
        hash_verification,
        hash_enregistre
    ):

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "erreur": "E-mail ou numéro de téléphone incorrect."
            },
            status_code=401
        )

    # Connexion réussie
    request.session["user_id"] = utilisateur.id
    request.session["role"] = utilisateur.role

    return RedirectResponse(
        "/dashboard",
        status_code=303
    )
# =====================================================
# INSCRIPTION
# =====================================================

@app.get("/inscription")
def inscription(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="inscription.html",
        context={
            "request": request
        }
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
    db: Session = Depends(get_db)
):

    # Vérification du mot de passe
    if mot_de_passe != confirmation:

        return templates.TemplateResponse(
            request=request,
            name="inscription.html",
            context={
                "request": request,
                "erreur": "Les deux mots de passe ne correspondent pas."
            },
            status_code=400
        )

    # Vérification du rôle
    roles_autorises = [
        "client",
        "proprietaire",
        "agence"
    ]

    if role not in roles_autorises:
        role = "client"

    # Vérification si l'email existe déjà
    utilisateur_existant = (
        db.query(Utilisateur)
        .filter(Utilisateur.email == email)
        .first()
    )

    if utilisateur_existant:

        return templates.TemplateResponse(
            request=request,
            name="inscription.html",
            context={
                "request": request,
                "erreur": "Cette adresse e-mail est déjà utilisée."
            },
            status_code=400
        )

    # -------------------------------------------------
    # HACHAGE SÉCURISÉ DU MOT DE PASSE
    # -------------------------------------------------

    sel = secrets.token_bytes(16)

    hash_mot_de_passe = hashlib.pbkdf2_hmac(
        "sha256",
        mot_de_passe.encode("utf-8"),
        sel,
        200_000
    )

    mot_de_passe_securise = (
        sel.hex()
        + "$"
        + hash_mot_de_passe.hex()
    )

    # -------------------------------------------------
    # CRÉATION DE L'UTILISATEUR
    # -------------------------------------------------

    utilisateur = Utilisateur(
        nom=nom,
        prenom=prenom,
        email=email,
        telephone=telephone,
        mot_de_passe=mot_de_passe_securise,
        role=role,
        actif=True
    )

    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)

    # -------------------------------------------------
    # REDIRECTION APRÈS INSCRIPTION
    # -------------------------------------------------

    return RedirectResponse(
        "/login",
        status_code=303
    )


# =====================================================
# DASHBOARD
# =====================================================

@app.get("/dashboard")
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request
        }
    )
@app.get("/ajouter-annonce")
def ajouter_annonce(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="ajouter_annonce.html",
        context={
            "request": request
        }
    )
@app.post("/ajouter-annonce")
async def enregistrer_annonce(
    titre: str = Form(""),
    description: str = Form(...),
    categorie: str = Form(...),
    type_transaction: str = Form(...),
    prix: float = Form(0),
    superficie: float = Form(...),
    region: str = Form(...),
    ville: str = Form(...),
    quartier: str = Form(...),
    adresse: str = Form(...),
    nombre_chambres: int = Form(...),
    nombre_salles_bain: int = Form(...),
    meuble: bool = Form(False),
    telephone: str = Form(...),
    whatsapp: str = Form(...),
    email: str = Form(...),
    latitude: float = Form(0),
    longitude: float = Form(0),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Création du dossier uploads si nécessaire
    os.makedirs("uploads", exist_ok=True)

    # Sauvegarde de l'image
    chemin_image = os.path.join("uploads", "annonces", image.filename)

    with open(chemin_image, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Création de l'annonce
    annonce = Annonce(
        titre=titre,
        description=description,
        categorie=categorie,
        type_transaction=type_transaction,
        prix=prix,
        superficie=superficie,
        region=region,
        ville=ville,
        quartier=quartier,
        adresse=adresse,
        nombre_chambres=nombre_chambres,
        nombre_salles_bain=nombre_salles_bain,
        meuble=meuble,
        telephone=telephone,
        whatsapp=whatsapp,
        email=email,
        latitude=latitude,
        longitude=longitude,
        image=image.filename
    )

    db.add(annonce)
    db.commit()

    return RedirectResponse("/", status_code=303)
@app.get("/annonce/{id}")
def detail_annonce(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    annonce = db.query(Annonce).filter(
        Annonce.id == id
    ).first()

    if annonce:

        annonce.vues += 1

        db.commit()

    return templates.TemplateResponse(
        request=request,
        name="detail_annonce.html",
        context={
            "request": request,
            "annonce": annonce
        }
    )