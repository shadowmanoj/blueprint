# Service Name: Terminals
## Overview
Terminals is a microservice that manages payment terminals (also called payment instruments) within the Razorpay payment ecosystem. It handles the onboarding, configuration, and lifecycle management of various payment terminals/gateways for merchants. The service enables merchants to process different payment methods including cards, UPI, netbanking, wallets, and more through various payment gateways.
## Dependencies
- **PostgreSQL** - Primary database for storing terminal and merchant data
- **Redis** - For caching and distributed locking
- **Razorpay API Service** - For merchant information and method enablement
- **Mozart** - Payment gateway integration service
- **Optimizer** - Payment routing optimization service
- **Vault** - For secure secret management
- **Razorx** - For feature flags and experimentation
- **Event Producer SDK** - For producing events
## Downstream Services
- **Mozart** - For gateway integrations and payment processing
- **API Service** - For syncing terminal data, enabling payment methods, and pricing rules
- **Mozart v2** - Updated gateway integration service
- **Vault** - For storing and retrieving sensitive credentials
- **Optimizer** - For routing payment transactions
## Upstream Services
- **Payment Service** - Uses terminals for processing payments
- **Merchant Onboarding Service** - Initiates terminal creation
- **Admin Dashboards** - For terminal management
- **Merchant Dashboard** - For viewing and configuring terminals
## Main Flows / Workflows
1. **Terminal Onboarding**
   - Triggered by: API Request
   - Steps:
     - Validate merchant information and permissions
     - Check for duplicate terminals
     - Generate terminal identifiers (TID/MID)
     - Create the terminal in the database
     - Enable pricing and payment methods for the merchant
     - Sync with gateway services
   - Outputs: Fully configured terminal
2. **Terminal Activation**
   - Triggered by: API Request or Workflow
   - Steps:
     - Verify terminal details
     - Update terminal status to active
     - Setup gateway-specific configurations
     - Set reminders for pending activations if needed
   - Outputs: Activated terminal ready for payments
3. **Terminal Editing**
   - Triggered by: API Request
   - Steps:
     - Validate edit permissions
     - Update terminal configuration
     - Sync changes with gateway services
   - Outputs: Updated terminal configuration
4. **Terminal Testing**
   - Triggered by: API Request
   - Steps:
     - Create test order
     - Initialize payment
     - Process test transaction
     - Verify status
   - Outputs: Test transaction results
## Data Sources
- **PostgreSQL** - SQL database for storing terminal data, merchant mappings, and configurations
- **Redis** - NoSQL key-value store for caching and distributed locking
## Data Schemas (High-Level)
### Table/Model: Terminal
- Fields:
  - terminal_id: string - Unique identifier for the terminal
  - merchant_id: string - Associated merchant ID
  - org_id: string - Organization ID
  - procurer: string - Who procured the terminal
  - gateway: string - Payment gateway (e.g., HDFC, Paytm, etc.)
  - gateway_acquirer: string - Acquirer bank/institution
  - identifiers: json - Terminal identifiers (TID, MID, etc.)
  - secrets: json - Encrypted sensitive credentials
  - methods: string[] - Enabled payment methods
  - features: json - Feature configurations for different payment methods
  - status: string - Terminal status (active, pending, etc.)
  - enabled: boolean - Whether terminal is enabled
  - mode: int - Test or live mode
  - created_at: timestamp - Creation timestamp
  - updated_at: timestamp - Last update timestamp
### Table/Model: Onboarding
- Fields:
  - gateway: string - Payment gateway
  - org_id: string - Organization ID
  - merchant_id: string - Merchant identifier
  - terminal_id: string - Terminal ID if exists
  - identifiers: json - Terminal identifiers
  - features: json - Configured features
  - secrets: json - Sensitive credentials
  - methods: string[] - Payment methods to enable
  - mode: int - Test or live mode
## Security & Auth
- Basic Authentication for API service communication
- Encrypted secrets storage for terminal credentials
- Role-based access control for terminal management
- Tokenization for sensitive payment information
- Environment-specific configurations (test vs. production)
## :gear: Configuration
- Environment variables for service connections
- TOML configuration files (dev.toml, test.toml)
- Feature flags via Razorx
- Gateway-specific configuration parameters
- Test/Live mode settings