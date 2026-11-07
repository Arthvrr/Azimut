# SENTINEL.md

# Azimut est une web app permettant de centraliser toute la communication entre les parents d'animés et les chefs scouts.

## Stack technique

- **Front-end :** HTML, Vanilla JavaScript, Tailwind CSS, FullCalendar.js.
- **Back-end :** Python, FastAPI, Uvicorn.
- **Base de données :** Supabase (PostgreSQL, Auth et Storage).
- **E-mails :** Brevo.
- **Hébergement :** Hostinger, Render et GitHub Pages.
- **Gestion des e-mails :** ImprovMX.

## Contexte fonctionnel

Azimut permet de centraliser :
- Les profils des parents et des enfants.
- Les documents administratifs et médicaux (PDF).
- Les calendriers et éphémérides par section.
- La gestion des absences.
- Les newsletters et communications par e-mail.
- La gestion annuelle des données (Smart Rollover).

L'application possède trois rôles :
- **superadmin :** direction d'unité, accès global à l'unité.
- **admin :** staff de section, accès limité à sa section.
- **parent :** accès uniquement aux informations de sa propre famille et de ses enfants.

Un parent peut avoir plusieurs enfants répartis dans différentes sections.

## Mission de sécurité

Analyse les commits Git et le code source afin de détecter toute vulnérabilité pouvant compromettre la sécurité des données d'Azimut.

Accorde une attention particulière à :

- **Supabase :** politiques RLS, permissions SQL et accès à la base de données.
- **Authentification :** contournement des connexions et élévation de privilèges.
- **Cloisonnement :** impossibilité pour un parent d'accéder aux données d'une autre famille ou pour un chef d'accéder à une autre section.
- **Documents :** confidentialité des fiches médicales et PDF stockés dans Supabase Storage.
- **FastAPI :** IDOR, injections SQL et accès non autorisés aux endpoints.
- **Secrets :** exposition de clés API, mots de passe et identifiants dans le code ou l'historique Git.
- **Brevo :** accès non autorisés aux fonctionnalités d'envoi d'e-mails et aux listes de destinataires.

**Priorité absolue :** protéger les données personnelles et médicales des enfants et des familles, conformément au RGPD.

Ne fais jamais confiance aux restrictions uniquement implémentées côté client. Ne modifie pas les données ou la configuration de production sans autorisation.