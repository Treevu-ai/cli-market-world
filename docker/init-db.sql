-- Inicializar base de datos para almacenar histórico de precios
-- Se ejecuta automáticamente en docker-compose.complete.yml

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    unit VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prices (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    retailer VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(5, 2),
    country VARCHAR(2) DEFAULT 'PE',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    max_price DECIMAL(10, 2),
    alert_type VARCHAR(50) DEFAULT 'email',
    recipients TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    triggered_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS shopping_orders (
    id SERIAL PRIMARY KEY,
    hotel_name VARCHAR(255),
    total_cost DECIMAL(12, 2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES shopping_orders(id),
    product_name VARCHAR(255),
    quantity DECIMAL(10, 2),
    unit_price DECIMAL(10, 2),
    total DECIMAL(12, 2)
);

-- Índices para optimizar búsquedas
CREATE INDEX idx_prices_product ON prices(product_id);
CREATE INDEX idx_prices_retailer ON prices(retailer);
CREATE INDEX idx_prices_recorded ON prices(recorded_at DESC);
CREATE INDEX idx_alerts_product ON alerts(product_id);
CREATE INDEX idx_alerts_active ON alerts(is_active);
CREATE INDEX idx_orders_status ON shopping_orders(status);

-- Vistas útiles
CREATE VIEW latest_prices AS
SELECT 
    p.name,
    pr.retailer,
    pr.price,
    pr.discount,
    pr.country,
    pr.recorded_at,
    ROW_NUMBER() OVER (PARTITION BY p.id, pr.retailer ORDER BY pr.recorded_at DESC) as price_rank
FROM products p
JOIN prices pr ON p.id = pr.product_id;

CREATE VIEW price_trends AS
SELECT 
    p.name,
    AVG(pr.price) as avg_price,
    MIN(pr.price) as min_price,
    MAX(pr.price) as max_price,
    COUNT(*) as price_samples,
    DATE(pr.recorded_at) as date
FROM products p
JOIN prices pr ON p.id = pr.product_id
GROUP BY p.id, p.name, DATE(pr.recorded_at);
