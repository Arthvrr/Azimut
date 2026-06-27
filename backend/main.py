import os
import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from dotenv import load_dotenv

# Chargement des variables d'environnement du fichier .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

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

def send_welcome_email(to_email: str, token: str):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    
    # Lien de désinscription (pointant vers ton serveur local pour l'instant)
    unsubscribe_link = f"http://127.0.0.1:8000/api/v1/unsubscribe?token={token}"
    
    payload = {
        "sender": {"name": "Azimut", "email": "arthurlouette12@gmail.com"}, # ⚠️ À REMPLACER
        "to": [{"email": to_email}],
        "subject": "Bienvenue dans la newsletter de la section ! 🏕️",
        "htmlContent": f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2E7D32;">Bienvenue !</h2>
            <p>Tu es maintenant inscrit(e) pour recevoir toutes les informations de la section.</p>
            <br><br>
            <p style="font-size: 12px; color: gray;">
                Pour te désabonner à tout moment, <a href="{unsubscribe_link}">clique ici</a>.
            </p>
        </div>
        """
    }
    
    # On envoie la requête à Brevo
    response = requests.post(url, json=payload, headers=headers)
    
    # Petit affichage dans le terminal pour vérifier que ça a marché
    if response.status_code == 201:
        print(f"✅ E-mail envoyé avec succès à {to_email}")
    else:
        print(f"❌ Erreur lors de l'envoi : {response.text}")

# Modèle de données pour valider l'e-mail reçu
class SubscriberRequest(BaseModel):
    email: EmailStr
    section_id: int = 1  # Par défaut la section 1 (Troupe)

class MassEmailRequest(BaseModel):
    subject: str
    message: str
    section_id: int = 1

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
        
        # On récupère les données de l'abonné UNE SEULE FOIS :
        subscriber_data = response.data[0]
        token = subscriber_data["unsubscribe_token"]
        
        # Envoi du vrai e-mail de bienvenue
        send_welcome_email(payload.email, str(token))
        
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

@app.post("/api/v1/send-mass-newsletter")
def send_mass_newsletter(payload: MassEmailRequest):
    """Route admin pour envoyer un e-mail à tous les abonnés actifs d'une section"""
    try:
        # 1. Récupérer tous les abonnés actifs de la section depuis Supabase
        response = supabase.table("newsletter_subscribers") \
            .select("email, unsubscribe_token") \
            .eq("section_id", payload.section_id) \
            .eq("is_subscribed", True) \
            .execute()
        
        subscribers = response.data
        
        if not subscribers:
            raise HTTPException(status_code=404, detail="Aucun abonné actif trouvé pour cette section.")
            
        succes_count = 0
        
        # 2. Préparer l'envoi via Brevo
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }
        
        # 3. Boucler sur chaque abonné pour envoyer un e-mail personnalisé (avec son propre lien de désinscription)
        for sub in subscribers:
            unsubscribe_link = f"http://127.0.0.1:8000/api/v1/unsubscribe?token={sub['unsubscribe_token']}"
            
            # Formatage du message avec un design très épuré et le lien en bas
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="white-space: pre-wrap; font-size: 16px; color: #333;">{payload.message}</div>
                <br><br>
                <hr style="border: none; border-top: 1px solid #eaeaea; margin-top: 30px;">
                <p style="font-size: 11px; color: gray; text-align: center;">
                    Vous recevez cet e-mail car vous êtes inscrit à la newsletter de la section.<br>
                    Pour vous désabonner, <a href="{unsubscribe_link}" style="color: #2E7D32;">cliquez ici</a>.
                </p>
            </div>
            """
            
            brevo_payload = {
                "sender": {"name": "Les Chefs", "email": "arthurlouette12@gmail.com"},
                "to": [{"email": sub["email"]}],
                "subject": payload.subject,
                "htmlContent": html_content
            }
            
            res = requests.post(url, json=brevo_payload, headers=headers)
            if res.status_code == 201:
                succes_count += 1
                
        return {
            "status": "success", 
            "message": f"E-mail envoyé avec succès à {succes_count} abonnés !"
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi groupé : {str(e)}")