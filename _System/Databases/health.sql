-- Health.sqlite: your own health data, kept on this computer, in 05 Databases. Optional: delete the file if you do
-- not track your health here. Read it with ICOR for Life - SQLite Viewer or any SQLite tool; your AI reads it through
-- SQL and never copies it into notes. Made from this file by `python3 _System/Tools/new-database.py health`.

CREATE TABLE about (key TEXT PRIMARY KEY, value TEXT NOT NULL);
INSERT INTO about (key, value) VALUES
  ('what', 'Your health data: measurements, workouts, medication, symptoms and mood. Yours only, never in a note.'),
  ('schema', '1'),
  ('docs', '05 Databases/README.md');

-- One measurement per row, from Apple Health, a scale, a watch or typed by hand. The shape ICOR for Life - Health
-- Tracker reads. metric_name is snake_case: weight_body_mass, body_fat_percentage, lean_body_mass, body_mass_index,
-- height, resting_heart_rate, heart_rate_variability, vo2_max, step_count, active_energy, sleep_hours, blood_pressure_*…
CREATE TABLE health_metric (
  id INTEGER PRIMARY KEY,
  metric_name TEXT NOT NULL,
  qty REAL NOT NULL,
  unit TEXT,                    -- kg, %, count/min, ms, mL/(kg·min), count, kcal, h
  local_date TEXT NOT NULL,     -- YYYY-MM-DD, your own day
  recorded_at_utc TEXT,         -- ISO 8601, when it was measured
  source TEXT                   -- Apple Health, Withings, by hand…
);
CREATE INDEX health_metric_by_name_date ON health_metric (metric_name, local_date);

CREATE TABLE workouts (
  id INTEGER PRIMARY KEY,
  workout_type TEXT NOT NULL,   -- running, cycling, strength, swimming, walking…
  start_time TEXT NOT NULL,     -- ISO 8601
  end_time TEXT,
  duration_min REAL,
  active_energy_kcal REAL,
  distance_km REAL,
  heart_rate_avg INTEGER,
  heart_rate_max INTEGER,
  source TEXT,
  note TEXT
);
CREATE INDEX workouts_by_start ON workouts (start_time);

CREATE TABLE medications (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL,           -- YYYY-MM-DD
  medication TEXT NOT NULL,
  dosage REAL,
  unit TEXT,
  status TEXT                   -- taken, skipped
);

CREATE TABLE symptoms (
  id INTEGER PRIMARY KEY,
  start_time TEXT NOT NULL,
  end_time TEXT,
  symptom TEXT NOT NULL,
  severity TEXT,                -- mild, moderate, severe
  source TEXT,
  note TEXT
);

CREATE TABLE mood_entries (
  id INTEGER PRIMARY KEY,
  timestamp TEXT NOT NULL,
  valence REAL,                 -- -1 (very unpleasant) to 1 (very pleasant)
  labels TEXT,                  -- comma-separated: calm, stressed…
  associations TEXT,            -- comma-separated: work, family…
  note TEXT
);

-- Each measurement per day: average, lowest, highest.
CREATE VIEW daily AS
  SELECT local_date AS date, metric_name, ROUND(AVG(qty), 2) AS avg, MIN(qty) AS min, MAX(qty) AS max, COUNT(*) AS n
  FROM health_metric GROUP BY local_date, metric_name;
