#!/bin/bash

echo "⏳ Waiting for RDS instance 'fundly-db' to be available..."
echo "This typically takes 3-5 minutes..."

while true; do
    STATUS=$(aws rds describe-db-instances \
        --db-instance-identifier fundly-db \
        --region us-east-1 \
        --query 'DBInstances[0].DBInstanceStatus' \
        --output text 2>/dev/null)
    
    if [ "$STATUS" = "available" ]; then
        echo "✅ RDS instance is available!"
        
        # Get endpoint and port
        ENDPOINT=$(aws rds describe-db-instances \
            --db-instance-identifier fundly-db \
            --region us-east-1 \
            --query 'DBInstances[0].Endpoint.Address' \
            --output text)
        
        PORT=$(aws rds describe-db-instances \
            --db-instance-identifier fundly-db \
            --region us-east-1 \
            --query 'DBInstances[0].Endpoint.Port' \
            --output text)
        
        echo "🔗 RDS Endpoint: $ENDPOINT"
        echo "🔌 Port: $PORT"
        
        # Update .env with RDS endpoint
        sed -i "s/RDS_DB_HOST=.*/RDS_DB_HOST=$ENDPOINT/" .env
        sed -i "s/USE_RDS=.*/USE_RDS=True/" .env
        
        echo ""
        echo "✅ Updated .env with RDS configuration"
        echo ""
        echo "Next steps:"
        echo "1. Verify RDS security group allows inbound on port 5432"
        echo "2. Run: python manage.py migrate"
        echo "3. Restart your Django server"
        break
    else
        echo "Current status: $STATUS"
        sleep 15
    fi
done
