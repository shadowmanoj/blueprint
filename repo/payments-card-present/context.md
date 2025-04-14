# Service Name: Payments Card Present (PCP)
## Overview
The Payments Card Present service is responsible for processing card-present payments (physical card transactions) for Razorpay. It handles the entire payment lifecycle including validation, initiation, confirmation, status checks, and refund flows. The service has two implementation versions: v1 (legacy dual-stack implementation with Ezetap API calls) and v2 (modern single-stack implementation with direct middleware calls).
## Dependencies
- MySQL Database - For storing payment transactions and related data
- Redis - For caching and distributed locking
- Kafka - For event streaming
- Prometheus - For metrics collection
- Coralogix - For logging
- TiDB - For payment entity data for dashboarding
## Downstream Services
- Middleware Service - Direct integration for payment processing in v2 flow
- Ezetap API - For payment processing in v1 flow (deprecated)
- PG Ledger - For transaction acknowledgment
- Event Streaming Service - For publishing events
- TiDB Service - For dashboarding and reporting
- Harvester Service - For dashboard analytics
## Upstream Services
- PG Router - Sends payment requests to the service
- Workflow Server - Integrates with the payment flow
## Main Flows / Workflows
1. Payment Validation Flow
  - Triggered by: API call from PG Router
  - Steps:
   - Create payment entity in database
   - Validate request parameters
   - Return success or failure response
  - Outputs: Validated payment entity or error response
2. Payment Initiation Flow
  - Triggered by: API call after validation
  - Steps:
   - In v1: Call Ezetap API for payment processing
   - In v2: Call middleware directly for payment processing
   - Update payment status
  - Outputs: Payment in authorized state or error response
3. Payment Capture Flow
  - Triggered by: Merchant request or external system
  - Steps:
   - Verify payment is in authorized state
   - Process fund movement from customer to merchant
   - Update payment status to captured
  - Outputs: Captured payment or error response
4. PG Ledger Acknowledgment Flow
  - Triggered by: Kafka message
  - Steps:
   - Process ledger acknowledgment
   - Update payment status
  - Outputs: Updated payment entity
## Data Sources
- MySQL Database - Primary data store for payment entities and transaction data
## Data Schemas (High-Level)
### Table/Model: payments
- Fields:
 - id: string - Primary identifier for the payment
 - amount: int - Payment amount in smallest currency unit
 - currency: string - Currency code
 - status: string - Current status of payment (created, authorized, captured, failed)
 - method: string - Payment method
 - reference_id: string - External reference identifier
 - created_at: timestamp - Creation timestamp
 - updated_at: timestamp - Last update timestamp
### Table/Model: terminal_transactions
- Fields:
 - id: string - Transaction identifier
 - payment_id: string - Reference to payment
 - terminal_id: string - Identifier for the terminal device
 - transaction_data: json - Transaction-specific data
 - status: string - Transaction status
 - created_at: timestamp - Creation timestamp
 - updated_at: timestamp - Last update timestamp
## Security & Auth
- Basic Authentication for Ezetap API integration
- API authentication for middleware calls
- JWT/Token-based authentication for internal service communication
## :gear: Configuration
The service is configured using:
- TOML configuration files (default.toml, dev.toml, etc.)
- Environment variables (can override config file settings)
- Command-line flags for specific runtime options