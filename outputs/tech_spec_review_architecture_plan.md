# System Architecture Plan

Below is a high-level system architecture plan that maps the provided features to existing services or proposes new services/components where necessary. Each feature is analyzed for integration points, ownership, and responsibilities.

---

## Features Mapping and Architecture

### 1. **Third-Party Payment Gateway Integration**
   - **Mapped Service**: **Mozart**
   - **Responsibilities**:
     - Manage integration with external payment gateways.
     - Handle API calls and configurations for third-party payment services.
     - Log audit trails for gateway interactions using PostgreSQL.
   - **Data Flow**:
     - Incoming requests from **pg-router** → Mozart → Third-party gateway APIs → Response back to **pg-router**.

---

### 2. **Secure Payment Processing**
   - **Mapped Service**: **Eze-Middleware**
   - **Responsibilities**:
     - Act as the intermediary layer for secure payment processing.
     - Manage encryption key lifecycle and secure workflows.
     - Interface with payment terminals and gateways.
   - **Data Flow**:
     - Payment initiation from **Terminals** → Eze-Middleware → Payment Gateways via **pg-router**.

---

### 3. **Cross-Border Payments**
   - **Mapped Service**: **Payments Cross Border**
   - **Responsibilities**:
     - Handle international transactions, including forex conversion and compliance.
     - Manage lifecycle of cross-border payments.
   - **Data Flow**:
     - Incoming cross-border payment requests from **pg-router** → Payments Cross Border → Forex and compliance services → Response back to **pg-router**.

---

### 4. **Payment Terminal Management**
   - **Mapped Service**: **Terminals**
   - **Responsibilities**:
     - Onboard, configure, and manage lifecycle of payment terminals.
     - Provide APIs for terminal-related operations.
   - **Data Flow**:
     - Merchant onboarding requests → Terminals → Configuration updates → Terminals → Integration with **Eze-Middleware** for payment processing.

---

### 5. **Payment Routing**
   - **Mapped Service**: **pg-router**
   - **Responsibilities**:
     - Route payment requests across various payment methods.
     - Act as the central intermediary between the API layer and backend services.
   - **Data Flow**:
     - Incoming payment requests → pg-router → Appropriate backend service (e.g., Mozart, Payments Cross Border, Payments Card Present) → Response back to API layer.

---

### 6. **Card-Present Payments**
   - **Mapped Service**: **Payments Card Present (PCP)**
   - **Responsibilities**:
     - Handle physical card transactions through point-of-sale terminals.
     - Manage lifecycle of card-present payments.
   - **Data Flow**:
     - Card-present payment initiation from **Terminals** → Payments Card Present → Payment Gateway (via **pg-router**) → Response back to **Terminals**.

---

## Proposed New Services/Components

### 1. **Compliance Service**
   - **Reason**: While Payments Cross Border handles compliance for international transactions, a dedicated service for compliance across all payment types may be needed for scalability and modularity.
   - **Responsibilities**:
     - Centralize compliance checks for domestic and international payments.
     - Integrate with regulatory APIs and maintain audit logs.
   - **Data Flow**:
     - Payment requests from **pg-router** → Compliance Service → Response back to **pg-router**.

### 2. **Monitoring and Analytics Service**
   - **Reason**: To provide real-time monitoring and analytics for all payment flows across services.
   - **Responsibilities**:
     - Aggregate logs and metrics from all services (e.g., Mozart, Eze-Middleware, pg-router).
     - Provide dashboards and alerts for operational insights.
   - **Data Flow**:
     - Logs and metrics from all services → Monitoring and Analytics Service → Dashboards and alerts.

---

## High-Level Data Flow Diagram

```plaintext
API Layer
   ↓
pg-router
   ↙       ↘
Mozart     Payments Cross Border
   ↓             ↓
Third-Party      Forex/Compliance APIs
Gateways         ↓
   ↓             Response
Response         ↑
   ↑             ↑
pg-router        ↑
   ↓             ↓
Eze-Middleware   Payments Card Present
   ↓             ↓
Payment Gateways Payment Terminals
   ↓             ↓
Response         Response
   ↑             ↑
pg-router        ↑
   ↓             ↓
API Layer        API Layer
```

---

## Ownership Summary

| Service Name               | Responsibility                                                                 |
|----------------------------|-------------------------------------------------------------------------------|
| **Mozart**                 | Third-party gateway integration and audit logging.                           |
| **Eze-Middleware**         | Secure payment processing and encryption management.                         |
| **Payments Cross Border**  | Handling international transactions and forex compliance.                    |
| **Terminals**              | Managing payment terminals and their lifecycle.                              |
| **pg-router**              | Routing payments across services and methods.                                |
| **Payments Card Present**  | Processing card-present transactions.                                        |
| **Compliance Service**     | (Proposed) Centralized compliance checks for all payment types.              |
| **Monitoring Service**     | (Proposed) Real-time monitoring and analytics for payment flows.             |

---

## Integration Notes

- **pg-router** acts as the central hub for routing all payment requests to the appropriate backend services.
- **Mozart** and **Payments Cross Border** handle external integrations, while **Eze-Middleware** ensures secure workflows.
- **Terminals** and **Payments Card Present** focus on physical payment instruments.
- Proposed services (Compliance and Monitoring) enhance modularity and scalability.

This architecture ensures clear separation of concerns, scalability, and maintainability across Razorpay's payment ecosystem.