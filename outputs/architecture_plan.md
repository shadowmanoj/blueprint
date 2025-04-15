```markdown
# High-Level Architecture Plan for Dynamic Currency Conversion (DCC) Integration

## 1. Overview
The goal is to integrate Dynamic Currency Conversion (DCC) into Razorpay's OmniChannel stack, supporting both online and offline merchants. This feature will enable real-time currency conversion with transparent exchange rates, revenue sharing for merchants, and customer opt-in/out functionality. It will also provide a unified dashboard for transaction reconciliation across channels and support aggregator merchants via the Hitachi-RBL BIN Sponsorship Model. The solution must integrate seamlessly with the Razorpay Cross-Border Payments Suite and adhere to service boundaries, data ownership, and compliance requirements.

---

## 2. Feature-to-Service Mapping

| **Feature**                                       | **Mapped Service**                                                                 |
|---------------------------------------------------|------------------------------------------------------------------------------------|
| Dynamic Currency Conversion (DCC) integration    | `payments-cross-border`, `pg-router`, `eze-middleware`, `terminals`               |
| Support for both online and offline merchants     | `payments-card-present`, `pg-router`, `terminals`                                 |
| Real-time currency conversion                    | `payments-cross-border`, `pg-router`                                              |
| Revenue sharing for merchants                    | `payments-cross-border`, `mozart`                                                 |
| Unified dashboard for transaction reconciliation | `mozart`                                                                          |
| Aggregator merchants via Hitachi-RBL BIN Model   | `payments-cross-border`, `pg-router`                                              |
| Customer opt-in/out for DCC                      | `payments-card-present`, `terminals`                                              |
| Integration with Cross-Border Payments Suite     | `payments-cross-border`                                                           |

---

## 3. Suggested Code Touchpoints

### **`payments-cross-border`**
- **Modules to Extend**:
  - **Forex Conversion Module**: Extend to support real-time DCC rates.
  - **Revenue Sharing Module**: Add logic for DCC markup distribution to merchants.
  - **BIN Sponsorship Module**: Implement Hitachi-RBL BIN sponsorship logic.
- **Interfaces**:
  - `ForexRateService`: Add methods for fetching DCC-specific rates.
  - `TransactionProcessor`: Extend to handle DCC-specific transaction attributes.

### **`pg-router`**
- **Modules to Extend**:
  - **Routing Logic**: Add DCC-specific routing for both online and offline transactions.
  - **Transaction Metadata**: Include DCC-related metadata in transaction payloads.
- **Interfaces**:
  - `PaymentMethodRouter`: Add DCC-specific logic for routing transactions.

### **`eze-middleware`**
- **Modules to Extend**:
  - **POS Transaction Processor**: Add support for customer opt-in/out for DCC at POS terminals.
  - **Encryption Module**: Ensure DCC-related data is securely transmitted.
- **Interfaces**:
  - `TransactionWorkflow`: Extend to include DCC opt-in/out logic.

### **`terminals`**
- **Modules to Extend**:
  - **Terminal Configuration**: Add support for enabling/disabling DCC at the terminal level.
  - **Customer Interaction Module**: Implement customer opt-in/out workflows.
- **Interfaces**:
  - `TerminalConfigService`: Add methods to configure DCC settings.

### **`mozart`**
- **Modules to Extend**:
  - **Dashboard Module**: Add DCC-related transaction reconciliation data.
  - **Audit Logs**: Track DCC-related events for compliance and debugging.
- **Interfaces**:
  - `ReconciliationService`: Extend to include DCC-specific reconciliation logic.

### **`payments-card-present`**
- **Modules to Extend**:
  - **Transaction Lifecycle**: Add support for DCC in card-present transactions.
- **Interfaces**:
  - `CardTransactionProcessor`: Extend to handle DCC-specific attributes.

---

## 4. New Components (if needed) with Rationale

### **DCC Rate Management Service**
- **Rationale**: While `payments-cross-border` handles forex rates, a dedicated service for managing DCC-specific rates ensures clear separation of concerns and scalability.
- **Responsibilities**:
  - Fetch and cache DCC rates from third-party providers.
  - Provide APIs for real-time rate queries by other services.
  - Manage rate validity and compliance with regulatory requirements.
- **Interfaces**:
  - `DccRateService`: Provide methods for fetching and validating DCC rates.
- **Integration**:
  - Consumed by `payments-cross-border` and `pg-router`.

---

## 5. Data Flow & Interfaces

### **Online Transactions**
1. **Customer Checkout**:
   - `pg-router` routes the transaction to `payments-cross-border` with DCC metadata.
2. **DCC Rate Fetch**:
   - `payments-cross-border` queries the `DCC Rate Management Service` for real-time rates.
3. **Transaction Processing**:
   - `payments-cross-border` processes the transaction with DCC markup and revenue sharing logic.
4. **Reconciliation**:
   - `mozart` updates the unified dashboard with DCC transaction details.

### **Offline Transactions (POS Terminals)**
1. **Customer Opt-In/Out**:
   - `terminals` handles customer interaction for DCC opt-in/out.
2. **Transaction Routing**:
   - `eze-middleware` routes the transaction to `payments-card-present` with DCC metadata.
3. **DCC Rate Fetch**:
   - `payments-cross-border` queries the `DCC Rate Management Service` for real-time rates.
4. **Transaction Processing**:
   - `payments-card-present` processes the transaction with DCC markup and revenue sharing logic.
5. **Reconciliation**:
   - `mozart` updates the unified dashboard with DCC transaction details.

---

## 6. Risks and Considerations

### **Technical Risks**
1. **Latency**:
   - Real-time rate fetching from third-party providers could introduce latency. Mitigation: Use caching in the `DCC Rate Management Service`.
2. **Service Boundaries**:
   - Clear separation of concerns must be maintained to avoid coupling between services.

### **Compliance Risks**
1. **Regulatory Requirements**:
   - Ensure compliance with forex and DCC regulations in all supported regions.
2. **Customer Transparency**:
   - Clearly display exchange rates and markups to customers.

### **Operational Risks**
1. **Rate Validity**:
   - Ensure rates are updated frequently to avoid discrepancies.
2. **Merchant Adoption**:
   - Provide clear documentation and support for merchants to enable DCC.

---

This architecture plan ensures a scalable, compliant, and reliable integration of DCC into Razorpay's OmniChannel stack while leveraging existing services and introducing minimal new components.
```