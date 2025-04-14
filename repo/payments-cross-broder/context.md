# :package: Service Name: Payments Cross Border
## :mag: Overview
Payments Cross Border is a specialized backend service within Razorpay's payment platform that handles the complexities of international transactions. It manages the end-to-end lifecycle of cross-border payments, including forex conversion, regulatory compliance (especially for Indian regulations like FEMA and LRS), document generation, and chargeback protection. The service acts as a critical bridge between Razorpay's domestic payment infrastructure and international payment capabilities, enabling merchants to receive payments in foreign currencies while ensuring compliance with financial regulations. Its core functions include forex rate management, transaction processing, document generation for regulatory purposes, and risk assessment for cross-border transactions.
## :link: Dependencies
- **Redis** - In-memory cache for performance optimization and temporary data storage
- **MySQL** - Primary relational database for persistent storage of transaction and entity data
- **AWS SQS** - Queue service for asynchronous job processing and message handling
- **Jaeger** - Distributed tracing system for monitoring and troubleshooting
- **Prometheus** - Metrics collection and monitoring
- **Kafka** - Event streaming platform for real-time data pipelines
- **WDA (Warehouse Data Access)** - Data warehouse access layer for analytics and reporting
- **Governor** - Rule engine for dynamic business logic implementation
- **Golang** (v1.23) - Core programming language
- **gRPC** - High-performance RPC framework for service communication
- **JWT** - Token-based authentication mechanism
- **Protobuf** - Interface definition language for API contracts
## :outbox_tray: Downstream Services
- **PG Router Service** - API calls to fetch order and payment details for processing transactions
- **Business Verification Service (BVS)** - API calls to validate KYC documents and verify user identities
- **Account Service** - API calls to retrieve and verify account information
- **Cross Border SDK** - Library integration for currency support and cross-border utilities
- **Splitz Service** - API calls to manage transaction splits for multi-party settlements
- **Harvester Service** - API calls for document processing and storage
- **Riskified** - External API integration for fraud analysis and chargeback protection
- **Mozart** - Workflow orchestration service for complex business processes
- **DCS (Data Control Service)** - API calls to check feature flags and service configuration
## :inbox_tray: Upstream Services
- **Payment Gateway** - Sends payment events to trigger cross-border processing workflows
- **API Gateway** - Routes external API requests to the service's endpoints
- **Frontend Services** - Initiates checkout and payment flows that require cross-border processing
- **Scheduler/Cron** - Triggers time-based jobs like forex rate updates and recurring tasks
## :repeat: Main Flows / Workflows
1. **Cross Border Payment Processing**
   - Triggered by: API request for payment processing
   - Steps:
     - Verify order details and payment method through PG Router
     - Process forex conversion with current rates
     - Generate required regulatory documents (A2 forms, transaction documents)
     - Initiate payment through the appropriate payment channel
     - Create transaction records in the database
   - Outputs: Processed payment and transaction documents
2. **LRS Processing (Liberalized Remittance Scheme)**
   - Triggered by: Indian customer making a foreign currency payment
   - Steps:
     - Generate LRS quotes with forex rates and fees
     - Validate required documents (PAN, Passport, etc.) using BVS
     - Process A2 form generation for regulatory compliance
     - Handle FEMA (Foreign Exchange Management Act) compliance checks
     - Create transaction records with regulatory details
   - Outputs: Compliant LRS transaction and documentation
3. **Forex Rate Processing**
   - Triggered by: Schedule or on-demand API request
   - Steps:
     - Fetch forex rates from providers (OpenExchange, Airwallex)
     - Process and store forex rates in the database
     - Apply markup based on Governor rules
   - Outputs: Updated forex rates for transactions
4. **Chargeback Protection**
   - Triggered by: Payment authorization request
   - Steps:
     - Risk evaluation of transaction using transaction data
     - Apply risk rules through Governor service
     - Process fraud detection using Riskified integration
     - Make authorization decisions based on risk assessment
   - Outputs: Risk assessment and authorization decision
5. **Document Generation**
   - Triggered by: Various transaction events
   - Steps:
     - Gather required data from multiple sources (order, payment, customer)
     - Generate required documents (A2 form, transaction documents)
     - Store documents using Harvester service
     - Link documents to transactions
   - Outputs: Legally compliant documents for regulatory purposes
## :receipt: Use Cases
- Enabling Indian users to make foreign currency payments under LRS guidelines
- Processing international payments for Indian merchants
- Generating regulatory compliance documents for cross-border transactions
- Providing real-time forex rates with appropriate markups
- Protecting merchants from cross-border payment fraud and chargebacks
- Supporting travel-related foreign currency transactions
- Facilitating GST and TCS calculations for foreign currency transactions
## :scroll: Repo Rules (Do's and Don'ts)
### :white_check_mark: Do
- Use the service registry pattern for dependency management
- Implement proper error handling with custom error types
- Follow the hexagonal architecture with clear separation of concerns
- Use mock generation for testing external dependencies
- Leverage context propagation for tracing and request scoping
- Use proper logging with structured data
- Implement transaction-based database operations
### :x: Don't
- Access database directly without going through repository layer
- Implement business logic in API handlers
- Use hardcoded configuration values
- Mix domain logic with integration code
- Create circular dependencies between packages
- Leave sensitive data unencrypted
## :globe_with_meridians: API Endpoints
- **POST /rzp.payments_cross_border.forex_processing.v1.ForexProcessingService/CheckoutCBFlows**
  - Auth: Public auth
  - Description: Provides forex information for checkout flows
  - Response: Forex rates and processing options
- **POST /rzp.payments_cross_border.documents.v1.DocumentService/FetchInvoiceDocuments**
  - Auth: Private auth
  - Description: Retrieves invoice documents for a transaction
  - Response: Document metadata and content links
- **POST /rzp.payments_cross_border.onboard.v1.PartnerOnboardService/OnboardPartner**
  - Auth: Private auth
  - Description: Onboards a partner for cross-border transactions
  - Response: Onboarding status and details
- **POST /rzp.payments_cross_border.chargeback_protection.v1.ChargebackProtectionService/CreateChargebackProtectionConfig**
  - Auth: Admin auth
  - Description: Creates configuration for chargeback protection
  - Response: Configuration details
## :package: Third-Party Integrations
- **Riskified**
  - Type: External API
  - Purpose: Fraud analysis and chargeback protection
  - Auth: API key authentication
  - Retry: Implements retry with exponential backoff
- **OpenExchange**
  - Type: External API
  - Purpose: Forex rate provider
  - Auth: API key authentication
  - Retry: Simple retry mechanism
- **Airwallex**
  - Type: External API
  - Purpose: Alternative forex rate provider
  - Auth: API key + secret
  - Retry: Implemented with Heimdall client
## :file_cabinet: Data Sources
- **MySQL Database** - Primary data store for transactions, forex rates, and entity relationships
- **Redis Cache** - Temporary storage for forex rates and frequently accessed data
- **WDA** - Data warehouse access for analytics and reporting
- **Trino** - SQL query engine for complex data analytics
## :dna: Data Schemas (High-Level)
### Table/Model: forex_entity
- Fields:
  - id: string - Unique identifier
  - source_currency: string - Source currency code
  - target_currency: string - Target currency code
  - forex_rate: float - Exchange rate
  - markup: float - Markup percentage
  - source_amount: int - Original amount in source currency
  - target_amount: int - Converted amount in target currency
  - status: string - Status of forex entity
  - created_at: timestamp - Creation timestamp
### Table/Model: payer
- Fields:
  - id: string - Unique identifier
  - entity_id: string - Related entity identifier
  - entity_type: string - Type of entity (Order, Payment)
  - name: string - Payer name
  - email: string - Payer email
  - contact: string - Contact information
  - pan_number: string - PAN card number (encrypted)
### Table/Model: import_transaction
- Fields:
  - id: string - Unique identifier
  - order_id: string - Related order ID
  - payment_id: string - Payment ID
  - forex_id: string - Related forex entity ID
  - amount: int - Transaction amount in base currency
  - gst: int - GST amount
  - tcs: int - TCS (Tax Collected at Source) amount
  - other_fees: int - Other fees
  - status: string - Transaction status
  - created_at: timestamp - Creation timestamp
## :closed_lock_with_key: Security & Auth
- **JWT Authentication** - For API access with role-based permissions
- **Passport** - For internal service authentication between Razorpay services
- **AES Encryption** - For sensitive data fields (PAN numbers, personal information)
- **mTLS** - For secure service-to-service communication
- **Secrets Management** - Credentials stored in CredStash and accessed securely
- **Role-based Access** - Different endpoints require different authentication levels (public, private, admin)
## :gear: Configuration
- **Environment Files** - TOML configuration files for different environments:
  - dev.toml
  - stage_test.toml
  - stage_live.toml
  - prod_test.toml
  - prod_live.toml
- **Feature Flags** - Managed through DCS service for controlled feature rollout
- **Service Credentials** - Stored in CredStash and retrieved at runtime
- **Governor Rules** - Configurable business logic implemented through rule chains
- **Environment Variables** - Basic service configuration like ports and hostnames
## :clock3: Schedulers / Cron Jobs
- **Forex Rate Fetching**
  - Schedule: Configured in job settings
  - Purpose: Periodically fetches and updates forex rates from providers
  - Output: Updated forex rates in database
- **LRS Travel Transaction Processing**
  - Schedule: Configured as a recurring job
  - Purpose: Processes travel-related LRS transactions in batches
  - Output: Processed transactions and generated documentation
- **Citi LRS Travel Reverse Statement Processing**
  - Schedule: Configured job
  - Purpose: Processes reverse statements for Citi LRS travel transactions
  - Output: Updated transaction records and reconciliation data
## :chart_with_upwards_trend: Metrics & Observability
- **Prometheus Metrics** - Custom metrics for transaction processing, forex rates, and service performance
- **Structured Logging** - Using logger package with context-aware structured logs
- **Jaeger Tracing** - Distributed tracing for request flows across services
- **Error Tracking** - Integration with Sentry for error monitoring
- **Health Endpoints** - Standard health check endpoints for service monitoring
## :test_tube: Testing Strategy
- **Unit Tests** - For core business logic components
- **Mock Generation** - Using gomock for external dependency mocking
- **Integration Tests** - For testing service interactions
- **E2E Tests** - End-to-end tests for critical flows
- **Test Coverage** - Tracked and enforced through CI pipeline