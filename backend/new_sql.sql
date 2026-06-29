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