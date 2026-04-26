# AWS Backend Deployment Guide

This guide covers deploying your Fundly backend on AWS using multiple AWS services:
- **S3** for image storage (already configured ✓)
- **RDS** for PostgreSQL database
- **SES** for email sending
- **EC2/ECS** for application hosting

---

## 1. AWS RDS Setup (PostgreSQL Database)

### Create RDS Instance via AWS Console:
1. Go to **RDS Dashboard** → **Create Database**
2. Choose **PostgreSQL** (version 14 or higher)
3. **DB Instance Identifier**: `fundly-db`
4. **Master Username**: `fundly_admin`
5. **Master Password**: Use a strong password
6. **DB Instance Class**: `db.t3.micro` (free tier eligible)
7. **Storage**: 20 GB, enable auto-scaling
8. **Connectivity**: 
   - VPC: Default
   - Public accessibility: Yes (for now)
   - Security group: Allow inbound on port 5432
9. Create database

### Get Connection Details:
After creation, copy the **Endpoint** (e.g., `fundly-db.c9akciq32.us-east-1.rds.amazonaws.com`)

### Update .env:
```env
USE_RDS=True
RDS_DB_NAME=postgres
RDS_DB_USER=fundly_admin
RDS_DB_PASSWORD=your-strong-password
RDS_DB_HOST=fundly-db.c9akciq32.us-east-1.rds.amazonaws.com
RDS_DB_PORT=5432
```

### Run Migrations:
```bash
python manage.py migrate
```

---

## 2. AWS SES Setup (Email Service)

### Verify Email Address:
1. Go to **SES Dashboard** → **Email Addresses**
2. Click **Verify a New Email Address**
3. Enter your email: `noreply@fundly.com` or your domain email
4. Check your email and click the verification link

### Request Production Access (Optional):
- By default, SES is in "Sandbox" mode (limited to verified addresses)
- To send to any email, submit a support ticket requesting production access

### Update .env:
```env
USE_SES=True
AWS_SES_REGION_NAME=us-east-1
DEFAULT_FROM_EMAIL=noreply@fundly.com
```

### Test Email Sending:
```bash
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'This is a test', 'noreply@fundly.com', ['your-email@example.com'])
```

---

## 3. Deployment Options

### Option A: AWS Elastic Beanstalk (Easiest)

**Prerequisites:**
```bash
pip install awsebcli
```

**Initialize EB:**
```bash
eb init -p python-3.12 fundly-backend --region us-east-1
```

**Create Environment:**
```bash
eb create fundly-production --scale 1 --envvars \
  USE_RDS=True,\
  RDS_DB_HOST=fundly-db.c9akciq32.us-east-1.rds.amazonaws.com,\
  RDS_DB_NAME=postgres,\
  RDS_DB_USER=fundly_admin,\
  RDS_DB_PASSWORD=your-password,\
  USE_AWS=True,\
  AWS_STORAGE_BUCKET_NAME=your-bucket,\
  USE_SES=True
```

**Deploy:**
```bash
eb deploy
```

---

### Option B: Docker + ECS

**Build Docker Image:**
```bash
docker build -t fundly-backend:latest .
```

**Push to ECR:**
```bash
# Create ECR repository
aws ecr create-repository --repository-name fundly-backend

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag fundly-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/fundly-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/fundly-backend:latest
```

**Deploy to ECS:**
1. Go to **ECS** → **Create Cluster**
2. Choose **EC2 template** or **Fargate**
3. Create task definition pointing to ECR image
4. Create service with environment variables

---

### Option C: EC2 Manual Deployment

**Launch EC2 Instance:**
1. **AMI**: Ubuntu 22.04 LTS
2. **Instance Type**: `t3.micro` (free tier)
3. **Security Group**: Allow ports 80, 443, 22

**Connect and Setup:**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt update && sudo apt install -y python3.12 python3.12-venv postgresql-client nginx

# Clone repo
git clone https://github.com/ebrahimmostafa133/Fundly-Backend.git
cd Fundly-Backend

# Setup virtual environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env with RDS and SES config
nano .env

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput

# Start gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

**Configure Nginx (Reverse Proxy):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 4. Environment Variables Checklist

```env
# Django
SECRET_KEY=your-secret
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# RDS Database
USE_RDS=True
RDS_DB_HOST=your-rds-endpoint.rds.amazonaws.com
RDS_DB_NAME=postgres
RDS_DB_USER=fundly_admin
RDS_DB_PASSWORD=your-password

# AWS S3
USE_AWS=True
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=your-cloudfront.cloudfront.net

# AWS SES
USE_SES=True
DEFAULT_FROM_EMAIL=noreply@your-domain.com

# Frontend
FRONTEND_URL_DEPLOY=https://your-frontend.com

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

---

## 5. Monitoring & Logging

### CloudWatch Logs:
```bash
# View Elastic Beanstalk logs
eb logs --stream

# Or via AWS CLI
aws logs tail /aws/elasticbeanstalk/fundly-production/var/log/eb-activity.log --follow
```

### Performance Monitoring:
- Enable **CloudWatch** monitoring in RDS dashboard
- Set alarms for CPU, connections, storage

---

## 6. Security Best Practices

✓ Use environment variables for all secrets (done)
✓ Set `DEBUG=False` in production
✓ Use `HTTPS_ONLY=True` for cookies
✓ Restrict RDS security group to only Elastic Beanstalk/EC2 instances
✓ Rotate AWS credentials regularly
✓ Enable MFA on AWS account
✓ Use IAM roles instead of access keys when possible

---

## 7. Cost Estimation (Monthly)

| Service | Tier | Cost |
|---------|------|------|
| RDS | db.t3.micro | ~$10-15 |
| S3 | 100GB storage | ~$2-3 |
| CloudFront | 1TB transfer | ~$0.085/GB |
| EC2/EB | t3.micro | Free (first 12 months) |
| **Total** | | **~$15-25/month** |

---

## Support

For issues:
1. Check CloudWatch logs: `eb logs`
2. Test database connection: `python manage.py dbshell`
3. Verify email: `python manage.py shell` → `send_mail(...)`
4. Check AWS console for service health
