-- 1. Nettoyage sécurisé
DELETE FROM newsletter_subscribers WHERE email LIKE 'arthurlouette12+parent%';
DELETE FROM admins WHERE email LIKE 'arthurlouette12+chef%' OR email LIKE 'arthurlouette12+superadmin%';
DELETE FROM sections WHERE id IN (1, 2, 3);
DELETE FROM unites WHERE id IN (1, 2);

-- 2. Création des Unités (CORRIGÉ : ajout de la colonne code_nom)
INSERT INTO unites (id, code_nom, nom_complet, code_superadmin) VALUES 
(1, '4CHENES', 'Unité des 4 Chênes', 'SUPER1'),
(2, 'GCERF', 'Unité du Grand Cerf', 'SUPER2');

-- 3. Création des Sections
INSERT INTO sections (id, unite_id, nom, code_chef, code_parent) VALUES 
(1, 1, 'Louveteaux', 'CHEF1', 'PAR1'),
(2, 1, 'Baladins', 'CHEF2', 'PAR2'),
(3, 2, 'Scouts', 'CHEF3', 'PAR3');

-- 4. Création des Admins (Staffs de section & Direction d'unité)
INSERT INTO admins (email, first_name, last_name, totem, role, section_id, unite_id) VALUES 
('arthurlouette12+chefloup@gmail.com', 'Chef', 'Loup', 'Akéla', 'chef', 1, NULL),
('arthurlouette12+chefbala@gmail.com', 'Chef', 'Baladin', 'Baloo', 'chef', 2, NULL),
('arthurlouette12+chefscout@gmail.com', 'Chef', 'Scout', 'Bagheera', 'chef', 3, NULL),
('arthurlouette12+superadmin1@gmail.com', 'Staff', 'Unité 1', 'Ocelot', 'super_admin', NULL, 1);

-- 5. Création des Abonnés (Parents)
INSERT INTO newsletter_subscribers (email, section_id, is_subscribed) VALUES 
('arthurlouette12+parentloup@gmail.com', 1, TRUE),
('arthurlouette12+parentbala@gmail.com', 2, TRUE),
('arthurlouette12+parentscout@gmail.com', 3, TRUE);