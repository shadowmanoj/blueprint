# :package: Service Name: Eze-Middleware
## :mag: Overview
Eze-Middleware is a Java-based payment processing service that acts as a critical intermediary layer between payment terminals and various payment gateways. It handles secure payment processing workflows, encryption key management, and transaction routing. The service is built on Spring Boot and provides RESTful APIs for processing payments, managing terminals, and handling settlements. As a core component of Ezetap's payment ecosystem, it securely processes card transactions, supports offline transactions, handles refunds, and manages cryptographic operations through HSM integration. The middleware abstracts the complexity of different payment processors, providing a unified interface for client applications while ensuring adherence to security standards for payment card processing.
## :link: Dependencies
- **Spring Boot (1.3.5.RELEASE)** - Web framework for building RESTful services
- **Spring Cloud (Brixton.RELEASE)** - Microservices architecture support
- **Hibernate (4.3.11.Final)** - ORM framework for database operations
- **MySQL (8.0.27)** - Relational database for transaction and entity storage
- **Redis** - In-memory data structure store for caching and session management
- **jPOS (1.8.2)** - Framework for handling ISO8583 financial message processing
- **Hazelcast (3.9.4)** - Distributed computing platform for caching and clustering
- **Apache POI (3.17)** - Library for working with Microsoft Office formats
- **C3P0 (0.9.5.4)** - JDBC connection pooling library
- **Zip4j (1.3.1)** - ZIP file handling library
- **Amazon POP Encryption Utils (1.0.0)** - Amazon encryption utilities
- **Jetty** - Embedded web server
## :outbox_tray: Downstream Services
- **Payment Gateways** - Multiple banking and payment processors (API) - For processing financial transactions
- **HSM Crypto Module** - Cryptographic operations service (API) - For secure key management and encryption
- **Redis** - Caching service (TCP) - For session management and distributed data
- **MySQL Database** - Relational database (JDBC) - For persistent data storage
- **Eureka Discovery Service** - Service registry (API) - For service discovery
- **File-based Settlement Service** - Settlement processing (Internal) - For transaction settlement
## :inbox_tray: Upstream Services
- **Client Applications** - Mobile and web clients (REST API) - Initiate payment requests
- **Payment Terminals** - Physical devices (REST API) - Send payment transaction data
- **Acquirer Banks** - Financial institutions (API) - Process settlement requests
- **Reporting Systems** - Business intelligence tools (API) - Consume transaction data
- **Omni Channel Applications** - Multi-channel clients (REST API) - Process payments across different channels
## :repeat: Main Flows / Workflows
1. **Payment Processing**
   - Triggered by: REST API Request
   - Steps:
     - Authenticate incoming request via MwareAuthenticationService
     - Extract payment details from MwareInput
     - Process card/payment information through MwareCardPaymentService
     - Route to appropriate payment gateway via PaymentGateway interface
     - Execute transaction through gateway's chargeTransaction method
     - Record transaction details
     - Return response to client
   - Output: Transaction result with success/failure status and gateway response
2. **Terminal Key Exchange**
   - Triggered by: Terminal initialization or API Request
   - Steps:
     - Receive key exchange request via TerminalKeyExchangeService
     - Authenticate terminal credentials
     - Generate or retrieve necessary cryptographic keys
     - Format and encrypt keys for secure transmission
     - Send encrypted keys to terminal
   - Output: Terminal-specific encrypted keys for secure communications
3. **Refund Processing**
   - Triggered by: API Request
   - Steps:
     - Validate original transaction through MwareRefundService
     - Retrieve transaction details from database
     - Process refund through appropriate payment gateway
     - Update transaction records with refund status
     - Generate refund receipt/confirmation
   - Output: Refund transaction result with confirmation ID
4. **Offline Transaction Sync**
   - Triggered by: API Request or Scheduled Task
   - Steps:
     - Receive offline transactions batch via MwareOfflineSyncTransactionService
     - Validate transaction integrity and merchant credentials
     - Process transactions through appropriate payment gateways
     - Update transaction statuses in database
     - Generate reconciliation report
   - Output: Batch processing results with status for each transaction
5. **Settlement Processing**
   - Triggered by: Scheduled Task or API Request
   - Steps:
     - Gather unsettled transactions through MwareSettleTerminal
     - Group transactions by acquirer/gateway
     - Submit settlement requests to payment gateways
     - Process settlement responses and update transaction status
     - Generate settlement reports
   - Output: Settlement report with batch totals and status
## :receipt: Use Cases
- Process card-present payment transactions securely on physical terminals
- Handle card-not-present transactions for e-commerce and phone orders
- Process refunds and reversals for completed transactions
- Support pre-authorization and completion workflows for hospitality/rental services
- Manage terminal key exchange for secure communications
- Support offline transaction processing for poor connectivity scenarios
- Generate settlement reports for reconciliation
- Facilitate EMI (Equated Monthly Installment) transactions
- Process loyalty transactions (earn/redeem points)
- Support BQR (Bharat QR) and UPI (Unified Payments Interface) transactions
## :scroll: Repo Rules (Do's and Don'ts)
### :white_check_mark: Do
- Use service interfaces and implementations for business logic
- Implement error handling with standardized error codes
- Use Spring dependency injection for component management
- Follow the controller → service → client pattern
- Use appropriate authentication for all API endpoints
- Implement logging for all significant operations
- Use transaction management for database operations
- Handle cryptographic operations through the HSM module
### :x: Don't
- Don't expose sensitive information in logs or responses
- Don't implement direct database operations in controllers
- Don't hardcode configuration values in source code
- Don't use deprecated payment gateway APIs
- Don't implement custom cryptographic algorithms
- Don't bypass authentication mechanisms
- Don't store sensitive card data in plaintext
## :globe_with_meridians: API Endpoints
- **POST /mware/{task}**
  - Auth: Session-based authentication
  - Description: Generic endpoint for various middleware tasks
  - Request: MwareInput containing API input, signature, and tokens
  - Response: ClientApiOutput with transaction status and details
  - Error codes: UNAUTHENTICATED_MWARE_REQUEST, PG_FATAL_EXCEPTION, JAVA_EXCEPTION_CAUGHT, KEK_NOT_SET
- **POST /mware/omni/terminalKx**
  - Auth: Session-based authentication
  - Description: Terminal key exchange endpoint
  - Request: MwareInput with terminal details
  - Response: TerminalKXOutput with encrypted keys
  - Error codes: DEVICE_V2_KEY_EXCHANGE_FAILED
- **POST /login**
  - Auth: None (authentication endpoint)
  - Description: Authenticates users/systems to use middleware APIs
  - Request: Login credentials
  - Response: Authentication token and session info
  - Error codes: INVALID_CREDENTIALS, ACCOUNT_LOCKED
## :package: Third-Party Integrations
- **Payment Gateway Processors** - API - Process financial transactions - Certificate-based auth - Implements retry with exponential backoff
- **HSM (Hardware Security Module)** - API/SDK - Secure cryptographic operations - Key-based authentication - Hardware-level security
- **Amazon POP Encryption** - SDK - Payment data encryption - Key-based - Managed through key rotation policies
## :file_cabinet: Data Sources
- **MySQL Database** - SQL - Stores transaction data, terminal information, and entity relationships
- **Redis** - NoSQL/Cache - Stores session data, distributed locks, and temporary transaction state
- **File System** - Blob - Stores logs, configuration files, and temporary report data
## :dna: Data Schemas (High-Level)
### Transaction
- Fields:
  - transaction_id: String - Unique identifier for the transaction
  - amount: Decimal - Transaction amount
  - currency: String - Currency code (e.g., INR, USD)
  - status: Enum - Transaction status (PENDING, COMPLETED, FAILED, SETTLED)
  - payment_method: String - Payment method used (CARD, UPI, QR)
  - terminal_id: String - Terminal identifier
  - merchant_id: String - Merchant identifier
  - payment_gateway: Enum - Gateway used for processing
  - created_at: Timestamp - Creation time
  - updated_at: Timestamp - Last update time
### Terminal
- Fields:
  - terminal_id: String - Unique identifier for the terminal
  - serial_number: String - Physical terminal serial number
  - model: String - Terminal model identifier
  - firmware_version: String - Current firmware version
  - status: Enum - Terminal status (ACTIVE, INACTIVE, PENDING)
  - last_active: Timestamp - Last communication time
  - merchant_id: String - Associated merchant
### EncryptionKey
- Fields:
  - key_id: String - Unique identifier for the key
  - key_type: Enum - Type of key (PIN, DATA, MAC, KEK)
  - key_value: Encrypted - Actual key value (encrypted)
  - activation_date: Timestamp - When key becomes active
  - expiry_date: Timestamp - When key expires
  - status: Enum - Key status (ACTIVE, INACTIVE, ROTATED)
## :closed_lock_with_key: Security & Auth
- Spring Security framework for authentication and authorization
- HSM integration for secure cryptographic operations
- Session-based authentication for API access with AuthSessionUtil
- Signature verification for request integrity
- Terminal authentication using key exchange protocols
- Encrypted communication with payment gateways using TLS
- Data encryption for sensitive payment information
- DEK (Data Encryption Key) and KEK (Key Encryption Key) management
- PCI-DSS compliant handling of card data
## :gear: Configuration
- **Spring Boot application.properties** - Main service configuration
- **Environment-specific profiles** - Development, testing, production settings
- **System environment variables** - For sensitive credentials and endpoints
- **JVM parameters** - Memory and performance tuning (specified in pom.xml)
- **Logging configuration** - Log levels, formats, and destinations
- **HSM configuration** - Cryptographic module settings
- **Payment gateway configurations** - Endpoint URLs, credentials, and timeout settings
- **Database connection parameters** - Connection pools, timeouts, and credentials
## :clock3: Schedulers / Cron Jobs
- **Batch Settlement Job** - Daily (typically midnight) - Settles pending transactions - Produces settlement reports
- **Offline Transaction Sync** - Every 6 hours - Synchronizes cached offline transactions - Updates transaction statuses
- **Key Rotation** - Weekly - Rotates cryptographic keys - Maintains key security
- **Transaction Cleanup** - Daily - Archives old transaction data - Optimizes database performance
## :chart_with_upwards_trend: Metrics & Observability
- Transaction volume metrics by payment gateway and merchant
- API response time tracking for performance monitoring
- Error rate monitoring by endpoint and payment gateway
- Payment success/failure ratio tracking
- Structured logging using SLF4J with transaction correlation IDs
- Jetty access logs for API request tracking
- Transaction tracing across payment gateway interactions
- System health metrics for database, Redis, and service connections
