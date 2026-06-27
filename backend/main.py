import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from dotenv import load_dotenv

# Chargement des variables d'environnement du fichier .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Les variables d'environnement SUPABASE_URL ou SUPABASE_KEY sont manquantes.")

# Initialisation de FastAPI et du client Supabase
app = FastAPI(title="Azimut API", version="1.0")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Activation du CORS pour permettre au futur Frontend de requêter l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, on remplacera par l'URL du frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèle de données pour valider l'e-mail reçu
class SubscriberRequest(BaseModel):
    email: EmailStr
    section_id: int = 1  # Par défaut la section 1 (Troupe)

@app.post("/api/v1/subscribe")
def subscribe(payload: SubscriberRequest):
    """Route pour s'abonner à la newsletter d'une section"""
    try:
        # Tentative d'insertion dans Supabase
        response = supabase.table("newsletter_subscribers").insert({
            "section_id": payload.section_id,
            "email": payload.email,
            "is_subscribed": True
        }).execute()
        
        # Si l'insertion réussit, on récupère les données de l'abonné (notamment son token)
        subscriber_data = response.data[0]
        token = subscriber_data["unsubscribe_token"]
        
        # C'est ici que nous brancherons le script d'envoi d'e-mail à la prochaine étape !
        print(f"👉 TODO: Envoyer l'e-mail de confirmation à {payload.email} avec le token {token}")
        
        return {
            "status": "success",
            "message": "Inscription validée avec succès.",
            "email": payload.email
        }
        
    except Exception as e:
        # Gestion de la contrainte UNIQUE (si l'e-mail est déjà inscrit pour cette section)
        if "duplicate key value" in str(e):
            raise HTTPException(status_code=400, detail="Cet adresse e-mail est déjà inscrite à la newsletter de cette section.")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")

@app.get("/api/v1/unsubscribe")
def unsubscribe(token: str = Query(..., description="Le token UUID unique de désinscription")):
    """Route de désinscription en un clic (appelée via le lien dans l'e-mail)"""
    try:
        # On cherche l'abonné avec ce token et on passe son statut à False
        response = supabase.table("newsletter_subscribers").update({
            "is_subscribed": False
        }).eq("unsubscribe_token", token).execute()
        
        # Si la liste retournée est vide, le token n'existait pas
        if not response.data:
            raise HTTPException(status_code=44, detail="Jeton de désinscription invalide ou expiré.")
            
        return {
            "status": "success",
            "message": "Vous avez été désabonné de la newsletter avec succès."
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erreur lors du désabonnement : {str(e)}")