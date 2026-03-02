
DROP TABLE IF EXISTS image CASCADE;
DROP TABLE IF EXISTS examination CASCADE;
DROP TABLE IF EXISTS patient CASCADE;
DROP TABLE IF EXISTS failrue CASCADE;

DROP TYPE IF EXISTS school CASCADE;
DROP TYPE IF EXISTS school_details CASCADE;
DROP TYPE IF EXISTS hand CASCADE;
DROP TYPE IF EXISTS gender CASCADE;

CREATE TYPE school AS ENUM (
    'PODSTAWOWE', 
    'SREDNIE', 
    'WYZSZE'
);

CREATE TYPE school_details AS ENUM (
    'KLASA1', 'KLASA2', 'KLASA3', 'KLASA4', 'KLASA5', 'KLASA6', 'KLASA7', 'KLASA8',
    'TECHNIKUM', 'LICEUM', 'LICENCJAT', 'MAGISTER', 'DOKTORAT', 'EDUKACJA_ZAKONCZONE'
);

CREATE TYPE hand AS ENUM (
    'PRAWA', 
    'LEWA'
);

CREATE TYPE gender AS ENUM (
    'MEZCZYZNA', 
    'KOBIETA'
);

-- 0. Tabela migracji (migration) - Śledzi czy skrypt został wykonany.
CREATE TABLE IF NOT EXISTS migration (
    id SERIAL PRIMARY KEY,
    finished BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS patient (
    id SERIAL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    date_of_birth DATE,
    gender gender,
    dominant_hand hand
);

-- 2. Tabela badań (examination)
CREATE TABLE IF NOT EXISTS examination (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patient(id) ON DELETE CASCADE,
    date DATE,
    whole_time INTERVAL,
    avg_time INTERVAL,
    age_years INTEGER,
    age_months INTEGER,
    age_days INTEGER,
    visual_impairment BOOLEAN,
    impairment_description TEXT,
    education school,
    education_details school_details,
    comments TEXT,
    examination_reason TEXT,
    total_duration_s DECIMAL(10, 4),
    test_start_ts DECIMAL(10, 4),
    test_end_ts TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_examination_patient_id ON examination(patient_id);

CREATE TABLE IF NOT EXISTS image (
    id SERIAL PRIMARY KEY,
    examine_id INTEGER NOT NULL REFERENCES examination(id) ON DELETE CASCADE,
    content BYTEA,
    started_at_ts TIMESTAMP,
    first_stroke_at_ts TIMESTAMP,
    finished_at_ts TIMESTAMP,
    interruptions_count INTEGER,
    interruptions_durations DECIMAL(10, 4)[], 
    undo_count INTEGER,
    redo_count INTEGER,
    overdrawing_score DECIMAL(10, 4),
    revisit_count INTEGER,
    shading_detected BOOLEAN,
    direction_changes_count INTEGER,
    direction_reversal_count INTEGER,
    rapid_velocity_changes_count INTEGER,
    efficency_ratio DECIMAL(10, 4),
    max_local_density DECIMAL(10, 4),
    max_local_density_coords INTEGER[], 
    avg_velocity DECIMAL(10, 4),
    max_velocity DECIMAL(10, 4),
    velocity_ratio DECIMAL(10, 4),
    velocities DECIMAL(10, 4)[], 
    velocity_profile_filename TEXT,
    overlay_filename TEXT,
    heatmap_filename TEXT,
    duration_s DECIMAL(10, 4),
    actual_drawing_duration_s DECIMAL(10, 4),
    avg_interruption_duration_s DECIMAL(10, 4)
);

CREATE INDEX IF NOT EXISTS idx_image_examine_id ON image(examine_id);

CREATE TABLE IF NOT EXISTS failure (
    id SERIAL PRIMARY KEY,
    image_id INTEGER NOT NULL REFERENCES image(id) ON DELETE CASCADE,
    pominiecia INTEGER,
    znieksztalcenia INTEGER,
    perserwacje INTEGER,
    rotacje INTEGER,
    przemieszczenia INTEGER,
    bledy_wzglednej_wielkosci INTEGER
);

CREATE INDEX IF NOT EXISTS idx_failure_image_id ON failure(image_id);

-- Oznaczamy zakończenie migracji
INSERT INTO migration (id, finished) 
VALUES (1, TRUE) 
ON CONFLICT (id) DO UPDATE SET finished = TRUE;
