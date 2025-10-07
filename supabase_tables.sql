-- Table de test pour Supabase
-- Exécuter ce script dans l'éditeur SQL de Supabase

-- Créer une table de test
CREATE TABLE IF NOT EXISTS test_data (
    id SERIAL PRIMARY KEY,
    test_field TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insérer des données de test
INSERT INTO test_data (test_field) VALUES
    ('Test 1'),
    ('Test 2'),
    ('Test 3');

-- Vérifier les données
SELECT * FROM test_data;

-- Pour les lectures bahá'íes (si nécessaire)
-- CREATE TABLE IF NOT EXISTS bahai_readings (
--     id SERIAL PRIMARY KEY,
--     date DATE NOT NULL,
--     period VARCHAR(10) NOT NULL, -- 'matin' ou 'soir'
--     content TEXT NOT NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- Activer RLS (Row Level Security) sur les tables sensibles
-- ALTER TABLE bahai_readings ENABLE ROW LEVEL SECURITY;

-- Créer une politique pour permettre l'accès public en lecture
-- CREATE POLICY "Allow public read access" ON bahai_readings
--     FOR SELECT USING (true);

-- Politique pour permettre l'insertion depuis l'API
-- CREATE POLICY "Allow API insert" ON bahai_readings
--     FOR INSERT WITH CHECK (true);
