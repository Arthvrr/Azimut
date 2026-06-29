INSERT INTO sections (unite_id, nom, code_parent, code_chef) 
VALUES (
    1,                         -- L'ID de l'unité (1 pour les 4 Chênes, ou l'ID de la nouvelle unité créée)
    'Chaîne Guides',           -- Le nom de la section (Louveteaux, Troupe, Guides, Baladins...)
    'PARENTS-GUIDES',          -- Le code secret d'invitation pour les parents de cette section
    'STAFF-GUIDES-SECURE'      -- Le code secret d'invitation sécurisé pour le staff de cette section
);