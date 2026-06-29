-- 1. Table des Unités
CREATE TABLE unites (
    id SERIAL PRIMARY KEY,
    code_nom VARCHAR(10) UNIQUE NOT NULL, -- ex: 'T4C'
    nom_complet VARCHAR(255) NOT NULL,    -- ex: 'Unité des 4 Chênes'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Table des Sections
CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    unite_id INT REFERENCES unites(id) ON DELETE CASCADE,
    nom VARCHAR(255) NOT NULL,            -- ex: 'Troupe', 'Louveteaux'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Table des Profils (Chefs / Admins)
-- Supabase gère la connexion, on stocke ici les rôles
CREATE TABLE profils (
    id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY, 
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) CHECK (role IN ('admin', 'parent')) DEFAULT 'parent',
    section_id INT REFERENCES sections(id) ON DELETE CASCADE, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Table de la Newsletter (Abonnements des parents)
CREATE TABLE newsletter_subscribers (
    id SERIAL PRIMARY KEY,
    section_id INT REFERENCES sections(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    is_subscribed BOOLEAN DEFAULT TRUE,
    unsubscribe_token UUID DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Cette contrainte empêche un parent de s'abonner 2 fois à la même section
    UNIQUE(section_id, email) 
);

-- --- DONNÉES DE DÉPART POUR TESTER --- --
-- On crée ton Unité
INSERT INTO unites (code_nom, nom_complet) 
VALUES ('T4C', 'Unité des 4 Chênes');

-- On crée ta Section (qui appartient à l'unité 1)
INSERT INTO sections (unite_id, nom) 
VALUES (1, 'Troupe Scoute');

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    section_id INT DEFAULT 1,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE events ADD COLUMN location VARCHAR(255);

-- 1. Création de la table des enfants
CREATE TABLE children (
    id SERIAL PRIMARY KEY,
    parent_email VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    medical_file_url TEXT,
    allergies TEXT,
    care_instructions TEXT,
    parent1_name VARCHAR(255),
    parent1_phone VARCHAR(255),
    parent2_name VARCHAR(255),
    parent2_phone VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Création de la table des absences
CREATE TABLE absences (
    id SERIAL PRIMARY KEY,
    event_id INT REFERENCES events(id) ON DELETE CASCADE,
    child_id INT REFERENCES children(id) ON DELETE CASCADE,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(event_id, child_id) -- Empêche de signaler deux fois la même absence
);

-- 1. Autoriser la lecture publique des PDF (Nécessaire car le bucket est public)
CREATE POLICY "Lecture publique" 
ON storage.objects FOR SELECT 
USING ( bucket_id = 'medical_files' );

-- 2. Autoriser les parents connectés à uploader un fichier
CREATE POLICY "Upload pour parents" 
ON storage.objects FOR INSERT 
TO authenticated 
WITH CHECK ( bucket_id = 'medical_files' );

-- 3. Autoriser les parents connectés à modifier/remplacer un fichier existant
CREATE POLICY "Update pour parents" 
ON storage.objects FOR UPDATE 
TO authenticated 
USING ( bucket_id = 'medical_files' );

-- ==========================================
-- 0. NETTOYAGE DE L'ANCIENNE BASE (Prototype)
-- ==========================================
DROP TABLE IF EXISTS absences CASCADE;
DROP TABLE IF EXISTS children CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS newsletter_subscribers CASCADE;
DROP TABLE IF EXISTS profils CASCADE;
DROP TABLE IF EXISTS admins CASCADE;
DROP TABLE IF EXISTS sections CASCADE;
DROP TABLE IF EXISTS unites CASCADE;

-- ==========================================
-- 1. STRUCTURE HIÉRARCHIQUE AVEC CODES SECRETS
-- ==========================================
CREATE TABLE unites (
    id SERIAL PRIMARY KEY,
    code_nom VARCHAR(10) UNIQUE NOT NULL, 
    nom_complet VARCHAR(255) NOT NULL,    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    unite_id INT REFERENCES unites(id) ON DELETE CASCADE NOT NULL,
    nom VARCHAR(255) NOT NULL,
    code_parent VARCHAR(50) NOT NULL, -- NOUVEAU: Le code à donner aux parents
    code_chef VARCHAR(50) NOT NULL,   -- NOUVEAU: Le code sécurisé pour le staff
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- 2. LES GESTIONNAIRES (Chefs / Staff)
-- ==========================================
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    totem VARCHAR(255),
    section_id INT REFERENCES sections(id) ON DELETE CASCADE NOT NULL,
    role VARCHAR(50) DEFAULT 'chef',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- 3. DONNÉES DE LA SECTION
-- ==========================================
CREATE TABLE children (
    id SERIAL PRIMARY KEY,
    parent_email VARCHAR(255) NOT NULL,
    section_id INT REFERENCES sections(id) ON DELETE CASCADE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    medical_file_url TEXT,
    allergies TEXT,
    care_instructions TEXT,
    parent1_name VARCHAR(255),
    parent1_phone VARCHAR(255),
    parent2_name VARCHAR(255),
    parent2_phone VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    section_id INT REFERENCES sections(id) ON DELETE CASCADE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE absences (
    id SERIAL PRIMARY KEY,
    event_id INT REFERENCES events(id) ON DELETE CASCADE NOT NULL,
    child_id INT REFERENCES children(id) ON DELETE CASCADE NOT NULL,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(event_id, child_id)
);

CREATE TABLE newsletter_subscribers (
    id SERIAL PRIMARY KEY,
    section_id INT REFERENCES sections(id) ON DELETE CASCADE NOT NULL,
    email VARCHAR(255) NOT NULL,
    is_subscribed BOOLEAN DEFAULT TRUE,
    unsubscribe_token UUID DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(section_id, email) 
);

-- ==========================================
-- 4. CRÉATION DE TON UNITÉ ET TES SECTIONS
-- ==========================================
-- Création de ton Unité
INSERT INTO unites (code_nom, nom_complet) VALUES ('T4C', 'Unité des 4 Chênes');

-- Création de la Troupe (avec ses 2 codes secrets !)
INSERT INTO sections (unite_id, nom, code_parent, code_chef) 
VALUES (1, 'Troupe Scoute', 't4c-25-26', 'MORUE-IS-COOKED');

-- Ton profil officiel de Chef (lié à la Troupe)
INSERT INTO admins (email, first_name, last_name, totem, section_id, role) 
VALUES ('arthurlouette12@gmail.com', 'Arthur', 'Louette', 'Galgo', 1, 'animateur_responsable');

-- ==========================================
-- 1. STRUCTURE HIÉRARCHIQUE AVEC CODES SECRETS
-- ==========================================
CREATE TABLE IF NOT EXISTS unites (
    id SERIAL PRIMARY KEY,
    code_nom VARCHAR(10) UNIQUE NOT NULL, 
    nom_complet VARCHAR(255) NOT NULL,
    code_superadmin VARCHAR(50) NOT NULL, -- Code pour les chefs d'unité
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sections (
    id SERIAL PRIMARY KEY,
    unite_id INT REFERENCES unites(id) ON DELETE CASCADE NOT NULL,
    nom VARCHAR(255) NOT NULL,
    code_parent VARCHAR(50) NOT NULL,
    code_chef VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- 2. LES GESTIONNAIRES (Chefs / Staff)
-- ==========================================
CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    totem VARCHAR(255),
    section_id INT REFERENCES sections(id) ON DELETE CASCADE, -- Optionnel (Null pour un chef d'unité)
    unite_id INT REFERENCES unites(id) ON DELETE CASCADE NOT NULL, -- NOUVEAU : Toujours lié à une unité
    role VARCHAR(50) DEFAULT 'chef', -- 'chef' ou 'super_admin'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- 3. DONNÉES DE LA SECTION
-- ==========================================
CREATE TABLE IF NOT EXISTS children (
    id SERIAL PRIMARY KEY,
    parent_email VARCHAR(255) NOT NULL,
    section_id INT REFERENCES sections(id) ON DELETE CASCADE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    medical_file_url TEXT,
    allergies TEXT,
    care_instructions TEXT,
    parent1_name VARCHAR(255),
    parent1_phone VARCHAR(255),
    parent2_name VARCHAR(255),
    parent2_phone VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    section_id INT REFERENCES sections(id) ON DELETE CASCADE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS absences (
    id SERIAL PRIMARY KEY,
    event_id INT REFERENCES events(id) ON DELETE CASCADE NOT NULL,
    child_id INT REFERENCES children(id) ON DELETE CASCADE NOT NULL,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(event_id, child_id)
);

CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id SERIAL PRIMARY KEY,
    section_id INT REFERENCES sections(id) ON DELETE CASCADE NOT NULL,
    email VARCHAR(255) NOT NULL,
    is_subscribed BOOLEAN DEFAULT TRUE,
    unsubscribe_token UUID DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(section_id, email) 
);

-- 1. On ajoute proprement la colonne manquante à la table existante
ALTER TABLE unites ADD COLUMN IF NOT EXISTS code_superadmin VARCHAR(50) DEFAULT 'SUPER-UNITE-SECURE';

-- 2. On réexécute ta commande de mise à jour qui va maintenant fonctionner à 100%
UPDATE unites 
SET code_superadmin = 't4c-25-26' 
WHERE code_nom = 'T4C';

-- ==========================================================
-- LE GRAND CHECK-UP AZIMUT (Mise à jour sans perte de données)
-- ==========================================================

-- 1. Table UNITES : Ajout du code superadmin
ALTER TABLE unites ADD COLUMN IF NOT EXISTS code_superadmin VARCHAR(50) DEFAULT 'SUPER-UNITE-SECURE';

-- 2. Table SECTIONS : Ajout des codes d'invitation
ALTER TABLE sections ADD COLUMN IF NOT EXISTS code_parent VARCHAR(50) DEFAULT 'PARENTS-CODE';
ALTER TABLE sections ADD COLUMN IF NOT EXISTS code_chef VARCHAR(50) DEFAULT 'STAFF-CODE';

-- 3. Table ADMINS : Ajout de l'Unité et du Rôle
ALTER TABLE admins ADD COLUMN IF NOT EXISTS unite_id INT REFERENCES unites(id) ON DELETE CASCADE;
ALTER TABLE admins ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'chef';

-- Un chef d'unité n'a pas de section, on rend donc ce champ optionnel (Très important !)
ALTER TABLE admins ALTER COLUMN section_id DROP NOT NULL;

-- On lie automatiquement tes chefs existants (comme Arthur Louette) à l'unité de leur section
UPDATE admins 
SET unite_id = (SELECT unite_id FROM sections WHERE sections.id = admins.section_id) 
WHERE section_id IS NOT NULL AND unite_id IS NULL;

-- 4. Table CHILDREN : Ajout de la section
ALTER TABLE children ADD COLUMN IF NOT EXISTS section_id INT REFERENCES sections(id) ON DELETE CASCADE;

-- 5. Table EVENTS : Ajout de la localisation et de la section
ALTER TABLE events ADD COLUMN IF NOT EXISTS location VARCHAR(255);
ALTER TABLE events ADD COLUMN IF NOT EXISTS section_id INT REFERENCES sections(id) ON DELETE CASCADE;

-- ==========================================================
-- 6. APPLICATION DE TA MISE À JOUR (Code Unité T4C)
-- ==========================================================
UPDATE unites 
SET code_superadmin = 't4c-25-26' 
WHERE code_nom = 'T4C';

-- ==========================================================
-- 7. LA COMMANDE MAGIQUE (Vide la mémoire cache de Supabase)
-- ==========================================================
NOTIFY pgrst, 'reload schema';

ALTER TABLE children ADD COLUMN IF NOT EXISTS parental_auth_url TEXT;
ALTER TABLE children ADD COLUMN IF NOT EXISTS insurance_file_url TEXT;