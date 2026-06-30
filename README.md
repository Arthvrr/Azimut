# 🧭 Azimut - La boussole de votre Unité Scoute

**Azimut** est une plateforme SaaS (Software as a Service) conçue spécifiquement pour la gestion administrative et communicationnelle des unités scoutes et mouvements de jeunesse. 

Fini les groupes WhatsApp illisibles et les feuilles médicales perdues en forêt. Azimut centralise les documents, automatise les envois d'e-mails et respecte strictement le cloisonnement des données entre les différentes sections d'une unité.

---

## ✨ Fonctionnalités Principales

- 📁 **Dossier Administratif Centralisé** : Upload et stockage sécurisé des documents PDF (fiche médicale, autorisation parentale, assurance) avec limitation de taille stricte (300 Ko max) pour optimiser les serveurs.
- ✉️ **Communication Intégrée** : Système de newsletter intégré permettant d'envoyer des e-mails ciblés par section ou à l'ensemble de l'unité.
- 📅 **Éphéméride & Absences** : Calendrier interactif par section. Les parents peuvent signaler une absence en un clic, directement répercutée sur le tableau de bord du Staff.
- 🔄 **Smart Rollover (Purge Estivale)** : Une fonctionnalité de réinitialisation annuelle intelligente. En août, un bouton permet de purger le calendrier, les absences et les vieux PDF médicaux tout en **conservant les profils parents et enfants** pour l'année suivante.
- 📱 **Progressive Web App (PWA)** : Interface responsive installable directement sur l'écran d'accueil des smartphones iOS et Android comme une application native.

---

## 🏗️ Architecture et Rôles

L'application est calquée sur la hiérarchie réelle d'une unité scoute. Les données sont strictement isolées par section pour garantir la confidentialité (RGPD).

### 1. 🏢 La Direction d'Unité (`superadmin`)
- N'est rattachée à aucune section spécifique, mais supervise l'unité entière.
- Possède une vue globale via un **Annuaire d'Unité**.
- Peut envoyer un communiqué général à **tous** les parents et staffs de l'unité.
- Gère la purge annuelle (Smart Rollover).

### 2. 🏕️ Le Staff de Section (`admin`)
- Gère un environnement cloisonné (sa propre section : ex. Louveteaux).
- N'a accès qu'aux enfants inscrits dans sa section.
- Gère l'agenda de la section, la validation des fiches médicales et suit les absences.
- Envoie des newsletters ciblées aux parents abonnés à sa section.

### 3. 👨‍👩‍👧 Les Familles (`parent`)
- Disposent d'un compte **unique** basé sur leur e-mail.
- Peuvent gérer **plusieurs enfants** répartis dans des **sections différentes**.
- Le tableau de bord parent fusionne automatiquement les calendriers des différentes sections de leurs enfants.
- Gestion autonome des abonnements aux newsletters par section.

---

## 🛠️ Stack Technique

Azimut s'appuie sur des technologies modernes, légères et performantes pour garantir une expérience fluide et des coûts d'infrastructure minimes.

### Front-end (Client)
- **HTML5 / Vanilla JS** : Code brut et léger, sans framework lourd.
- **Tailwind CSS** : Stylisation moderne, rapide et entièrement responsive (via CDN).
- **FullCalendar.js** : Rendu des éphémérides et gestion des événements interactifs.
- **PWA** : Intégration d'un `manifest.json` et d'un Service Worker (`sw.js`).

### Back-end (Serveur)
- **Python 3 / FastAPI** : API REST ultra-rapide et typée pour gérer les requêtes sensibles (envoi d'e-mails, requêtes complexes de purge).
- **Uvicorn** : Serveur ASGI pour propulser l'API.

### Infrastructure & Services Tiers
- **Supabase (BaaS)** : 
  - *PostgreSQL* : Base de données relationnelle complexe.
  - *Supabase Auth* : Gestion sécurisée de l'authentification et des mots de passe.
  - *Supabase Storage* : Stockage des documents PDF au sein de buckets sécurisés.
- **Brevo (ex-Sendinblue)** :
  - API utilisée pour l'envoi des e-mails transactionnels (Bienvenue, Mot de passe oublié) et des campagnes (Newsletters de section et d'unité).