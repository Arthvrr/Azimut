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