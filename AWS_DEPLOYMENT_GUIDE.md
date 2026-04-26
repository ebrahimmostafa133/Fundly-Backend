# AWS Elastic Beanstalk Deployment Guide

This guide covers deploying your Fundly backend on **AWS Elastic Beanstalk** with:
- **S3** for image storage (already configured ✓)
- **RDS** for PostgreSQL database (being created ✓)
- **SES** for email sending (ready to configure)
- **Elastic Beanstalk** for application hosting (this guide)

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

## 3. Deploy to Elastic Beanstalk

### Prerequisites
```bash
pip install awsebcli
```

### Initialize Beanstalk
```bash
eb init -p python-3.12 fundly-backend --region us-east-1
```

Follow the prompts:
- Choose region: `us-east-1`
- Create new application key pair? **y** (or use existing)

### Create Environment
Wait for RDS to be ready, then create the Beanstalk environment:

```bash
eb create fundly-production \
  --scale 1 \
  --instance-type t3.micro \
  --envvars USE_RDS=True,RDS_DB_HOST=fundly-db.xxxxx.us-east-1.rds.amazonaws.com,RDS_DB_NAME=postgres,RDS_DB_USER=fundly_admin,RDS_DB_PASSWORD=Benzema_09,USE_AWS=True,AWS_STORAGE_BUCKET_NAME=demo-cloudfont-benzema-v5,AWS_S3_REGION_NAME=us-east-1,AWS_S3_CUSTOM_DOMAIN=d2qwfrld1oq4tr.cloudfront.net,USE_SES=True,DEFAULT_FROM_EMAIL=noreply@fundly.com,DEBUG=False
```

### Deploy
```bash
eb deploy
```

### Monitor Deployment
```bash
eb status
eb logs --stream
```

### Access Your Application
```bash
eb open
```

---

## 4. Elastic Beanstalk CLI Commands

```bash
# Check status
eb status

# View logs (live stream)
eb logs --stream

# SSH into instance
eb ssh

# Open application in browser
eb open

# Update environment variables
eb setenv USE_SES=True DEFAULT_FROM_EMAIL=noreply@fundly.com

# Deploy new version
eb deploy

# Terminate environment
eb terminate fundly-production
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
