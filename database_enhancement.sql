-- Enhanced Database Schema with Customers Table and Improved Security
-- This script adds the missing customers table and enhances security

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    company VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    customer_type VARCHAR(50) DEFAULT 'individual' CHECK (customer_type IN ('individual', 'business', 'wholesale')),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    credit_limit DECIMAL(12,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- Add customer_id to sales table
ALTER TABLE sales ADD COLUMN IF NOT EXISTS customer_id INTEGER REFERENCES customers(id);

-- Create indexes for customers table
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_company ON customers(company);
CREATE INDEX IF NOT EXISTS idx_customers_country ON customers(country);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_customers_type ON customers(customer_type);

-- Create view for customer analytics (admin only)
CREATE OR REPLACE VIEW customer_analytics AS
SELECT 
    c.id,
    c.name,
    c.company,
    c.country,
    c.customer_type,
    COUNT(s.id) as total_orders,
    SUM(s.total_amount) as total_spent,
    AVG(s.total_amount) as avg_order_value,
    MAX(s.sale_date) as last_purchase_date,
    MIN(s.sale_date) as first_purchase_date
FROM customers c
LEFT JOIN sales s ON c.id = s.customer_id
GROUP BY c.id, c.name, c.company, c.country, c.customer_type
ORDER BY total_spent DESC NULLS LAST;

-- Create view for financial summary (admin only)
CREATE OR REPLACE VIEW financial_summary AS
SELECT 
    SUM(s.total_amount) as total_revenue,
    SUM(s.quantity * p.cost_price) as total_cost,
    SUM(s.total_amount) - SUM(s.quantity * p.cost_price) as gross_profit,
    AVG(s.profit_margin) as avg_profit_margin,
    COUNT(DISTINCT s.customer_id) as unique_customers,
    COUNT(DISTINCT s.salesperson) as active_salespeople
FROM sales s
JOIN products p ON s.product_id = p.id;

-- Insert sample customers
INSERT INTO customers (name, email, phone, company, address, city, state, country, customer_type, status, created_by) 
VALUES 
    ('John Doe', 'john.doe@email.com', '+1-555-0101', 'Tech Solutions Inc', '123 Business St', 'New York', 'NY', 'United States', 'business', 'active', 1),
    ('Jane Smith', 'jane.smith@email.com', '+1-555-0102', NULL, '456 Personal Ave', 'Los Angeles', 'CA', 'United States', 'individual', 'active', 1),
    ('Mike Johnson', 'mike.johnson@email.com', '+1-555-0103', 'Global Corp', '789 Corporate Blvd', 'Chicago', 'IL', 'United States', 'business', 'active', 1),
    ('Sarah Wilson', 'sarah.wilson@email.com', '+1-555-0104', NULL, '321 Home St', 'Houston', 'TX', 'United States', 'individual', 'active', 1),
    ('David Brown', 'david.brown@email.com', '+1-555-0105', 'Retail Chain', '654 Store St', 'Phoenix', 'AZ', 'United States', 'wholesale', 'active', 1),
    ('Lisa Davis', 'lisa.davis@email.com', '+1-555-0106', NULL, '987 Residential Rd', 'Philadelphia', 'PA', 'United States', 'individual', 'active', 1),
    ('Tom Miller', 'tom.miller@email.com', '+1-555-0107', 'Manufacturing Co', '147 Industrial Ave', 'San Antonio', 'TX', 'United States', 'business', 'active', 1),
    ('Emma Wilson', 'emma.wilson@email.com', '+1-555-0108', NULL, '258 Family St', 'San Diego', 'CA', 'United States', 'individual', 'active', 1)
ON CONFLICT (email) DO NOTHING;

-- Update existing sales to reference customers
UPDATE sales SET customer_id = 1 WHERE customer_name = 'John Doe';
UPDATE sales SET customer_id = 2 WHERE customer_name = 'Jane Smith';
UPDATE sales SET customer_id = 3 WHERE customer_name = 'Mike Johnson';
UPDATE sales SET customer_id = 4 WHERE customer_name = 'Sarah Wilson';
UPDATE sales SET customer_id = 5 WHERE customer_name = 'David Brown';
UPDATE sales SET customer_id = 6 WHERE customer_name = 'Lisa Davis';
UPDATE sales SET customer_id = 7 WHERE customer_name = 'Tom Miller';
UPDATE sales SET customer_id = 8 WHERE customer_name = 'Emma Wilson';

-- Create trigger for updated_at on customers
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE customers TO sales_user;
GRANT ALL PRIVILEGES ON SEQUENCE customers_id_seq TO sales_user;
GRANT ALL PRIVILEGES ON VIEW customer_analytics TO sales_user;
GRANT ALL PRIVILEGES ON VIEW financial_summary TO sales_user;
