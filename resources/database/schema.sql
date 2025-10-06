-- Schema für Kapazitäts- & Auslastungsplaner
-- SQLite via Qt SQL

-- Tabelle: Workers (Knowledge Worker Profile)
CREATE TABLE IF NOT EXISTS workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,          -- Verschlüsselt gespeichert
    email TEXT NOT NULL UNIQUE,  -- Verschlüsselt gespeichert
    team TEXT NOT NULL,
    active INTEGER DEFAULT 1,    -- Boolean: 1=aktiv, 0=inaktiv
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabelle: Time Entries (Arbeitszeiterfassung)
CREATE TABLE IF NOT EXISTS time_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    date DATE NOT NULL,
    duration_minutes INTEGER NOT NULL,
    description TEXT NOT NULL,
    project TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE
);

-- Tabelle: Capacities (Geplante Kapazitäten)
CREATE TABLE IF NOT EXISTS capacities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    planned_hours REAL NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_time_entries_worker 
ON time_entries(worker_id, date);

CREATE INDEX IF NOT EXISTS idx_time_entries_date 
ON time_entries(date);

CREATE INDEX IF NOT EXISTS idx_capacities_worker 
ON capacities(worker_id, start_date, end_date);

-- Schema-Version für Migrations
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO schema_version (version) VALUES (1);
