// Railway Backend Configuration
// Replace YOUR-RAILWAY-APP-NAME with your actual Railway app name
const RAILWAY_URL = 'https://data-analytics-master.up.railway.app'; 

// API Configuration
const API_CONFIG = {
    baseUrl: window.location.origin.includes('localhost') 
        ? RAILWAY_URL  // Use Railway URL when running locally
        : window.location.origin,  // Use same origin when deployed
    
    endpoints: {
        health: '/health',
        login: '/api/auth/login',
        sales: '/api/sales',
        products: '/api/products',
        users: '/api/users',
        analytics: '/api/analytics/kpi'
    }
};

// Export for use in main application
window.API_CONFIG = API_CONFIG;

// Debug function to test Railway connection
function testRailwayConnection() {
    console.log('Testing Railway connection...');
    console.log('API Base URL:', API_CONFIG.baseUrl);
    
    // Test health endpoint
    fetch(`${API_CONFIG.baseUrl}/health`)
        .then(response => response.json())
        .then(data => {
            console.log('✅ Railway connection successful:', data);
            return true;
        })
        .catch(error => {
            console.error('❌ Railway connection failed:', error);
            return false;
        });
}

// Make test function available globally
window.testRailwayConnection = testRailwayConnection;