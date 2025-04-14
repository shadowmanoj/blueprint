# High-Level System Architecture Plan

## Overview
Based on the provided feature list and the existing service `Payments Card Present (PCP)` in the codebase, we will map features to existing services where possible and suggest new services if necessary. The goal is to ensure modularity, scalability, and maintainability of the system.

---

## Existing Service: Payments Card Present (PCP)
### Responsibilities:
- **Card-present payments**: Handles physical card transactions.
- **Payment lifecycle**: Includes validation, initiation, confirmation, status checks, and refunds.

---

## Feature Mapping and System Architecture

### 1. **Card-Present Payment Processing**
   - **Mapped Service**: Payments Card Present (PCP)
   - **Details**: This feature is already covered by the PCP service. It handles physical card transactions and the entire payment lifecycle.

---

### 2. **Card-Not-Present Payment Processing**
   - **Proposed New Service**: Payments Card Not Present (PCNP)
   - **Details**: A new service should be created to handle card-not-present transactions (e.g., online payments). This service will include:
     - Validation of card-not-present transactions.
     - Payment initiation and confirmation.
     - Fraud detection and prevention mechanisms.
     - Refund processing.

---

### 3. **Payment Status Checks**
   - **Mapped Service**: Payments Card Present (PCP)
   - **Details**: PCP already supports status checks for card-present transactions. For card-not-present transactions, the functionality should be integrated into the proposed PCNP service.

---

### 4. **Refund Processing**
   - **Mapped Service**: Payments Card Present (PCP)
   - **Details**: PCP handles refunds for card-present transactions. For card-not-present transactions, refund processing should be integrated into the proposed PCNP service.

---

### 5. **Fraud Detection**
   - **Proposed New Service**: Fraud Detection Service (FDS)
   - **Details**: A dedicated service should be created to handle fraud detection for both card-present and card-not-present transactions. This service will:
     - Analyze transaction patterns.
     - Use machine learning models to detect anomalies.
     - Provide APIs for fraud status checks and reporting.

---

### 6. **Payment Analytics**
   - **Proposed New Service**: Payment Analytics Service (PAS)
   - **Details**: A new service should be created to provide analytics for payments. This service will:
     - Aggregate transaction data from PCP and PCNP.
     - Generate insights and reports.
     - Provide APIs for querying analytics data.

---

### 7. **Customer Notifications**
   - **Proposed New Service**: Notification Service (NS)
   - **Details**: A new service should be created to handle customer notifications related to payments. This service will:
     - Send notifications for payment confirmations, refunds, and fraud alerts.
     - Support multiple channels (email, SMS, push notifications).

---

## System Architecture Diagram

```plaintext
+-------------------------+
| Payments Card Present   | <-- Handles card-present transactions
| (PCP)                  |
+-------------------------+
          |
          v
+-------------------------+
| Payments Card Not       | <-- Handles card-not-present transactions
| Present (PCNP)          |
+-------------------------+
          |
          v
+-------------------------+
| Fraud Detection Service | <-- Detects fraud across all transactions
| (FDS)                  |
+-------------------------+
          |
          v
+-------------------------+
| Payment Analytics       | <-- Provides analytics and insights
| Service (PAS)           |
+-------------------------+
          |
          v
+-------------------------+
| Notification Service    | <-- Sends customer notifications
| (NS)                   |
+-------------------------+
```

---

## Summary of Proposed Services
1. **Payments Card Not Present (PCNP)**: Handles online transactions.
2. **Fraud Detection Service (FDS)**: Detects and prevents fraudulent transactions.
3. **Payment Analytics Service (PAS)**: Provides insights and reports on payment data.
4. **Notification Service (NS)**: Manages customer notifications.

---

## Next Steps
1. **Design and implement the proposed services**:
   - Define APIs and data models for each service.
   - Ensure integration points with PCP and other existing systems.
2. **Enhance existing PCP service**:
   - Validate its scalability and performance for card-present transactions.
3. **Set up monitoring and logging**:
   - Implement observability tools for all services to ensure reliability and traceability.

This architecture ensures modularity and scalability while addressing the new feature requirements effectively.