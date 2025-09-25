# 🧹 Project Cleanup Plan

## 📊 **Current Project Analysis:**

### **✅ Files Currently in Use:**
- `enhanced_dashboard.html` - Main frontend (cloud-ready)
- `backend/production_server_cloud.py` - Main backend (cloud-ready)
- `backend/database_enhanced.py` - Enhanced database models
- `docker-compose.cloud.yml` - Cloud deployment configuration
- `frontend/nginx.cloud.conf` - Cloud nginx configuration
- `init.sql` - Database initialization
- `database_enhancement.sql` - Database enhancements
- `deploy_cloud.sh` - Cloud deployment script

### **❌ Files to Remove (Unused/Old Versions):**

#### **Backend Files:**
- `backend/production_server.py` - Old version
- `backend/production_server_v2.py` - Old version  
- `backend/production_server_secure.py` - Superseded by cloud version
- `backend/database.py` - Old version
- `backend/Dockerfile` - Old version

#### **Frontend Files:**
- `enhanced_dashboard_v2.html` - Old version
- `frontend/Dockerfile` - Old version
- `frontend/nginx.conf` - Old version
- `frontend/node_modules/` - React app (not used)
- `frontend/src/` - React components (not used)
- `frontend/package.json` - React dependencies (not used)
- `frontend/package-lock.json` - React dependencies (not used)

#### **Deployment Files:**
- `docker-compose.yml` - Old version
- `deploy.sh` - Old version
- `deploy.bat` - Old version
- `deploy_production.sh` - Old version
- `deploy_production.bat` - Old version
- `start_servers.bat` - Old version

#### **Documentation Files:**
- `CLOUD_READY_ENHANCEMENTS.md` - Planning document
- `database_schema_report.md` - Analysis document

## 🗑️ **Cleanup Commands:**

### **Remove Old Backend Files:**
```bash
rm backend/production_server.py
rm backend/production_server_v2.py
rm backend/production_server_secure.py
rm backend/database.py
rm backend/Dockerfile
```

### **Remove Old Frontend Files:**
```bash
rm enhanced_dashboard_v2.html
rm frontend/Dockerfile
rm frontend/nginx.conf
rm -rf frontend/node_modules/
rm -rf frontend/src/
rm frontend/package.json
rm frontend/package-lock.json
```

### **Remove Old Deployment Files:**
```bash
rm docker-compose.yml
rm deploy.sh
rm deploy.bat
rm deploy_production.sh
rm deploy_production.bat
rm start_servers.bat
```

### **Remove Documentation Files:**
```bash
rm CLOUD_READY_ENHANCEMENTS.md
rm database_schema_report.md
```

## 📈 **Space Savings Estimate:**
- **node_modules/**: ~50-100MB
- **Old backend files**: ~2-5MB
- **Old frontend files**: ~1-2MB
- **Old deployment files**: ~1MB
- **Total estimated savings**: ~55-110MB

## ✅ **Files to Keep:**
- `enhanced_dashboard.html` - Main frontend
- `backend/production_server_cloud.py` - Main backend
- `backend/database_enhanced.py` - Database models
- `docker-compose.cloud.yml` - Cloud deployment
- `frontend/nginx.cloud.conf` - Cloud nginx
- `init.sql` - Database init
- `database_enhancement.sql` - Database enhancements
- `deploy_cloud.sh` - Cloud deployment
- `README.md` - Documentation
- `SECURITY_AND_DATABASE_ENHANCEMENT_REPORT.md` - Security docs
- `CLOUD_DEPLOYMENT_SUMMARY.md` - Deployment docs
