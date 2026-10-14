-- Local-dev-only seed: a handful of basic canasta items so the moat_health
-- watchdog ("moat_empty") doesn't fire against the empty local Postgres
-- container from run_local.py. Not production data — plausible test rows.
INSERT INTO price_snapshots
    (product_id, name, brand, price, list_price, discount, store, store_name,
     currency, line, line_name, category, stock, url, queried_at, confidence)
VALUES
    ('local-seed-arroz-costeno-5kg', 'Arroz Costeño Extra 5kg', 'Costeño', 24.90, 24.90, 0, 'plazavea', 'Plaza Vea', 'PEN', 'supermercados', 'Supermercados', 'arroz', 50, 'https://www.plazavea.com.pe/local-seed-arroz', now(), 'ok'),
    ('local-seed-pollo-entero-kg', 'Pollo Entero x Kg', 'San Fernando', 13.50, 13.50, 0, 'wong', 'Wong', 'PEN', 'supermercados', 'Supermercados', 'pollo', 30, 'https://www.wong.pe/local-seed-pollo', now(), 'ok'),
    ('local-seed-huevos-30', 'Huevos Rojos x 30 unidades', 'San Fernando', 18.90, 18.90, 0, 'metro', 'Metro', 'PEN', 'supermercados', 'Supermercados', 'huevos', 40, 'https://www.metro.pe/local-seed-huevos', now(), 'ok'),
    ('local-seed-leche-gloria-400g', 'Leche Evaporada Gloria 400g', 'Gloria', 4.20, 4.50, 7, 'plazavea', 'Plaza Vea', 'PEN', 'supermercados', 'Supermercados', 'leche', 100, 'https://www.plazavea.com.pe/local-seed-leche', now(), 'ok'),
    ('local-seed-aceite-primor-1l', 'Aceite Vegetal Primor 1L', 'Primor', 12.90, 14.50, 11, 'wong', 'Wong', 'PEN', 'supermercados', 'Supermercados', 'aceite', 60, 'https://www.wong.pe/local-seed-aceite', now(), 'ok'),
    ('local-seed-pan-bimbo-integral', 'Pan Integral Bimbo 500g', 'Bimbo', 7.80, 7.80, 0, 'metro', 'Metro', 'PEN', 'supermercados', 'Supermercados', 'pan', 25, 'https://www.metro.pe/local-seed-pan', now(), 'ok'),
    ('local-seed-papa-kg', 'Papa Blanca x Kg', NULL, 2.50, 2.50, 0, 'plazavea', 'Plaza Vea', 'PEN', 'supermercados', 'Supermercados', 'papa', 200, 'https://www.plazavea.com.pe/local-seed-papa', now(), 'ok'),
    ('local-seed-cebolla-kg', 'Cebolla Roja x Kg', NULL, 2.80, 2.80, 0, 'wong', 'Wong', 'PEN', 'supermercados', 'Supermercados', 'cebolla', 150, 'https://www.wong.pe/local-seed-cebolla', now(), 'ok')
ON CONFLICT (product_id, store) DO UPDATE SET
    price = EXCLUDED.price,
    queried_at = EXCLUDED.queried_at;
