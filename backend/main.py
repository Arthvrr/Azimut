import os
import requests
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Les variables d'environnement SUPABASE_URL ou SUPABASE_KEY sont manquantes.")

app = FastAPI(title="Azimut API", version="1.0")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_section_and_unit_names(section_id: int):
    res = supabase.table("sections").select("nom, unites(nom_complet)").eq("id", section_id).execute()
    if not res.data: return "Section", "Unité Scoute"
    return res.data[0]["nom"], res.data[0]["unites"]["nom_complet"]

def send_welcome_email(to_email: str, token: str, section_id: int):
    sec_nom, unite_nom = get_section_and_unit_names(section_id)
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {"accept": "application/json", "api-key": BREVO_API_KEY, "content-type": "application/json"}
    unsubscribe_link = f"http://127.0.0.1:8000/api/v1/unsubscribe?token={token}"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
        <h2 style="color: #2E7D32; text-align: center;">Bienvenue chez {sec_nom} ! 🏕️</h2>
        <p style="font-size: 15px; color: #333; line-height: 1.5;">Bonjour,</p>
        <p style="font-size: 15px; color: #333; line-height: 1.5;">Tu es maintenant inscrit(e) sur la liste de diffusion officielle de la <strong>{sec_nom}</strong> ({unite_nom}).</p>
        <p style="font-size: 15px; color: #333; line-height: 1.5;">Tu recevras bientôt les convocations, les éphémérides et toutes les actualités importantes envoyées par le Staff.</p>
        <br>
        <p style="font-size: 15px; color: #333;">Salutations scoutes,<br><strong>Le Staff {sec_nom}</strong></p>
        <hr style="border: none; border-top: 1px solid #eaeaea; margin-top: 30px; margin-bottom: 20px;">
        <p style="font-size: 11px; color: gray; text-align: center;">
            Ceci est un message automatique.<br>Pour te désabonner à tout moment, <a href="{unsubscribe_link}" style="color: #2E7D32;">clique ici</a>.
        </p>
    </div>
    """
    
    payload = {"sender": {"name": f"Staff {sec_nom}", "email": "arthurlouette12@gmail.com"}, "to": [{"email": to_email}], "subject": f"Inscription confirmée - {sec_nom}", "htmlContent": html_content}
    requests.post(url, json=payload, headers=headers)

# --- NOUVEAU : STRUCTURE DE PIÈCE JOINTE ---
class Attachment(BaseModel):
    name: str
    content: str # Sera encodé en base64 par le front-end

class SubscriberRequest(BaseModel):
    email: EmailStr
    section_id: int

class MassEmailRequest(BaseModel):
    subject: str
    message: str
    section_id: int
    attachment: Optional[Attachment] = None

class DirectEmailRequest(BaseModel):
    parent_email: EmailStr
    subject: str
    message: str
    chef_email: EmailStr
    attachment: Optional[Attachment] = None

class UnitEmailRequest(BaseModel):
    subject: str
    message: str
    unite_id: int
    attachment: Optional[Attachment] = None

class SuperAdminSectionEmailRequest(BaseModel):
    subject: str
    message: str
    section_id: int
    unite_id: int

class ParentToChefEmailRequest(BaseModel):
    chef_email: EmailStr
    subject: str
    message: str
    parent_email: EmailStr

# --- ROUTES ---

@app.post("/api/v1/subscribe")
def subscribe(payload: SubscriberRequest):
    try:
        response = supabase.table("newsletter_subscribers").insert({"section_id": payload.section_id, "email": payload.email, "is_subscribed": True}).execute()
        token = response.data[0]["unsubscribe_token"]
        send_welcome_email(payload.email, str(token), payload.section_id)
        return {"status": "success", "message": "Inscription validée avec succès."}
    except Exception as e:
        if "duplicate key value" in str(e): raise HTTPException(status_code=400, detail="Cet adresse e-mail est déjà inscrite.")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/unsubscribe")
def unsubscribe(token: str = Query(...)):
    try:
        response = supabase.table("newsletter_subscribers").update({"is_subscribed": False}).eq("unsubscribe_token", token).execute()
        if not response.data: raise HTTPException(status_code=44, detail="Jeton invalide ou expiré.")
        return {"status": "success", "message": "Vous avez été désabonné de la newsletter avec succès."}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/send-mass-newsletter")
def send_mass_newsletter(payload: MassEmailRequest):
    try:
        sec_nom, unite_nom = get_section_and_unit_names(payload.section_id)
        subscribers = supabase.table("newsletter_subscribers").select("email, unsubscribe_token").eq("section_id", payload.section_id).eq("is_subscribed", True).execute().data
        if not subscribers: raise HTTPException(status_code=404, detail="Aucun abonné actif trouvé.")
            
        succes_count = 0
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {"accept": "application/json", "api-key": BREVO_API_KEY, "content-type": "application/json"}
        
        for sub in subscribers:
            unsubscribe_link = f"http://127.0.0.1:8000/api/v1/unsubscribe?token={sub['unsubscribe_token']}"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                <h3 style="color: #2E7D32; margin-top: 0;">Newsletter {sec_nom}</h3>
                <div style="white-space: pre-wrap; font-size: 15px; color: #333; line-height: 1.5;">{payload.message}</div>
                <br><br>
                <hr style="border: none; border-top: 1px solid #eaeaea; margin-top: 20px; margin-bottom: 20px;">
                <p style="font-size: 11px; color: gray; text-align: center; margin: 0;">
                    Cet e-mail vous a été envoyé par le Staff de la <strong>{sec_nom}</strong> ({unite_nom}).<br>
                    Pour vous désabonner, <a href="{unsubscribe_link}" style="color: #2E7D32;">cliquez ici</a>.
                </p>
            </div>
            """
            
            brevo_payload = {
                "sender": {"name": f"Staff {sec_nom}", "email": "arthurlouette12@gmail.com"},
                "to": [{"email": sub["email"]}],
                "subject": payload.subject,
                "htmlContent": html_content
            }
            if payload.attachment:
                brevo_payload["attachment"] = [{"name": payload.attachment.name, "content": payload.attachment.content}]
            
            if requests.post(url, json=brevo_payload, headers=headers).status_code == 201: succes_count += 1
                
        return {"status": "success", "message": f"E-mail envoyé avec succès à {succes_count} abonnés !"}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/send-direct-email")
def send_direct_email(payload: DirectEmailRequest):
    try:
        admin_res = supabase.table("admins").select("section_id, first_name, totem").eq("email", payload.chef_email).execute()
        if not admin_res.data: raise HTTPException(status_code=403, detail="Chef introuvable.")
        
        admin_info = admin_res.data[0]
        sec_nom, unite_nom = get_section_and_unit_names(admin_info["section_id"])
        totem_str = f" \"{admin_info['totem']}\"" if admin_info['totem'] else ""
        chef_name = f"{admin_info['first_name']}{totem_str}"

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {"accept": "application/json", "api-key": BREVO_API_KEY, "content-type": "application/json"}
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
            <h3 style="color: #2E7D32; margin-top: 0;">Message de {chef_name} (Staff {sec_nom})</h3>
            <div style="white-space: pre-wrap; font-size: 15px; color: #333; line-height: 1.5;">{payload.message}</div>
            <br><br>
            <hr style="border: none; border-top: 1px solid #eaeaea; margin-top: 20px; margin-bottom: 20px;">
            <p style="font-size: 11px; color: gray; text-align: center; margin: 0;">
                Cet e-mail personnel vous a été envoyé directement via le portail de l'<strong>{unite_nom}</strong>.<br>
                Vous pouvez y répondre directement, le message sera transmis à <strong>{chef_name}</strong>.
            </p>
        </div>
        """
        
        brevo_payload = {
            "sender": {"name": f"Staff {sec_nom}", "email": "arthurlouette12@gmail.com"},
            "replyTo": {"email": payload.chef_email}, 
            "to": [{"email": payload.parent_email}],
            "subject": payload.subject,
            "htmlContent": html_content
        }
        if payload.attachment:
            brevo_payload["attachment"] = [{"name": payload.attachment.name, "content": payload.attachment.content}]
        
        res = requests.post(url, json=brevo_payload, headers=headers)
        if res.status_code == 201: return {"status": "success", "message": "E-mail envoyé avec succès au parent !"}
        else: raise HTTPException(status_code=res.status_code, detail=res.text)
            
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/send-parent-to-chef-email")
def send_parent_to_chef_email(payload: ParentToChefEmailRequest):
    try:
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {"accept": "application/json", "api-key": BREVO_API_KEY, "content-type": "application/json"}
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
            <h3 style="color: #800020; margin-top: 0;">Message d'un Parent</h3>
            <div style="white-space: pre-wrap; font-size: 15px; color: #333; line-height: 1.5;">{payload.message}</div>
            <br><br>
            <hr style="border: none; border-top: 1px solid #eaeaea; margin-top: 20px; margin-bottom: 20px;">
            <p style="font-size: 11px; color: gray; text-align: center; margin: 0;">
                Envoyé par le parent : {payload.parent_email} via l'application Azimut.<br>
                Vous pouvez cliquer sur "Répondre" pour le contacter directement.
            </p>
        </div>
        """
        
        brevo_payload = {
            "sender": {"name": "Portail Parent", "email": "arthurlouette12@gmail.com"},
            "replyTo": {"email": payload.parent_email}, 
            "to": [{"email": payload.chef_email}],
            "subject": f"{payload.subject}",
            "htmlContent": html_content
        }
        
        res = requests.post(url, json=brevo_payload, headers=headers)
        if res.status_code == 201: return {"status": "success", "message": "Votre message a bien été transmis au chef !"}
        else: raise HTTPException(status_code=res.status_code, detail=res.text)
            
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/send-unit-newsletter")
def send_unit_newsletter(payload: UnitEmailRequest):
    try:
        unit_res = supabase.table("unites").select("nom_complet").eq("id", payload.unite_id).execute()
        unite_nom = unit_res.data[0]["nom_complet"] if unit_res.data else "L'Unité Scoute"

        sections_res = supabase.table("sections").select("id").eq("unite_id", payload.unite_id).execute()
        section_ids = [s["id"] for s in sections_res.data]
        if not section_ids: raise HTTPException(status_code=404, detail="Aucune section dans cette unité.")

        parents_res = supabase.table("newsletter_subscribers").select("email, unsubscribe_token").in_("section_id", section_ids).eq("is_subscribed", True).execute()
        chefs_res = supabase.table("admins").select("email").in_("section_id", section_ids).execute()

        all_emails = {}
        for p in parents_res.data: all_emails[p["email"]] = {"type": "parent", "token": p["unsubscribe_token"]}
        for c in chefs_res.data:
            if c["email"] not in all_emails: all_emails[c["email"]] = {"type": "chef", "token": None}

        if not all_emails: raise HTTPException(status_code=404, detail="Aucun membre trouvé.")

        succes_count = 0
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {"accept": "application/json", "api-key": BREVO_API_KEY, "content-type": "application/json"}
        
        for email, info in all_emails.items():
            if info["type"] == "parent":
                link = f"http://127.0.0.1:8000/api/v1/unsubscribe?token={info['token']}"
                footer = f'Désinscription (Espace Parent) : <a href="{link}" style="color: #1E3A8A;">cliquez ici</a>.'
            else:
                footer = f'Vous recevez ceci en tant que Staff.'

            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                <h3 style="color: #1E3A8A; margin-top: 0;">Communiqué du Staff d'Unité</h3>
                <div style="white-space: pre-wrap; font-size: 15px; color: #333; line-height: 1.5;">{payload.message}</div>
                <br><br>
                <hr style="border: none; border-top: 1px solid #eaeaea; margin-top: 20px; margin-bottom: 20px;">
                <p style="font-size: 11px; color: gray; text-align: center; margin: 0;">
                    Cet e-mail général a été envoyé à tous les membres de <strong>{unite_nom}</strong>.<br>{footer}
                </p>
            </div>
            """
            
            brevo_payload = {
                "sender": {"name": f"Staff d'Unité {unite_nom}", "email": "arthurlouette12@gmail.com"},
                "to": [{"email": email}],
                "subject": f"{payload.subject}",
                "htmlContent": html_content
            }
            if payload.attachment:
                brevo_payload["attachment"] = [{"name": payload.attachment.name, "content": payload.attachment.content}]
            
            if requests.post(url, json=brevo_payload, headers=headers).status_code == 201: succes_count += 1
                
        return {"status": "success", "message": f"E-mail envoyé avec succès à {succes_count} membres (Staffs & Parents) !"}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/send-superadmin-section-newsletter")
def send_superadmin_section_newsletter(payload: SuperAdminSectionEmailRequest):
    try:
        sec_check = supabase.table("sections").select("id").eq("id", payload.section_id).eq("unite_id", payload.unite_id).execute()
        if not sec_check.data: raise HTTPException(status_code=403, detail="Section hors de votre unité.")

        sec_nom, unite_nom = get_section_and_unit_names(payload.section_id)

        parents_res = supabase.table("newsletter_subscribers").select("email, unsubscribe_token").eq("section_id", payload.section_id).eq("is_subscribed", True).execute()
        chefs_res = supabase.table("admins").select("email").eq("section_id", payload.section_id).execute()

        all_emails = {}
        for p in parents_res.data: all_emails[p["email"]] = {"type": "parent", "token": p["unsubscribe_token"]}
        for c in chefs_res.data:
            if c["email"] not in all_emails: all_emails[c["email"]] = {"type": "chef", "token": None}

        if not all_emails: raise HTTPException(status_code=404, detail="Aucun membre trouvé dans la section.")

        succes_count = 0
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {"accept": "application/json", "api-key": BREVO_API_KEY, "content-type": "application/json"}

        for email, info in all_emails.items():
            if info["type"] == "parent":
                link = f"http://127.0.0.1:8000/api/v1/unsubscribe?token={info['token']}"
                footer = f'Désinscription : <a href="{link}" style="color: #1E3A8A;">cliquez ici</a>.'
            else:
                footer = f'Vous recevez ceci en tant que Staff de la {sec_nom}.'

            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                <h3 style="color: #1E3A8A; margin-top: 0;">Message du Staff d'Unité ({sec_nom})</h3>
                <div style="white-space: pre-wrap; font-size: 15px; color: #333; line-height: 1.5;">{payload.message}</div>
                <br><br>
                <hr style="border: none; border-top: 1px solid #eaeaea; margin-top: 20px; margin-bottom: 20px;">
                <p style="font-size: 11px; color: gray; text-align: center; margin: 0;">
                    Envoyé par les Chefs d'Unité de <strong>{unite_nom}</strong>.<br>{footer}
                </p>
            </div>
            """
            
            brevo_payload = {
                "sender": {"name": f"Staff d'Unité {unite_nom}", "email": "arthurlouette12@gmail.com"},
                "to": [{"email": email}],
                "subject": f"[{sec_nom}] {payload.subject}",
                "htmlContent": html_content
            }
            
            if requests.post(url, json=brevo_payload, headers=headers).status_code == 201: succes_count += 1
                
        return {"status": "success", "message": f"E-mail envoyé avec succès à {succes_count} membres de la {sec_nom} !"}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))