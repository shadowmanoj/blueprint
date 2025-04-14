# 📦 Service Name: Payments Card Present (PCP)
## 🔍 Overview
Payments Card Present is a specialized backend service within Razorpay's payment platform responsible for processing card-present payments (physical card transactions) through point-of-sale terminals. The service handles the entire lifecycle of card-present transactions including validation, initiation, confirmation, status checks, and refund flows. It exists in two implementation versions: v1 (legacy dual-stack with Ezetap API integration) and v2 (modern single-stack with direct middleware calls). As a critical component in Razorpay's retail payment infrastructure, PCP enables merchants to accept in-person card payments while ensuring proper transaction processing, fund movement, and regulatory compliance. The service bridges the physical payment terminal world with Razorpay's digital payment ecosystem, handling complex terminal interactions, authorization flows, and payment captures.
## :link: Dependencies
- **MySQL** - Relational database for storing payment transactions and related entity data
- **Redis** - In-memory cache for distributed locking and temporary data storage
- **Kafka** - Event streaming platform for asynchronous processing and messaging
- **Prometheus** - Metrics collection and monitoring service
- **Gin** - HTTP web framework for REST API implementation
- **GORM** - ORM library for database interactions with MySQL
- **Viper** - Configuration management for handling different environments
- **Goose** - Database migration tool for schema versioning
- **OpenTracing/Jaeger** - Distributed tracing for request flow tracking
- **Heimdall** - HTTP client library with retries and circuit breaking
- **Looplab/FSM** - State machine library for payment status management
- **Zap** - Structured logging library
- **Golang** (v1.21) - Core programming language
- **Golangci-lint** - Static code analysis tool
- **Pre-commit** - Git hooks for code quality checks
## :outbox_tray: Downstream Services
- **Middleware Service** - API calls for direct payment processing in v2 flow
  - Endpoints: Various payment processing endpoints
  - Purpose: Processing card-present payments without Ezetap intermediary
- **Ezetap API** - External API integration for payment processing in v1 flow (deprecated)
  - Endpoints: Various payment endpoints (auth, capture, void)
  - Purpose: Handling terminal interactions and payment processing
- **PG Ledger** - API calls for transaction acknowledgment and reconciliation
  - Purpose: Ensuring payment reconciliation and ledger updates
- **Event Producer Service** - Event publishing for payment status updates
  - Topics: Various payment event topics
  - Purpose: Notifying other systems about payment state changes
- **TiDB** - Data storage service for dashboard and reporting
  - Purpose: Analytics and business intelligence
- **Harvester** - API calls for dashboard analytics
  - Purpose: Data aggregation for analytics
- **BIN SDK** - Internal library integration
  - Purpose: Bank Identification Number information
- **Workflow Server** - API integration for payment flow orchestration
  - Purpose: Complex payment flow management
- **DCS (Data Control Service)** - Feature flag and configuration checks
  - Purpose: Dynamic service configuration
## 📥 Upstream Services
- **PG Router** - Sends payment requests through API calls
  - Communication: REST API
  - Purpose: Initial payment routing and validation
- **Verify Callback** - Triggered for payment status verification
  - Communication: Webhook/API call
  - Purpose: Verify payment status after failures
- **Timeout Callback** - Triggered for payment timeout handling
  - Communication: Webhook/API call
  - Purpose: Cancel authorizations for timed-out payments
- **Kafka Consumers** - Process acknowledgment messages
  - Communication: Kafka topics
  - Purpose: Asynchronous payment processing
## :repeat: Main Flows / Workflows
1. **Payment Validation Flow**
   - Triggered by: API call from PG Router
   - Steps:
     - Receive validation request with payment details
     - Create payment entity in database with "created" status
     - Validate request parameters (amount, currency, etc.)
     - Perform fail-fast validations to prevent invalid transactions
     - Return validation result to caller
   - Outputs: Validated payment entity or validation failure response
2. **Payment Initiation Flow**
   - Triggered by: API call after successful validation
   - Steps:
     - In v1: Call Ezetap API for payment processing
     - In v2: Call middleware directly for payment processing
     - Process authorization leg of the payment
     - Update payment entity status to "authorized" or "failed"
     - Register verify and timeout callbacks with PG Router
   - Outputs: Payment in authorized state or error response
3. **Payment Capture Flow**
   - Triggered by: Merchant request or external system
   - Steps:
     - Verify payment is in authorized state
     - Process fund movement from customer to merchant's Razorpay balance
     - Update payment status to "captured"
     - Publish capture event for downstream processing
   - Outputs: Captured payment or error response
4. **PG Ledger Acknowledgment Flow**
   - Triggered by: Kafka message
   - Steps:
     - Consume ledger acknowledgment message
     - Process acknowledgment data
     - Update payment status and reconciliation data
     - Handle any anomalies or errors
   - Outputs: Updated payment entity with acknowledgment status
5. **Payment Verify Flow**
   - Triggered by: PG Router callback
   - Steps:
     - Check payment status with the method service or gateway
     - Retry authorization if possible
     - Update payment status based on verification result
     - Notify relevant systems about status change
   - Outputs: Updated payment status (success or terminal failure)
6. **Payment Timeout Flow**
   - Triggered by: PG Router callback
   - Steps:
     - Check current payment status
     - Cancel the authorization if payment is still in progress
     - Update payment status to "failed"
     - Log timeout details
   - Outputs: Failed payment with timeout reason
## 🧾 Use Cases
- Processing in-person card payments at physical retail locations
- Authorizing and capturing funds for card-present transactions
- Supporting physical point-of-sale payment terminals
- Reconciling payment transactions with ledger records
- Providing real-time payment status updates to merchants
- Handling payment failures and retries for card transactions
- Supporting offline transaction processing capabilities
- Enabling secure PCI-compliant card payment processing
## :scroll: Repo Rules (Do's and Don'ts)
### ✅ Do
- Implement new features exclusively in v2 flow (v1 is deprecated)
- Use the payment service interface for consistent implementation
- Follow transaction-based database operations for data integrity
- Implement proper error handling with custom error types
- Use context propagation for request scoping and tracing
- Utilize structured logging with trace codes for better debugging
- Write unit tests for all new functionality
- Use the service registry pattern for dependency management
- Run linting and pre-commit hooks before submitting code
### ❌ Don't
- Add new features to v1 flow (it's being deprecated)
- Make direct database calls outside the repository layer
- Implement business logic in API handlers
- Use hardcoded configuration values
- Mix domain logic with integration code
- Bypass middleware for direct external API calls
- Create tight coupling between service components
- Leave sensitive data unencrypted in logs or database
## 🌐 API Endpoints
- **POST /api/v1/payments/validate**
  - Auth: PG Router auth
  - Description: Validates payment request parameters
  - Request: Payment validation parameters (amount, currency, method)
  - Response: Validation result (success/failure)
  - Error codes: 400 (Bad Request), 500 (Internal Server Error)
- **POST /api/v1/payments/initiate**
  - Auth: PG Router auth  
  - Description: Initiates payment processing
  - Request: Payment initiation parameters (order_id, amount, terminal_id)
  - Response: Payment status and details
  - Error codes: 400 (Bad Request), 500 (Internal Server Error), 504 (Gateway Timeout)
- **POST /api/v1/payments/confirm**
  - Auth: PG Router auth
  - Description: Confirms and captures payment
  - Request: Payment confirmation parameters (payment_id)
  - Response: Confirmation status
  - Error codes: 400 (Bad Request), 404 (Not Found), 500 (Internal Server Error)
- **POST /api/v1/payments/check-status**
  - Auth: PG Router auth
  - Description: Retrieves current payment status
  - Request: Payment identifier
  - Response: Current payment status and details
  - Error codes: 400 (Bad Request), 404 (Not Found), 500 (Internal Server Error)
- **POST /api/v1/payments/verify**
  - Auth: PG Router auth
  - Description: Verifies payment status with gateway
  - Request: Payment verification parameters
  - Response: Verification result
  - Error codes: 400 (Bad Request), 404 (Not Found), 500 (Internal Server Error)
- **GET /api/v1/health**
  - Auth: None
  - Description: Health check endpoint
  - Response: Service health status
  - Error codes: 500 (Internal Server Error)
## 📦 Third-Party Integrations
- **Ezetap API**
  - Type: External REST API
  - Purpose: Payment processing for v1 flow
  - Auth: Basic authentication
  - Retry: Implemented with Heimdall client with exponential backoff
  - Endpoints: Various payment processing endpoints (auth, capture, void)
## 🗄️ Data Sources
- **MySQL Database** - Primary data store for payment entities and transaction data
  - Stores: Payment records, terminal transactions, configuration
- **Redis Cache** - Used for distributed locking and temporary data
  - Stores: Locks, session data, temporary processing states
## :dna: Data Schemas (High-Level)
### Table/Model: payments
- Fields:
  - id: string - Primary identifier for the payment
  - amount: int - Payment amount in smallest currency unit
  - currency: string - Currency code
  - status: string - Current status of payment (created, authorized, captured, failed)
  - method: string - Payment method
  - reference_id: string - External reference identifier
  - order_id: string - Associated order ID
  - terminal_id: string - Terminal device identifier
  - merchant_id: string - Merchant identifier
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
### Table/Model: pg_ledger_acknowledgements
- Fields:
  - id: string - Acknowledgment identifier
  - payment_id: string - Reference to payment
  - status: string - Acknowledgment status
  - data: json - Acknowledgment data
  - created_at: timestamp - Creation timestamp
  - updated_at: timestamp - Last update timestamp
## 🔐 Security & Auth
- **Basic Authentication** - Used for Ezetap API integration
  - Username/password stored securely in configuration
- **API Authentication** - For middleware calls and inter-service communication
  - Token-based authentication for internal service calls
- **JWT/Token-based Auth** - For internal service communication
  - JWT tokens with appropriate claims and expiration
- **Key Redaction** - Sensitive fields are redacted in logs
  - PAN, card details, and other PII are automatically redacted
## ⚙️ Configuration
- **TOML Configuration Files**:
  - default.toml - Base configuration for all environments
  - dev.toml - Development environment overrides
  - stage.toml - Staging environment overrides
  - prod.toml - Production environment overrides
- **Environment Variables** - Can override config file settings
  - DEV_SERVE - For development server setup
  - Prefixed with configuration key paths (e.g., DB_HOST)
- **Command-line Flags**:
  - base_path - Directory for configuration loading
  - env - Environment to initialize (default: dev)
  - command - For command mode execution
Key configuration areas include:
- Database connection settings (host, user, password, database)
- Redis connection settings (host, port, auth)
- Kafka configuration (brokers, topics, consumer groups)
- HTTP server settings (port, timeouts)
- Prometheus metrics settings (port, endpoint)
- API integration endpoints and credentials
- Logger configuration (level, format)
- Feature flags and toggles
## 🕒 Schedulers / Cron Jobs
- **PG Ledger Cron**
  - Schedule: Configured as a recurring job
  - Purpose: Processes PG ledger transactions in batches
  - Steps:
    - Fetch pending ledger transactions
    - Process each transaction
    - Update transaction status
  - Output: Updated transaction records and reconciliation data
## 📈 Metrics & Observability
- **Prometheus Metrics**:
  - Payment processing counts by status
  - API endpoint response times
  - Error rates by type
  - Database operation latencies
- **Structured Logging**:
  - Using logger package with trace codes
  - Log level configuration (INFO, DEBUG, ERROR)
  - Context-aware logging with request IDs
- **Coralogix Integration**:
  - Log aggregation and analysis
  - Query language for log searching
  - Dashboard for monitoring
- **Health Endpoints**:
  - /api/v1/health for service health checks
  - Database connectivity checks
  - Dependency health verification
- **Profiling Support**:
  - Memory usage tracking
  - CPU profiling
  - Goroutine analysis