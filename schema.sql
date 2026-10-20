-- Run once on a NEW project database. No DROP, DELETE or TRUNCATE.
CREATE DATABASE IF NOT EXISTS warehouse_mgmt CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE warehouse_mgmt;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(40) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    unit VARCHAR(30) NOT NULL,
    unit_cost DECIMAL(12,2) NOT NULL DEFAULT 0,
    min_stock INT NOT NULL DEFAULT 0,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (unit_cost >= 0), CHECK (min_stock >= 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    phone VARCHAR(30) NOT NULL DEFAULT ''
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS stock_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    supplier_id INT NULL,
    movement_type ENUM('IN','OUT','ADJUST_IN','ADJUST_OUT') NOT NULL,
    quantity INT NOT NULL,
    note VARCHAR(500) NOT NULL DEFAULT '',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE RESTRICT,
    CHECK (quantity > 0),
    CHECK ((movement_type = 'IN' AND supplier_id IS NOT NULL)
        OR (movement_type <> 'IN' AND supplier_id IS NULL)),
    CHECK (movement_type NOT IN ('ADJUST_IN','ADJUST_OUT') OR CHAR_LENGTH(TRIM(note)) > 0),
    INDEX idx_product_date (product_id, created_at),
    INDEX idx_movement_date (created_at)
) ENGINE=InnoDB;
