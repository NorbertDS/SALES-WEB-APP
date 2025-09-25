-- Sales Analytics Database Initialization Script
-- This script creates the necessary tables and initial data for the sales analytics system

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'analyst', 'viewer')),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    permissions TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    description TEXT,
    profit_margin DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN unit_price > 0 THEN ROUND(((unit_price - cost_price) / unit_price) * 100, 2)
            ELSE 0
        END
    ) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create sales table
CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    sale_date DATE NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    region VARCHAR(100) NOT NULL,
    salesperson VARCHAR(255) NOT NULL,
    profit_margin DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_region ON sales(region);
CREATE INDEX IF NOT EXISTS idx_sales_salesperson ON sales(salesperson);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Insert default admin user
INSERT INTO users (email, name, role, hashed_password, is_active, permissions) 
VALUES (
    'admin@example.com',
    'Admin User',
    'admin',
    'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', -- admin123
    TRUE,
    ARRAY['read', 'create', 'update', 'delete', 'admin']
) ON CONFLICT (email) DO NOTHING;

-- Insert default analyst user
INSERT INTO users (email, name, role, hashed_password, is_active, permissions) 
VALUES (
    'analyst@example.com',
    'Analyst User',
    'analyst',
    'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', -- analyst123
    TRUE,
    ARRAY['read', 'create', 'update']
) ON CONFLICT (email) DO NOTHING;

-- Insert default viewer user
INSERT INTO users (email, name, role, hashed_password, is_active, permissions) 
VALUES (
    'viewer@example.com',
    'Viewer User',
    'viewer',
    'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', -- viewer123
    TRUE,
    ARRAY['read']
) ON CONFLICT (email) DO NOTHING;

-- Insert sample products
INSERT INTO products (name, category, unit_price, cost_price, stock_quantity, description) 
VALUES 
    ('Laptop Pro 15', 'Electronics', 1200.00, 900.00, 50, 'High-performance laptop for professionals'),
    ('Wireless Mouse', 'Accessories', 80.00, 56.00, 100, 'Ergonomic wireless mouse'),
    ('Mechanical Keyboard', 'Accessories', 150.00, 100.00, 75, 'RGB mechanical keyboard'),
    ('Monitor 27"', 'Electronics', 300.00, 200.00, 30, '4K Ultra HD monitor'),
    ('Gaming Chair', 'Furniture', 250.00, 150.00, 20, 'Ergonomic gaming chair')
ON CONFLICT DO NOTHING;

-- Insert sample sales data
INSERT INTO sales (product_id, quantity, unit_price, sale_date, customer_name, region, salesperson, profit_margin)
VALUES 
    (1, 2, 1200.00, '2024-01-15', 'John Doe', 'North', 'Alice Johnson', 25.00),
    (2, 1, 80.00, '2024-01-16', 'Jane Smith', 'South', 'Bob Wilson', 30.00),
    (1, 3, 1200.00, '2024-01-17', 'Mike Johnson', 'East', 'Alice Johnson', 25.00),
    (3, 1, 150.00, '2024-01-18', 'Sarah Wilson', 'West', 'Bob Wilson', 33.33),
    (4, 1, 300.00, '2024-01-19', 'David Brown', 'North', 'Alice Johnson', 33.33),
    (2, 2, 80.00, '2024-01-20', 'Lisa Davis', 'South', 'Bob Wilson', 30.00),
    (5, 1, 250.00, '2024-01-21', 'Tom Miller', 'East', 'Alice Johnson', 40.00),
    (1, 1, 1200.00, '2024-01-22', 'Emma Wilson', 'West', 'Bob Wilson', 25.00)
ON CONFLICT DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sales_updated_at BEFORE UPDATE ON sales
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create view for sales analytics
CREATE OR REPLACE VIEW sales_analytics AS
SELECT 
    s.id,
    s.sale_date,
    p.name as product_name,
    p.category,
    s.quantity,
    s.unit_price,
    s.total_amount,
    s.customer_name,
    s.region,
    s.salesperson,
    s.profit_margin,
    s.created_at
FROM sales s
JOIN products p ON s.product_id = p.id
ORDER BY s.sale_date DESC;

-- Create view for revenue by region
CREATE OR REPLACE VIEW revenue_by_region AS
SELECT 
    region,
    COUNT(*) as total_sales,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_sale_value,
    COUNT(DISTINCT salesperson) as unique_salespeople
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;

-- Create view for top products
CREATE OR REPLACE VIEW top_products AS
SELECT 
    p.id,
    p.name,
    p.category,
    COUNT(s.id) as total_sales,
    SUM(s.quantity) as total_quantity_sold,
    SUM(s.total_amount) as total_revenue,
    AVG(s.profit_margin) as avg_profit_margin
FROM products p
LEFT JOIN sales s ON p.id = s.product_id
GROUP BY p.id, p.name, p.category
ORDER BY total_revenue DESC NULLS LAST;

-- Grant permissions to sales_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sales_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sales_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO sales_user;
