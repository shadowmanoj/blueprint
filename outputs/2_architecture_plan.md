```markdown
# High-Level Architecture Plan

## 1. Overview
This architecture plan integrates Dynamic Currency Conversion (DCC) into the existing microservices environment. It introduces a unified DCC solution for online and offline payments, supports aggregator merchants via the Hitachi-RBL BIN sponsorship model, and provides real-time currency conversion with transparent exchange rates. Additionally, it includes customer opt-in/out functionality, revenue sharing for merchants, and a unified dashboard for transaction management and reconciliation. Where existing services are insufficient, new services are proposed to maintain clear service boundaries and scalability.

---

## 2. Feature-to-Service Mapping

| **Feature**                                                                 | **Target Service(s)**                     |
|-----------------------------------------------------------------------------|-------------------------------------------|
| Dynamic Currency Conversion (DCC) integration into OmniChannel Stack       | `Payment Gateway Service`, `DCC Service` (new) |
| Support for aggregator merchants via Hitachi-RBL BIN Sponsorship Model      | `Merchant Management Service`, `BIN Sponsorship Service` (new) |
| Unified DCC solution for online and offline payments                        | `Payment Gateway Service`, `DCC Service` (new) |
| Real-time currency conversion with transparent exchange rates               | `DCC Service` (new), `Exchange Rate Provider Integration` |
| Customer opt-in/out for DCC at POS terminals and online checkouts           | `POS Service`, `Checkout Service`, `DCC Service` (new) |
| Revenue sharing for merchants on DCC markup fees                            | `Revenue Management Service` (new)       |
| Unified dashboard for transaction management and reconciliation             | `Reporting & Reconciliation Service`     |

---

## 3. New Components (If Any)

### 3.1 DCC Service
- **Purpose**: Handles all DCC-related operations, including currency conversion, exchange rate retrieval, and customer opt-in/out logic.
- **Justification**: Centralizing DCC logic ensures reusability across online and offline channels while maintaining a clear separation of concerns.
- **Responsibilities**:
  - Fetch real-time exchange rates from external providers.
  - Calculate markup fees and apply them to transactions.
  - Manage customer opt-in/out preferences.
  - Publish DCC-related events for downstream services.

### 3.2 BIN Sponsorship Service
- **Purpose**: Manages BIN sponsorship models for aggregator merchants, including onboarding, validation, and integration with Hitachi-RBL.
- **Justification**: A dedicated service ensures compliance with sponsorship requirements and isolates this functionality from other merchant management logic.
- **Responsibilities**:
  - Onboard aggregator merchants under the BIN sponsorship model.
  - Validate transactions against sponsored BINs.
  - Integrate with Hitachi-RBL APIs.

### 3.3 Revenue Management Service
- **Purpose**: Handles revenue sharing calculations and payouts for merchants based on DCC markup fees.
- **Justification**: A separate service ensures scalability and flexibility in managing complex revenue-sharing models.
- **Responsibilities**:
  - Calculate revenue shares for merchants.
  - Generate payout schedules.
  - Provide APIs for reporting and reconciliation.

---

## 4. High-Level Data Flow / Interactions

1. **Online Checkout Flow**:
   - `Checkout Service` calls `DCC Service` to fetch real-time exchange rates and calculate converted amounts.
   - `DCC Service` integrates with external exchange rate providers via APIs.
   - Customer opts in/out for DCC, and `DCC Service` records the preference.
   - `Payment Gateway Service` processes the transaction with the converted amount (if opted in).

2. **POS Terminal Flow**:
   - `POS Service` interacts with `DCC Service` for real-time currency conversion.
   - Customer opt-in/out is handled at the terminal and sent to `DCC Service`.

3. **Revenue Sharing**:
   - `DCC Service` publishes events with transaction details and markup fees to a Kafka topic.
   - `Revenue Management Service` consumes these events, calculates revenue shares, and schedules payouts.

4. **Aggregator Merchant Support**:
   - `Merchant Management Service` interacts with `BIN Sponsorship Service` for onboarding and validation.
   - `BIN Sponsorship Service` integrates with Hitachi-RBL APIs for sponsorship compliance.

5. **Unified Dashboard**:
   - `Reporting & Reconciliation Service` aggregates data from `Payment Gateway Service`, `DCC Service`, and `Revenue Management Service` to provide a unified view of transactions and payouts.

---

## 5. Key Considerations / Risks

1. **Real-Time Exchange Rate Latency**:
   - Ensure low-latency integration with external exchange rate providers to avoid checkout delays.
   - Consider caching exchange rates with a short TTL for high-traffic scenarios.

2. **Scalability**:
   - `DCC Service` and `Revenue Management Service` must handle high transaction volumes, especially during peak periods.
   - Use event-driven architecture (e.g., Kafka) to decouple services and improve scalability.

3. **Compliance**:
   - Ensure `BIN Sponsorship Service` adheres to regulatory requirements for aggregator merchants.
   - Maintain audit logs for all DCC-related transactions and opt-in/out actions.

4. **Customer Experience**:
   - Provide clear and transparent exchange rate information to customers.
   - Minimize friction in the opt-in/out process at both POS terminals and online checkouts.

5. **Data Consistency**:
   - Ensure consistent transaction data across `DCC Service`, `Revenue Management Service`, and `Reporting & Reconciliation Service`.
   - Use distributed tracing to debug issues across microservices.

---
```