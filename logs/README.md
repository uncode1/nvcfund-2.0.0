# NVC Banking Platform - Log Directory Structure

## Directory Organization

The logs are organized in a nested year/month/date structure for efficient management and archival:

```
logs/
├── YYYY/           # Year (e.g., 2025)
│   ├── MM/         # Month (e.g., 07)
│   │   ├── DD/     # Date (e.g., 06)
│   │   │   ├── security_reports/     # Security audit reports and assessments
│   │   │   ├── application/          # General application logs
│   │   │   ├── banking/              # Banking operation logs
│   │   │   ├── compliance/           # AML, KYC, and regulatory compliance logs
│   │   │   ├── admin/                # Administrative and management logs
│   │   │   ├── errors/               # Error logs and exception reports
│   │   │   ├── audit/                # Audit trail logs
│   │   │   └── system/               # System health and monitoring logs
```

## Log Categories

- **security_reports/**: Security assessments, vulnerability reports, audit findings
- **application/**: General application runtime logs
- **banking/**: Transaction logs, account operations, payment processing
- **compliance/**: AML screening, KYC verification, regulatory reporting
- **admin/**: User management, administrative operations
- **errors/**: Exception logs, error reports, debugging information
- **audit/**: Audit trail logs, compliance monitoring
- **system/**: System health, performance metrics, monitoring

## Retention Policy

- Current day logs: Active logging location
- Historical logs: Archived by date for compliance and audit purposes
- Security reports: Maintained for regulatory compliance requirements

## Access Control

- Admin users: Full access to all log categories
- Compliance officers: Access to compliance and audit logs
- Security team: Access to security_reports and system logs
- Standard users: No direct log access

Generated: 2025-07-06 03:17:44
