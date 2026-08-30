# 📊 Limites de l'Architecture Gratuite - Azimut App

Ce document résume les contraintes des plans "Free" (gratuits) utilisés pour l'infrastructure du projet Azimut. Globalement, cette stack est extrêmement généreuse et permet de gérer une unité scoute entière sans frais, mais possède quelques goulots d'étranglement à surveiller.

---

## 1. Front-End : GitHub Pages
*Hébergement du site web et des interfaces (Espace Parent / Espace Chef)*

*   **Bande passante :** **100 GB** par mois.
*   **Stockage :** **1 GB** maximum pour le code source et les ressources (images, CSS).
*   **Limite de build :** 10 déploiements par heure (si tu utilises GitHub Actions).
*   **Verdict pour Azimut :** Limite **quasi-inatteignable**. Le site web est constitué de fichiers texte légers (HTML/JS/CSS). Tu peux avoir des dizaines de milliers de visites par mois sans jamais t'en soucier.

## 2. Back-End : Render (Plan Free)
*Hébergement de l'API Python / FastAPI*

*   **Ressources :** **512 MB** de RAM et **0.1** CPU.
*   **Mise en veille (Cold Start) :** Le serveur s'endort après **15 minutes d'inactivité**. Lorsqu'un parent se connecte après une période creuse, la première requête mettra environ 30 à 50 secondes à répondre le temps que le serveur se réveille.
*   **Temps d'exécution :** **750 heures** actives par mois (largement suffisant pour couvrir un mois complet de 730h).
*   **Verdict pour Azimut :** La mise en veille est le seul vrai défaut. Pour une app scoute (utilisation surtout le week-end ou en soirée), c'est acceptable. Si cela devient frustrant, le premier plan payant pour éviter la mise en veille coûte environ 7$/mois.

## 3. Base de Données : Supabase (Plan Free)
*Gestion des utilisateurs, des données et stockage des PDF*

*   **Base de données (PostgreSQL) :** **500 MB** de stockage de données pures (texte).
*   **Stockage de fichiers (Buckets) :** **1 GB** pour stocker les PDF (fiches médicales).
*   **Authentification :** Jusqu'à **50 000 utilisateurs actifs** par mois.
*   **Mise en veille :** Si le projet ne reçoit **aucune requête pendant 1 semaine**, la base de données est mise en pause. Il faut la relancer manuellement sur le site de Supabase.
*   **Verdict pour Azimut :** Très généreux sur les données (500 MB de texte, c'est des millions de lignes). En revanche, **le stockage de 1 GB pour les PDF devra être surveillé** si l'unité compte beaucoup de membres et que tu gardes les fiches des années précédentes.

## 4. Envoi d'E-mails : Brevo (Plan Free)
*Routage SMTP pour l'envoi des liens magiques et newsletters*

*   **Volume d'envoi :** **300 e-mails par jour** maximum.
*   **Contacts :** Nombre de contacts illimité.
*   **Logo Brevo :** Les e-mails envoyés via leurs templates (newsletters) incluent un petit logo Brevo en bas de page.
*   **Verdict pour Azimut :** **C'est le principal goulot d'étranglement de l'architecture.** Si tu as 250 parents dans l'unité et que le Staff d'Unité envoie une newsletter générale, le quota journalier est quasiment atteint d'un coup. Les 300 e-mails/jour incluent aussi les e-mails de connexion (liens magiques).

## 5. Réception d'E-mails : ImprovMX (Plan Free)
*Redirection des e-mails parents vers le staff*

*   **Domaine :** **1** seul nom de domaine configuré.
*   **Alias :** Jusqu'à **25 alias** gratuits (ex: communication@, staff@, baladins@).
*   **Volume de transfert :** **500 e-mails redirigés par jour**.
*   **Vitesse :** Traitement standard (pas de priorité premium), quelques secondes de délai.
*   **Verdict pour Azimut :** Parfaitement dimensionné. Il est rarissime qu'une unité reçoive plus de 500 e-mails de parents le même jour.

## 6. Nom de Domaine : Hostinger
*Achat du domaine azimut-app.be et gestion DNS*

*   **Coût :** Il n'y a pas de plan gratuit pour la possession d'un domaine (paiement annuel requis, généralement entre 10€ et 15€/an).
*   **Gestion DNS :** La modification des zones DNS (les fameuses règles MX, TXT, CNAME) est **gratuite et illimitée** avec l'achat du domaine.
*   **Verdict pour Azimut :** Aucun blocage technique ici, la seule contrainte est de penser à renouveler le domaine chaque année pour ne pas que l'application "casse" intégralement.

---

### 🚨 Résumé de Scalabilité (Quand faudra-t-il payer ?)

Si l'application Azimut est utilisée par une unité standard de **100 à 200 animés**, l'architecture actuelle à **0€/mois** tiendra parfaitement la route.

**Les 3 limites qui forceront un passage à un plan payant (par ordre chronologique probable) :**
1. **Le quota de 300 e-mails/jour (Brevo) :** Si les envois de masse deviennent fréquents ou que l'unité dépasse les 250 membres.
2. **Le temps de réveil du serveur (Render) :** Si les chefs se plaignent que l'application met trop de temps à charger lors de la première connexion.
3. **Le stockage des PDF (Supabase) :** Au bout de 2 ou 3 ans, le plafond de 1 GB pourrait être atteint si les anciens PDF ne sont pas supprimés de la base.