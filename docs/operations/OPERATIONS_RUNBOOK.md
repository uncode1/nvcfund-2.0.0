# NVC Banking Platform - Operations Runbook

## Overview

This runbook provides operational procedures for managing the NVC Banking Platform in production. It covers routine maintenance, monitoring, troubleshooting, and emergency response procedures.

## System Architecture Overview

```
Internet → Route 53 → CloudFront → ALB → Auto Scaling Groups → EC2 Instances → RDS PostgreSQL
                                    ↓
                                   WAF → Security Groups → VPC
```

### Key Components
- **Domain**: nvcfund.com (Hostgator → Route 53)
- **Load Balancer**: Application Load Balancer (ALB)
- **Compute**: Auto Scaling Groups with T3.micro instances
- **Database**: RDS PostgreSQL (Multi-AZ)
- **CDN**: CloudFront for static assets
- **Security**: WAF, Security Groups, SSL/TLS

## Daily Operations

### Morning Health Check (9:00 AM EST)
```bash
# Check overall system health
curl -s https://nvcfund.com/health | jq .
curl -s https://api.nvcfund.com/health | jq .

# Verify SSL certificates
openssl s_client -connect nvcfund.com:443 -servername nvcfund.com 2>/dev/null | openssl x509 -noout -dates

# Check Auto Scaling Group health
aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names nvc-banking-primary-asg --query 'AutoScalingGroups[0].Instances[*].[InstanceId,HealthStatus,LifecycleState]' --output table

# Check RDS status
aws rds describe-db-instances --db-instance-identifier nvcfund-db --query 'DBInstances[0].[DBInstanceStatus,MultiAZ,BackupRetentionPeriod]' --output table
```

### End of Day Review (6:00 PM EST)
```bash
# Review CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/ApplicationELB \
    --metric-name RequestCount \
    --dimensions Name=LoadBalancer,Value=app/nvc-banking-alb/1234567890abcdef \
    --start-time $(date -u -d '1 day ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 3600 \
    --statistics Sum

# Check error rates
aws logs filter-log-events \
    --log-group-name /aws/ec2/nvc-banking \
    --start-time $(date -d 'today 00:00:00' +%s)000 \
    --filter-pattern "ERROR"

# Review scaling events
aws autoscaling describe-scaling-activities \
    --auto-scaling-group-name nvc-banking-primary-asg \
    --max-items 10
```

## Monitoring and Alerting

### Key Metrics to Monitor

#### Application Performance
- **Response Time**: < 500ms for 95th percentile
- **Error Rate**: < 1% for 4xx/5xx errors
- **Throughput**: Monitor requests per second
- **Availability**: > 99.9% uptime

#### Infrastructure Health
- **CPU Utilization**: < 80% average
- **Memory Usage**: < 85% average
- **Database Connections**: < 80% of max connections
- **Disk Space**: < 80% utilization

#### Security Metrics
- **WAF Blocked Requests**: Monitor for attacks
- **Failed Login Attempts**: Banking security monitoring
- **SSL Certificate Expiry**: 30-day advance warning

### CloudWatch Alarms Configuration

```bash
# High CPU alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "NVC-Banking-High-CPU" \
    --alarm-description "High CPU utilization on banking instances" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-2:123456789012:nvc-banking-alerts

# Database connection alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "NVC-Banking-DB-Connections" \
    --alarm-description "High database connection count" \
    --metric-name DatabaseConnections \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-2:123456789012:nvc-banking-alerts

# Application error rate alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "NVC-Banking-Error-Rate" \
    --alarm-description "High application error rate" \
    --metric-name HTTPCode_Target_5XX_Count \
    --namespace AWS/ApplicationELB \
    --statistic Sum \
    --period 300 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:us-east-2:123456789012:nvc-banking-alerts
```

## Routine Maintenance

### Weekly Tasks (Sunday 2:00 AM EST)

#### System Updates
```bash
# Update launch template with latest AMI
aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query 'Images[*].[ImageId,CreationDate]' \
    --output table

# Update security groups if needed
aws ec2 describe-security-groups \
    --group-ids sg-web-xxxxxxxx \
    --query 'SecurityGroups[0].IpPermissions'

# Review WAF logs for new threats
aws wafv2 get-sampled-requests \
    --web-acl-arn arn:aws:wafv2:us-east-2:123456789012:regional/webacl/nvc-banking-waf/12345678-1234-1234-1234-123456789012 \
    --rule-metric-name BankingRateLimitMetric \
    --scope REGIONAL \
    --time-window StartTime=$(date -d '1 week ago' +%s),EndTime=$(date +%s) \
    --max-items 100
```

#### Database Maintenance
```bash
# Review RDS performance insights
aws rds describe-db-instances \
    --db-instance-identifier nvcfund-db \
    --query 'DBInstances[0].[PerformanceInsightsEnabled,MonitoringInterval]'

# Check backup status
aws rds describe-db-snapshots \
    --db-instance-identifier nvcfund-db \
    --snapshot-type automated \
    --max-items 7

# Review slow query logs
aws logs filter-log-events \
    --log-group-name /aws/rds/instance/nvcfund-db/postgresql \
    --start-time $(date -d '1 week ago' +%s)000 \
    --filter-pattern "duration"
```

### Monthly Tasks (First Sunday of Month)

#### Security Review
```bash
# Review IAM access
aws iam get-account-summary
aws iam list-users --query 'Users[*].[UserName,CreateDate]' --output table

# Check SSL certificate expiry
aws acm list-certificates \
    --query 'CertificateSummaryList[?DomainName==`nvcfund.com`].[DomainName,Status,NotAfter]' \
    --output table

# Review CloudTrail logs for unusual activity
aws logs filter-log-events \
    --log-group-name CloudTrail/NVCBankingAuditLogs \
    --start-time $(date -d '1 month ago' +%s)000 \
    --filter-pattern "ConsoleLogin"
```

#### Cost Optimization
```bash
# Review EC2 instance utilization
aws cloudwatch get-metric-statistics \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --start-time $(date -d '1 month ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date +%Y-%m-%dT%H:%M:%S) \
    --period 86400 \
    --statistics Average

# Check for unused resources
aws ec2 describe-volumes --filters "Name=status,Values=available" --query 'Volumes[*].[VolumeId,Size,CreateTime]' --output table
aws ec2 describe-snapshots --owner-ids self --query 'Snapshots[?StartTime<=`$(date -d "30 days ago" +%Y-%m-%d)`].[SnapshotId,StartTime,VolumeSize]' --output table
```

## Scaling Operations

### Manual Scaling
```bash
# Scale up during high traffic
aws autoscaling set-desired-capacity \
    --auto-scaling-group-name nvc-banking-primary-asg \
    --desired-capacity 6 \
    --honor-cooldown

# Scale down during low traffic
aws autoscaling set-desired-capacity \
    --auto-scaling-group-name nvc-banking-primary-asg \
    --desired-capacity 2 \
    --honor-cooldown

# Monitor scaling activity
aws autoscaling describe-scaling-activities \
    --auto-scaling-group-name nvc-banking-primary-asg \
    --max-items 5
```

### Scheduled Scaling
```bash
# Business hours scaling (9 AM EST)
aws autoscaling put-scheduled-update-group-action \
    --auto-scaling-group-name nvc-banking-primary-asg \
    --scheduled-action-name business-hours-scale-up \
    --recurrence "0 14 * * 1-5" \
    --desired-capacity 4 \
    --min-size 2 \
    --max-size 10

# After hours scaling (7 PM EST)
aws autoscaling put-scheduled-update-group-action \
    --auto-scaling-group-name nvc-banking-primary-asg \
    --scheduled-action-name after-hours-scale-down \
    --recurrence "0 0 * * 1-5" \
    --desired-capacity 2 \
    --min-size 2 \
    --max-size 10
```

## Deployment Procedures

### Blue-Green Deployment
```bash
# Create new launch template version
aws ec2 create-launch-template-version \
    --launch-template-name nvc-banking-t3-template \
    --source-version 1 \
    --launch-template-data '{"ImageId":"ami-new-version"}'

# Update Auto Scaling Group with new version
aws autoscaling update-auto-scaling-group \
    --auto-scaling-group-name nvc-banking-primary-asg \
    --launch-template LaunchTemplateName=nvc-banking-t3-template,Version='$Latest'

# Trigger instance refresh
aws autoscaling start-instance-refresh \
    --auto-scaling-group-name nvc-banking-primary-asg \
    --preferences '{"InstanceWarmup":300,"MinHealthyPercentage":90}'
```

### Rolling Updates
```bash
# Update one instance at a time
aws autoscaling terminate-instance-in-auto-scaling-group \
    --instance-id i-1234567890abcdef0 \
    --should-decrement-desired-capacity

# Wait for replacement and verify health
aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names nvc-banking-primary-asg \
    --query 'AutoScalingGroups[0].Instances[*].[InstanceId,HealthStatus,LifecycleState]' \
    --output table
```

## Backup and Recovery

### Database Backups
```bash
# Create manual snapshot
aws rds create-db-snapshot \
    --db-instance-identifier nvcfund-db \
    --db-snapshot-identifier nvc-banking-manual-$(date +%Y%m%d-%H%M%S)

# List available snapshots
aws rds describe-db-snapshots \
    --db-instance-identifier nvcfund-db \
    --query 'DBSnapshots[*].[DBSnapshotIdentifier,SnapshotCreateTime,Status]' \
    --output table

# Restore from snapshot (emergency procedure)
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier nvcfund-db-restored \
    --db-snapshot-identifier nvc-banking-manual-20250106-120000
```

### Application Backups
```bash
# Backup configuration files
aws s3 cp /etc/nginx/nginx.conf s3://nvc-banking-backups/config/nginx.conf
aws s3 cp /etc/systemd/system/nvc-banking.service s3://nvc-banking-backups/config/

# Backup logs
aws s3 sync /var/log/nvc-banking/ s3://nvc-banking-backups/logs/$(date +%Y%m%d)/
```

## Security Procedures

### Password Policy Enforcement
The system enforces banking-grade password complexity:
- Minimum 12 characters
- At least 2 uppercase, 2 lowercase, 2 numbers, 2 special characters
- Blocks common patterns (admin, password, banking, etc.)
- No more than 2 repeated characters
- No 3+ consecutive characters
- Minimum 8 unique characters

### Security Monitoring
```bash
# Monitor failed login attempts
aws logs filter-log-events \
    --log-group-name /aws/ec2/nvc-banking \
    --start-time $(date -d 'today 00:00:00' +%s)000 \
    --filter-pattern "authentication failed"

# Check WAF blocked requests
aws wafv2 get-sampled-requests \
    --web-acl-arn arn:aws:wafv2:us-east-2:123456789012:regional/webacl/nvc-banking-waf/12345678-1234-1234-1234-123456789012 \
    --rule-metric-name BankingRateLimitMetric \
    --scope REGIONAL \
    --time-window StartTime=$(date -d '1 day ago' +%s),EndTime=$(date +%s) \
    --max-items 100

# Review CloudTrail for admin actions
aws logs filter-log-events \
    --log-group-name CloudTrail/NVCBankingAuditLogs \
    --start-time $(date -d '1 day ago' +%s)000 \
    --filter-pattern "{ $.eventName = CreateUser || $.eventName = DeleteUser || $.eventName = AttachUserPolicy }"
```

## Performance Optimization

### Database Performance
```bash
# Monitor database performance
aws rds describe-db-instances \
    --db-instance-identifier nvcfund-db \
    --query 'DBInstances[0].[DBInstanceStatus,AllocatedStorage,DBInstanceClass,MultiAZ]'

# Check connection pool usage
aws cloudwatch get-metric-statistics \
    --namespace AWS/RDS \
    --metric-name DatabaseConnections \
    --dimensions Name=DBInstanceIdentifier,Value=nvcfund-db \
    --start-time $(date -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Average,Maximum
```

### Application Performance
```bash
# Monitor response times
aws cloudwatch get-metric-statistics \
    --namespace AWS/ApplicationELB \
    --metric-name TargetResponseTime \
    --dimensions Name=LoadBalancer,Value=app/nvc-banking-alb/1234567890abcdef \
    --start-time $(date -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Average,Maximum

# Check memory usage
aws cloudwatch get-metric-statistics \
    --namespace CWAgent \
    --metric-name mem_used_percent \
    --dimensions Name=AutoScalingGroupName,Value=nvc-banking-primary-asg \
    --start-time $(date -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Average,Maximum
```

## Troubleshooting Guide

### Common Issues

#### High CPU Usage
1. Check if scaling policies are working
2. Identify resource-intensive processes
3. Review application logs for errors
4. Consider vertical scaling if needed

#### Database Connection Issues
1. Check security groups
2. Verify database instance status
3. Review connection pool settings
4. Check for long-running queries

#### SSL Certificate Issues
1. Verify certificate validity
2. Check Route 53 DNS records
3. Validate certificate chain
4. Review ALB listener configuration

#### Load Balancer Issues
1. Check target group health
2. Review security groups
3. Verify health check endpoints
4. Check WAF rules for blocking

### Log Analysis
```bash
# Application logs
aws logs filter-log-events \
    --log-group-name /aws/ec2/nvc-banking \
    --start-time $(date -d '1 hour ago' +%s)000 \
    --filter-pattern "ERROR"

# Access logs
aws logs filter-log-events \
    --log-group-name /aws/applicationelb/nvc-banking-alb \
    --start-time $(date -d '1 hour ago' +%s)000 \
    --filter-pattern "[..., status_code=5*]"

# Database logs
aws logs filter-log-events \
    --log-group-name /aws/rds/instance/nvcfund-db/postgresql \
    --start-time $(date -d '1 hour ago' +%s)000 \
    --filter-pattern "ERROR"
```

## Contact Information

### On-Call Escalation
1. **Primary**: Development Team Lead
2. **Secondary**: Infrastructure Team Lead
3. **Escalation**: CTO/Technical Director

### Service Contacts
- **AWS Support**: Enterprise Support Plan
- **Domain Support**: Hostgator Support
- **Application Support**: Internal Development Team

### Emergency Contacts
- **Security Incident**: CISO
- **Data Breach**: Legal & Compliance Team
- **Business Continuity**: Operations Manager

## Documentation References

- [Developer Guide](./DEVELOPER_GUIDE.md)
- [AWS Deployment Guide](./AWS_DEPLOYMENT_GUIDE.md)
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)
- [Incident Response Procedures](./INCIDENT_RESPONSE.md)

---

**Last Updated**: July 6, 2025
**Version**: 1.0
**Review Schedule**: Monthly