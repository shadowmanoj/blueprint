## :package: Service Name: pg-router
## :mag: Overview
The pg-router service is a critical microservice in the Razorpay payment processing ecosystem responsible for routing payments across various payment methods. It serves as the central intermediary between the API layer and various payment method processors, handling method-agnostic code and orchestrating payment flows. The service is designed to decouple payment routing logic from the core API, allowing for more scalable payment method integrations and routing decisions. It handles various aspects of the payment lifecycle including order creation, payment processing, callbacks, and notification management.
## :link: Dependencies
- **Go Modules**: Extensive use of Go packages for core functionality
- **Protocol Buffers**: For gRPC service definitions and API contracts
- **Kafka**: For event streaming and asynchronous processing
- **Docker**: For containerization and deployment
- **MySQL/PostgreSQL**: For persistent storage (inferred from database package)
- **Redis**: For caching (inferred from cache package)
- **gRPC**: For service-to-service communication
- **REST Gateway**: For exposing gRPC services as REST endpoints
- **Various Razorpay SDKs**: For integration with other Razorpay services
## :outbox_tray: Downstream Services
- **Ledger Service**: For creating journal entries and financial record-keeping
- **Notification Service**: For sending notifications to merchants and customers
- **Payment Method Processors**: Various payment gateways and method-specific services
- **Currency Conversion Service**: For handling currency exchanges
- **Cross-border Import Service**: For international payment processing
- **Exchange Service**: For currency and rate handling
## :inbox_tray: Upstream Services
- **API Monolith**: Sends payment creation and processing requests
- **Kafka Topics**: Subscribes to various events for asynchronous processing
- **Client Applications**: May directly call pg-router endpoints for payment operations
- **Webhook Sources**: Receives callbacks from payment gateways and processors
## :repeat: Main Flows / Workflows
1. **Order Creation Flow**
   - Triggered by API request
   - Creates payment order
   - Prepares routing information
   - Returns order creation response
2. **Payment Creation Flow**
   - Triggered by API request
   - Validates payment details
   - Determines optimal payment route
   - Routes to appropriate payment processor
   - Returns payment status and details
3. **Payment Callback Flow**
   - Triggered by payment gateway callback
   - Processes callback data
   - Updates payment status
   - Triggers notifications
   - Initiates ledger entries
4. **Ledger Processing Flow**
   - Triggered by Kafka message
   - Parses transaction data
   - Creates ledger journal entries
   - Posts to ledger service
## :receipt: Use Cases
- Processing payments across various payment methods
- Routing payment requests to appropriate payment processors
- Handling callbacks from payment gateways
- Creating financial ledger entries for transactions
- Sending notifications to merchants and customers
- Optimizing payment routing based on various factors
- Supporting international payments and currency conversion
## :scroll: Repo Rules
### :white_check_mark: Do
- Use the structured logging package for consistent logging
- Follow protocol buffer definitions for service interfaces
- Implement proper error handling and propagation
- Use dependency injection for services
- Follow the established module structure
- Set up Git pre-commit hooks for linting and imports check
### :x: Don't
- Directly integrate new payment methods without going through pg-router
- Access database directly without using repository patterns
- Implement method-specific logic directly in pg-router (should be in method-specific services)
- Skip validation steps in payment processing flows
## :globe_with_meridians: API Endpoints
- **Payment Creation API**
  - Method: POST
  - Auth: JWT
  - Request: Payment details including amount, currency, method
  - Response: Payment ID, status, and routing information
  - Error codes: Various payment processing errors
- **Order Creation API**
  - Method: POST
  - Auth: JWT
  - Request: Order details including items, amount, currency
  - Response: Order ID and creation status
  - Error codes: Order creation errors
- **Payment Status API**
  - Method: GET
  - Auth: JWT
  - Request: Payment ID
  - Response: Current payment status and details
  - Error codes: Not found, processing errors
- **Callback Receiver API**
  - Method: POST
  - Auth: Varies by payment processor
  - Request: Callback data from payment gateway
  - Response: Acknowledgement
  - Error codes: Validation errors, processing errors
## :package: Third-Party Integrations
- **Payment Gateways**: Various payment processors for different payment methods
- **Notification Services**: For sending SMS/email notifications
- **Kafka**: For event streaming and message processing
- **Ledger Systems**: For financial record-keeping
- **Currency Conversion APIs**: For real-time exchange rates
## :file_cabinet: Data Sources
- **Relational Database**: Stores payment, order, and routing information
- **Redis Cache**: Caches frequently accessed data and session information
- **Kafka Streams**: Source of event data for asynchronous processing
## :dna: Data Schemas (High-Level)
- **Payment**
  - ID: string - Unique payment identifier
  - OrderID: string - Associated order
  - Amount: decimal - Payment amount
  - Currency: string - Payment currency
  - Method: string - Payment method
  - Status: string - Current payment status
  - CreatedAt: timestamp - Creation time
  - UpdatedAt: timestamp - Last update time
- **Order**
  - ID: string - Unique order identifier
  - MerchantID: string - Associated merchant
  - Amount: decimal - Order amount
  - Currency: string - Order currency
  - Status: string - Current order status
  - Items: array - Order items
  - CreatedAt: timestamp - Creation time
- **Route**
  - ID: string - Unique route identifier
  - PaymentID: string - Associated payment
  - ProcessorID: string - Selected processor
  - Priority: int - Routing priority
  - Status: string - Routing status
  - CreatedAt: timestamp - Creation time
## :closed_lock_with_key: Security & Auth
- JWT authentication for API requests
- Merchant authentication and authorization
- Secure callback validation from payment processors
- Encrypted communication with payment gateways
- Access controls based on merchant permissions
- Environment variable based secret management
## :gear: Configuration
- Environment variables for service configuration
- Docker Compose for local development setup
- Kubernetes configurations for production deployment
- Feature flags for progressive rollout
- Service discovery configuration
- Rate limiting and circuit breaker settings
## :clock3: Schedulers / Cron Jobs
- **Notification Worker**: Processes and sends notifications to merchants and customers
- **Ledger Worker**: Processes transaction data and creates journal entries
- **Reconciliation Jobs**: Reconciles payment statuses with gateway reports
- **Cleanup Jobs**: Cleans up stale data and expired sessions
## :chart_with_upwards_trend: Metrics & Observability
- Prometheus metrics for service monitoring
- Structured logging with correlation IDs
- Tracing for request flows through the system
- Health check endpoints for service status
- Performance metrics for payment processing times
- Error rate tracking by payment method and merchant
## :test_tube: Testing Strategy
- Unit tests for business logic
- Integration tests for service interactions
- End-to-end tests for complete payment flows
- Mock implementations for external dependencies
- CI pipeline for automated testing
- Load testing for performance validation