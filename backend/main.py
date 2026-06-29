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

# Activation du CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    
    unsubscribe_link = f"http://127.0.0.1:8000/api/v1/unsubscribe?token={token}"
    
    payload = {
        "sender": {"name": "Azimut", "email": "arthurlouette12@gmail.com"}, 
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
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        print(f"✅ E-mail envoyé avec succès à {to_email}")
    else:
        print(f"❌ Erreur lors de l'envoi : {response.text}")

# --- MODÈLES DE DONNÉES ---
class SubscriberRequest(BaseModel):
    email: EmailStr
    section_id: int = 1

class MassEmailRequest(BaseModel):
    subject: str
    message: str
    section_id: int = 1

class DirectEmailRequest(BaseModel):
    parent_email: EmailStr
    subject: str
    message: str
    chef_email: EmailStr  # Utilisé pour que le parent puisse lui répondre directement

# --- ROUTES ---

@app.post("/api/v1/subscribe")
def subscribe(payload: SubscriberRequest):
    try:
        response = supabase.table("newsletter_subscribers").insert({
            "section_id": payload.section_id,
            "email": payload.email,
            "is_subscribed": True
        }).execute()
        
        subscriber_data = response.data[0]
        token = subscriber_data["unsubscribe_token"]
        
        send_welcome_email(payload.email, str(token))
        
        return {"status": "success", "message": "Inscription validée avec succès.", "email": payload.email}
    except Exception as e:
        if "duplicate key value" in str(e):
            raise HTTPException(status_code=400, detail="Cet adresse e-mail est déjà inscrite.")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")

@app.get("/api/v1/unsubscribe")
def unsubscribe(token: str = Query(..., description="Le token UUID unique de désinscription")):
    try:
        response = supabase.table("newsletter_subscribers").update({"is_subscribed": False}).eq("unsubscribe_token", token).execute()
        if not response.data:
            raise HTTPException(status_code=44, detail="Jeton de désinscription invalide ou expiré.")
        return {"status": "success", "message": "Vous avez été désabonné de la newsletter avec succès."}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Erreur lors du désabonnement : {str(e)}")

@app.post("/api/v1/send-mass-newsletter")
def send_mass_newsletter(payload: MassEmailRequest):
    try:
        response = supabase.table("newsletter_subscribers").select("email, unsubscribe_token").eq("section_id", payload.section_id).eq("is_subscribed", True).execute()
        subscribers = response.data
        if not subscribers:
            raise HTTPException(status_code=404, detail="Aucun abonné actif trouvé pour cette section.")
            
        succes_count = 0
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {"accept": "application/json", "api-key": BREVO_API_KEY, "content-type": "application/json"}
        
        for sub in subscribers:
            unsubscribe_link = f"http://127.0.0.1:8000/api/v1/unsubscribe?token={sub['unsubscribe_token']}"
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
                "sender": {"name": "Le Staff", "email": "arthurlouette12@gmail.com"},
                "to": [{"email": sub["email"]}],
                "subject": payload.subject,
                "htmlContent": html_content
            }
            
            res = requests.post(url, json=brevo_payload, headers=headers)
            if res.status_code == 201: succes_count += 1
                
        return {"status": "success", "message": f"E-mail envoyé avec succès à {succes_count} abonnés !"}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi groupé : {str(e)}")

@app.post("/api/v1/send-direct-email")
def send_direct_email(payload: DirectEmailRequest):
    """Route admin pour envoyer un e-mail ciblé à un seul parent"""
    try:
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {"accept": "application/json", "api-key": BREVO_API_KEY, "content-type": "application/json"}
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="white-space: pre-wrap; font-size: 16px; color: #333;">{payload.message}</div>
            <br><br>
            <hr style="border: none; border-top: 1px solid #eaeaea; margin-top: 30px;">
            <p style="font-size: 11px; color: gray; text-align: center;">
                Cet e-mail vous a été envoyé directement par le Staff de votre section.
            </p>
        </div>
        """
        
        brevo_payload = {
            "sender": {"name": "Staff Scout", "email": "arthurlouette12@gmail.com"},
            "replyTo": {"email": payload.chef_email}, # MAGIE ICI : Les réponses iront au chef !
            "to": [{"email": payload.parent_email}],
            "subject": payload.subject,
            "htmlContent": html_content
        }
        
        res = requests.post(url, json=brevo_payload, headers=headers)
        if res.status_code == 201:
            return {"status": "success", "message": "E-mail envoyé avec succès au parent !"}
        else:
            raise HTTPException(status_code=res.status_code, detail=res.text)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'envoi : {str(e)}")

class SuperAdminSectionEmailRequest(BaseModel):
    subject: str
    message: str
    section_id: int
    unite_id: int

@app.post("/api/v1/send-superadmin-section-newsletter")
def send_superadmin_section_newsletter(payload: SuperAdminSectionEmailRequest):
    """Route SuperAdmin pour envoyer un e-mail au staff ET aux parents d'une section spécifique"""
    try:
        # 1. Vérifier que la section appartient bien à l'unité du Chef d'Unité (Sécurité)
        sec_check = supabase.table("sections").select("id").eq("id", payload.section_id).eq("unite_id", payload.unite_id).execute()
        if not sec_check.data:
            raise HTTPException(status_code=403, detail="Cette section n'appartient pas à votre unité.")

        # 2. Récupérer les parents (via les abonnements newsletter)
        parents_res = supabase.table("newsletter_subscribers").select("email, unsubscribe_token").eq("section_id", payload.section_id).eq("is_subscribed", True).execute()
        
        # 3. Récupérer les chefs (via la table admins)
        chefs_res = supabase.table("admins").select("email").eq("section_id", payload.section_id).execute()

        # Combiner intelligemment les e-mails (Pour éviter d'envoyer 2 fois si un chef est aussi parent)
        all_emails = {}
        for p in parents_res.data:
            all_emails[p["email"]] = {"type": "parent", "token": p["unsubscribe_token"]}
        for c in chefs_res.data:
            if c["email"] not in all_emails:
                all_emails[c["email"]] = {"type": "chef", "token": None}

        if not all_emails:
            raise HTTPException(status_code=404, detail="Aucun membre (parent ou chef) trouvé dans cette section.")

        succes_count = 0
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {"accept": "application/json", "api-key": BREVO_API_KEY, "content-type": "application/json"}

        # 4. Envoyer les e-mails
        for email, info in all_emails.items():
            if info["type"] == "parent":
                unsubscribe_link = f"http://127.0.0.1:8000/api/v1/unsubscribe?token={info['token']}"
                footer = f"""<br><br><hr style="border: none; border-top: 1px solid #eaeaea; margin-top: 30px;">
                             <p style="font-size: 11px; color: gray; text-align: center;">Désinscription parent : <a href="{unsubscribe_link}" style="color: #1E3A8A;">cliquez ici</a>.</p>"""
            else:
                footer = f"""<br><br><hr style="border: none; border-top: 1px solid #eaeaea; margin-top: 30px;">
                             <p style="font-size: 11px; color: gray; text-align: center;">Vous recevez cet e-mail en tant que membre du Staff de la section.</p>"""

            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h3 style="color: #1E3A8A;">Message de la Direction d'Unité</h3>
                <div style="white-space: pre-wrap; font-size: 16px; color: #333;">{payload.message}</div>
                {footer}
            </div>
            """
            
            brevo_payload = {
                "sender": {"name": "L'Unité Scoute", "email": "arthurlouette12@gmail.com"},
                "to": [{"email": email}],
                "subject": f"[UNITÉ] {payload.subject}",
                "htmlContent": html_content
            }
            
            res = requests.post(url, json=brevo_payload, headers=headers)
            if res.status_code == 201: succes_count += 1
                
        return {"status": "success", "message": f"E-mail envoyé avec succès à {succes_count} personnes (Staff & Parents) !"}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Erreur d'envoi : {str(e)}")