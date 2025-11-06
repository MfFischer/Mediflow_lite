# Production Deployment Guide

This guide covers deploying MediFlow Lite to production environments.

## 🎯 Pre-Deployment Checklist

### Security
- [ ] Change all default passwords
- [ ] Generate new `SECRET_KEY` (use `openssl rand -hex 32`)
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Review CORS settings
- [ ] Set up backup encryption keys
- [ ] Configure secure database passwords

### Environment
- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Set `DEBUG=false`
- [ ] Configure production database URL
- [ ] Set up SendGrid API key for emails
- [ ] Configure Gemini API key for AI features
- [ ] Set proper CORS origins

### Infrastructure
- [ ] Set up PostgreSQL database
- [ ] Configure backup strategy
- [ ] Set up monitoring (Sentry, Datadog, etc.)
- [ ] Configure logging aggregation
- [ ] Set up CDN for static assets
- [ ] Plan for horizontal scaling

---

## 🚀 Deployment Options

### Option 1: Docker Compose (Simple VPS)

**Best for:** Small clinics, single-server deployments

1. **Prepare the server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y
```

2. **Clone and configure**
```bash
git clone <your-repo-url>
cd mediflow

# Set up production environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit .env files with production values
nano backend/.env
nano frontend/.env
```

3. **Create production docker-compose**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: mediflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - mediflow-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    env_file:
      - ./backend/.env
    depends_on:
      - postgres
    networks:
      - mediflow-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    environment:
      - NODE_ENV=production
    env_file:
      - ./frontend/.env
    depends_on:
      - backend
    networks:
      - mediflow-network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - mediflow-network

volumes:
  postgres_data:

networks:
  mediflow-network:
    driver: bridge
```

4. **Set up Nginx reverse proxy**
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

5. **Deploy**
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

---

### Option 2: Cloud Platform (AWS/GCP/Azure)

**Best for:** Multi-location clinics, scalable deployments

#### AWS Deployment

1. **Set up RDS PostgreSQL**
   - Create RDS instance
   - Configure security groups
   - Note connection string

2. **Deploy Backend (ECS/Fargate)**
   - Build and push Docker image to ECR
   - Create ECS task definition
   - Configure environment variables
   - Set up Application Load Balancer

3. **Deploy Frontend (Vercel/Netlify)**
   - Connect GitHub repository
   - Configure build settings
   - Set environment variables
   - Deploy

4. **Set up CloudFront CDN**
   - Create distribution
   - Configure SSL certificate
   - Set up custom domain

---

### Option 3: Kubernetes (Enterprise)

**Best for:** Large hospitals, multi-tenant deployments

See `k8s/` directory for Kubernetes manifests (to be created).

---

## 🔒 Security Hardening

### 1. SSL/TLS Configuration

**Get free SSL certificate with Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 2. Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 3. Database Security

```sql
-- Create read-only user for reporting
CREATE USER mediflow_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE mediflow TO mediflow_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mediflow_readonly;
```

### 4. Backup Strategy

**Automated daily backups:**
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup database
docker-compose exec -T postgres pg_dump -U mediflow mediflow > $BACKUP_DIR/db_$DATE.sql

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz backend/uploads/

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

**Add to crontab:**
```bash
0 2 * * * /path/to/backup.sh
```

---

## 📊 Monitoring & Logging

### 1. Set up Sentry for Error Tracking

```python
# backend/app/main.py
import sentry_sdk

if settings.is_production:
    sentry_sdk.init(
        dsn="your-sentry-dsn",
        environment=settings.environment,
    )
```

### 2. Configure Logging

```python
# backend/app/core/config.py
LOGGING_CONFIG = {
    "version": 1,
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/mediflow.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file"]
    }
}
```

### 3. Health Check Monitoring

Set up uptime monitoring with:
- UptimeRobot
- Pingdom
- StatusCake

Monitor: `https://yourdomain.com/health`

---

## 🔄 CI/CD Pipeline

### GitHub Actions (Already configured)

The `.github/workflows/ci.yml` file runs:
- Tests on every push
- Security scans
- Docker builds

### Add Deployment Step

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /path/to/mediflow
            git pull
            docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 📈 Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_patients_email ON patients(email);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_audit_timestamp ON audit_events(timestamp);
```

### 2. Caching

Consider adding Redis for:
- Session storage
- API response caching
- Rate limiting

### 3. CDN Configuration

Use CloudFront/CloudFlare for:
- Static assets
- Frontend distribution
- DDoS protection

---

## 🆘 Troubleshooting

### Check logs
```bash
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Database connection issues
```bash
docker-compose exec postgres psql -U mediflow -d mediflow
```

### Restart services
```bash
docker-compose restart backend
docker-compose restart frontend
```

---

## 📞 Post-Deployment

1. **Test all critical flows**
   - User login
   - Patient creation
   - Data export (GDPR)

2. **Set up monitoring alerts**
   - Server down
   - High error rate
   - Database issues

3. **Document for your team**
   - Access credentials
   - Backup procedures
   - Emergency contacts

---

**Your production deployment is ready! 🎉**

