import requests
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"

# --- IDs DE TA BASE DE DONNÉES ---
UNITE_1_ID = 1
SEC_1A_LOUVETEAUX = 1
SEC_1B_BALADINS = 2

UNITE_2_ID = 2
SEC_2A_SCOUTS = 3

# --- EMAILS POUR TESTS DIRECTS ---
CHEF_LOUVETEAUX = "arthurlouette12+chefloup@gmail.com"
PARENT_LOUVETEAUX = "arthurlouette12+parentloup@gmail.com"

def print_test(num, description):
    print(f"\n⏳ TEST {num} : {description}")

def run_test(response):
    if response.status_code in [200, 201]:
        print(f"✅ SUCCÈS : {response.json().get('message', 'OK')}")
    else:
        print(f"❌ ÉCHEC ({response.status_code}) : {response.text}")
    time.sleep(1.5)  # Pause de 1.5s pour respecter les limites de Brevo

print("="*60)
print("🛡️ DÉMARRAGE DES TESTS D'ISOLATION AZIMUT 🛡️")
print("="*60)

# ---------------------------------------------------------
# BLOC 1 : TESTS DE NEWSLETTERS DE SECTION (ISOLATION INTERNE)
# ---------------------------------------------------------

print_test("1.1", "Newsletter Section 1A (Louveteaux)")
run_test(requests.post(f"{BASE_URL}/send-mass-newsletter", json={
    "subject": "[TEST 1.1] Uniquement pour Parent Louveteau",
    "message": "ATTENTE : Seul +parentloup@ doit recevoir cet e-mail. AUCUN autre parent.",
    "section_id": SEC_1A_LOUVETEAUX
}))

print_test("1.2", "Newsletter Section 1B (Baladins)")
run_test(requests.post(f"{BASE_URL}/send-mass-newsletter", json={
    "subject": "[TEST 1.2] Uniquement pour Parent Baladin",
    "message": "ATTENTE : Seul +parentbala@ doit recevoir cet e-mail. Les louveteaux ne doivent pas le voir.",
    "section_id": SEC_1B_BALADINS
}))

print_test("1.3", "Newsletter Section 2A (Scouts - Unité 2)")
run_test(requests.post(f"{BASE_URL}/send-mass-newsletter", json={
    "subject": "[TEST 1.3] Uniquement pour Parent Scout (Unité 2)",
    "message": "ATTENTE : Seul +parentscout@ doit recevoir ceci. Aucune fuite vers l'Unité 1 autorisée.",
    "section_id": SEC_2A_SCOUTS
}))


# ---------------------------------------------------------
# BLOC 2 : TESTS DE COMMUNICATION D'UNITÉ (ISOLATION EXTERNE)
# ---------------------------------------------------------

print_test("2.1", "Communiqué Global Unité 1")
run_test(requests.post(f"{BASE_URL}/send-unit-newsletter", json={
    "subject": "[TEST 2.1] Communiqué Unité 1",
    "message": "ATTENTE : +parentloup, +parentbala, +chefloup et +chefbala doivent le recevoir. Mais AUCUN email 'scout' de l'Unité 2.",
    "unite_id": UNITE_1_ID
}))

print_test("2.2", "Communiqué Global Unité 2")
run_test(requests.post(f"{BASE_URL}/send-unit-newsletter", json={
    "subject": "[TEST 2.2] Communiqué Unité 2",
    "message": "ATTENTE : Seuls +parentscout et +chefscout doivent le recevoir. L'Unité 1 ne doit rien recevoir.",
    "unite_id": UNITE_2_ID
}))


# ---------------------------------------------------------
# BLOC 3 : TESTS DE SÉCURITÉ ET CROISEMENTS INTERDITS
# ---------------------------------------------------------

print_test("3.1", "SuperAdmin Unité 1 essaie de contacter Section 2A (Unité 2) -> DOIT ÉCHOUER")
response_fail = requests.post(f"{BASE_URL}/send-superadmin-section-newsletter", json={
    "subject": "[TEST 3.1] HACKING",
    "message": "Ceci ne doit jamais partir.",
    "section_id": SEC_2A_SCOUTS,
    "unite_id": UNITE_1_ID  # Unité 1 tente d'envoyer à la section 3 (qui appartient à Unité 2)
})
if response_fail.status_code == 403:
    print("✅ SUCCÈS : Le backend a bloqué la tentative de fuite de données (Erreur 403) !")
else:
    print(f"❌ ÉCHEC CRITIQUE : La sécurité a failli ! Statut: {response_fail.status_code}")


# ---------------------------------------------------------
# BLOC 4 : TESTS DE MESSAGERIE DIRECTE CHEF <-> PARENT
# ---------------------------------------------------------

print_test("4.1", "Message Direct Chef Louveteaux -> Parent Louveteaux")
run_test(requests.post(f"{BASE_URL}/send-direct-email", json={
    "subject": "[TEST 4.1] Message privé pour votre enfant",
    "message": "ATTENTE : Reçu uniquement par +parentloup@, envoyé par le backend.",
    "chef_email": CHEF_LOUVETEAUX,
    "parent_email": PARENT_LOUVETEAUX
}))

print_test("4.2", "Message Direct Parent Louveteaux -> Chef Louveteaux")
run_test(requests.post(f"{BASE_URL}/send-parent-to-chef-email", json={
    "subject": "[TEST 4.2] Question sur le camp",
    "message": "ATTENTE : Reçu uniquement par +chefloup@.",
    "chef_email": CHEF_LOUVETEAUX,
    "parent_email": PARENT_LOUVETEAUX
}))

print("="*60)
print("🏁 FIN DE LA PROCÉDURE DE TESTS AUTOMATISÉS 🏁")
print("👉 Vérifie ta boîte mail (arthurlouette12@gmail.com) pour analyser les alias des destinataires !")
print("="*60)