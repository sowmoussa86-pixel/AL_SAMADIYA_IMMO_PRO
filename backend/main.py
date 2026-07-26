from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend.models import Annonce

# Création des tables
Base.metadata.create_all(bind=engine)

# Initialisation de l'application
app = FastAPI(
    title="AL SAMADIYA IMMO PRO",
    version="1.0.0"
)

# Fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


# =====================================================
# ACCUEIL
# =====================================================

@app.get("/")
def accueil(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


# =====================================================
# RECHERCHE
# =====================================================

@app.get("/recherche")
def recherche(
    request: Request,
    region: str = "",
    categorie: str = "",
    prix_min: float = 0,
    prix_max: float = 0,
    db: Session = Depends(get_db)
):

    query = db.query(Annonce)

    if region:
        query = query.filter(Annonce.region == region)

    if categorie:
        query = query.filter(Annonce.categorie == categorie)

    if prix_min > 0:
        query = query.filter(Annonce.prix >= prix_min)

    if prix_max > 0:
        query = query.filter(Annonce.prix <= prix_max)

    annonces = query.all()

    return templates.TemplateResponse(
        request=request,
        name="resultats.html",
        context={
            "request": request,
            "annonces": annonces,
            "region": region,
            "categorie": categorie,
            "prix_min": prix_min,
            "prix_max": prix_max,
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