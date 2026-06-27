from supabase import create_client, Client

# Tes identifiants exacts
URL_SUPABASE = "https://nbhpninmmpayivjqhouj.supabase.co"
CLE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5iaHBuaW5tbXBheWl2anFob3VqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI1NTgyNzMsImV4cCI6MjA5ODEzNDI3M30.A6BdwmCVq6uWK6hlNekvetek3Er3LfO67vfwlRPpcpU"

# Création de la connexion
supabase: Client = create_client(URL_SUPABASE, CLE_SUPABASE)

print("Tentative de connexion à Azimut...")

try:
    # On insère un e-mail de test lié à la section 1
    reponse = supabase.table('newsletter_subscribers').insert({
        "section_id": 1,
        "email": "parent.test@gmail.com"
    }).execute()
    
    print("✅ Succès ! L'abonné a été ajouté à la base de données.")
    print("Données reçues :", reponse.data)
    
except Exception as e:
    print("❌ Une erreur est survenue :", e)