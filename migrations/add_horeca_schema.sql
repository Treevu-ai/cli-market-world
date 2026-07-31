-- Migration para agregar funcionalidad HORECA
-- Ejecutar: sqlite3 cli_market.db < migrations/add_horeca_schema.sql

-- Tabla de perfiles HORECA
CREATE TABLE IF NOT EXISTS horeca_profiles (
    whatsapp_number TEXT PRIMARY KEY,
    business_name TEXT NOT NULL,
    business_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_search_category TEXT,
    search_count INTEGER DEFAULT 0,
    total_savings REAL DEFAULT 0.0,
    currency TEXT DEFAULT 'PEN'
);

-- Tabla de búsquedas recurrentes (templates)
CREATE TABLE IF NOT EXISTS horeca_search_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    whatsapp_number TEXT NOT NULL,
    template_name TEXT NOT NULL,
    search_query TEXT NOT NULL,
    category TEXT NOT NULL,
    frequency TEXT DEFAULT 'weekly',
    last_used TIMESTAMP,
    savings_accumulated REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (whatsapp_number) REFERENCES horeca_profiles(whatsapp_number)
);

-- Tabla de tracking de búsquedas con cooldowns
CREATE TABLE IF NOT EXISTS horeca_search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    whatsapp_number TEXT NOT NULL,
    search_query TEXT NOT NULL,
    category TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result_count INTEGER,
    best_price REAL,
    avg_price REAL,
    savings REAL,
    FOREIGN KEY (whatsapp_number) REFERENCES horeca_profiles(whatsapp_number)
);

-- Tabla de alertas de precio
CREATE TABLE IF NOT EXISTS horeca_price_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    whatsapp_number TEXT NOT NULL,
    product_name TEXT NOT NULL,
    target_price REAL,
    current_price REAL,
    alert_threshold REAL DEFAULT 0.10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    triggered_at TIMESTAMP,
    FOREIGN KEY (whatsapp_number) REFERENCES horeca_profiles(whatsapp_number)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_horeca_history_timestamp 
    ON horeca_search_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_horeca_history_number 
    ON horeca_search_history(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_horeca_history_query 
    ON horeca_search_history(whatsapp_number, search_query, timestamp);
CREATE INDEX IF NOT EXISTS idx_horeca_templates_number 
    ON horeca_search_templates(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_horeca_alerts_number 
    ON horeca_price_alerts(whatsapp_number, is_active);