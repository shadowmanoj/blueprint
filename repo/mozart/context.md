#  Service Name: Mozart
## Overview
Mozart is Razorpay's Enterprise Integration Platform, also known as Gateway Integration Framework. It manages all of Razorpay's third-party integrations, particularly payment gateways and financial services.
## Dependencies
- PostgreSQL - Database for audit logs and storage
- Redis - Cache for improved performance
- Vault - For secure storage and handling of credentials
- Lumberjack - Logging service
- Terminal Service - Provides merchant terminal credentials
##  Downstream Services
- Various Payment Gateways - Integration with multiple payment processors (Cybersource, PayU, Billdesk, etc.)
- Banking Services - Integration with banks (ICICI, HDFC, Yes Bank, etc.)
- Wallet Services - Integration with digital wallets (PhonePe, PayPal, etc.)
- UPI Services - Integration with UPI providers
## Upstream Services
- API Service - Makes requests to Mozart for payment processing
- Barricade - Security service that interacts with Mozart
- Payouts Service - Uses Mozart for processing payouts
- Scrooge Service - Financial service that relies on Mozart
- FTS (Fund Transfer Service) - Uses Mozart for financial transactions
- KYC Service - Integrates with Mozart for KYC verification workflows
- Settlements Service - Uses Mozart for settlement processing
## Main Flows / Workflows
1. Payment Gateway Integration
   - Triggered by: API Request for payment processing
   - Steps:
     - Receives payment information from upstream services
     - Validates request parameters
     - Maps request to gateway-specific format
     - Sends request to payment gateway
     - Processes gateway response
     - Returns normalized response to caller
   - Outputs: Payment status, gateway reference IDs
2. Authentication Workflows
   - Triggered by: Authentication requests (3DS, etc.)
   - Steps:
     - Handle enrollment status check
     - Process authentication challenge
     - Verify authentication results
   - Outputs: Authentication status, related tokens
3. Refund Workflows
   - Triggered by: Refund requests
   - Steps:
     - Validate refund request
     - Process refund via payment gateway
     - Record refund status
   - Outputs: Refund status and reference IDs
4. Audit Logging
   - Triggered by: All transactions
   - Steps:
     - Record transaction details
     - Store in database
   - Outputs: Audit records
## Data Sources
- PostgreSQL - For audit logging and transaction data
- Redis - Cache for improved performance and temporary storage
## Data Schemas (High-Level)
### Table/Model: Audits
- Fields:
  - id: string - Primary key
  - created_at: timestamp - When the audit was created
  - entity_id: string - ID of the entity being audited
  - entity_type: string - Type of entity being audited
  - action: string - Action performed
  - gateway: string - Gateway used
  - namespace: string - Namespace of the operation
  - request_data: json - Request data
  - response_data: json - Response data
## Security & Auth
- Basic Authentication - For API access
- JWT - For certain API endpoints
- Vault Integration - For secure credential storage and retrieval
- Encrypted communication with payment gateways
- TLS client certificates for bank integrations
## :gear: Configuration
- Environment variables for service configuration
- TOML-based configuration files
- Configuration varies by environment (dev, stage, func, prod)
- Gateway-specific configurations in jsonnet templates
- Application modes: web, worker, or both