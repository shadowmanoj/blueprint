# Repository: Payment Service

## Overview

The Payment Service handles all payment processing, subscription management, and financial transactions across our platform. It integrates with multiple payment gateways and provides a unified API for payment operations.

## Key Technologies

- Java (Spring Boot)
- PostgreSQL
- Kafka for event streaming
- Redis for caching
- Docker
- Kubernetes for deployment
- Stripe, PayPal, and Adyen integrations

## API Endpoints

### Payments

- `POST /api/payments`: Create a new payment
- `GET /api/payments/{id}`: Get payment details
- `POST /api/payments/{id}/capture`: Capture an authorized payment
- `POST /api/payments/{id}/refund`: Refund a payment
- `POST /api/payments/{id}/void`: Void an authorized payment
- `GET /api/payments`: List payments with filtering

### Payment Methods

- `GET /api/payment-methods`: List saved payment methods for a customer
- `POST /api/payment-methods`: Save a new payment method
- `DELETE /api/payment-methods/{id}`: Remove a saved payment method
- `PUT /api/payment-methods/{id}/default`: Set a payment method as default

### Subscriptions

- `POST /api/subscriptions`: Create a new subscription
- `GET /api/subscriptions/{id}`: Get subscription details
- `PUT /api/subscriptions/{id}`: Update a subscription
- `DELETE /api/subscriptions/{id}`: Cancel a subscription
- `POST /api/subscriptions/{id}/pause`: Pause a subscription
- `POST /api/subscriptions/{id}/resume`: Resume a paused subscription

### Products and Plans

- `GET /api/products`: List products
- `GET /api/products/{id}`: Get product details
- `GET /api/products/{id}/plans`: Get plans for a product
- `GET /api/plans/{id}`: Get plan details

## Data Models

### Payment

```java
public class Payment {
    private String id;
    private BigDecimal amount;
    private String currency;
    private PaymentStatus status; // PENDING, AUTHORIZED, CAPTURED, FAILED, REFUNDED, VOIDED
    private String description;
    private String customerId;
    private String paymentMethodId;
    private PaymentProvider provider; // STRIPE, PAYPAL, ADYEN
    private String providerPaymentId;
    private Map<String, Object> metadata;
    private Date createdAt;
    private Date updatedAt;
    private String orderId;
    private String invoiceId;
    private BigDecimal refundedAmount;
    private List<PaymentEvent> events;
}
```

### Subscription

```java
public class Subscription {
    private String id;
    private String customerId;
    private String planId;
    private SubscriptionStatus status; // ACTIVE, PAST_DUE, CANCELED, PAUSED, TRIAL
    private Date startDate;
    private Date endDate;
    private Integer trialDays;
    private Date trialEndDate;
    private Date nextBillingDate;
    private String paymentMethodId;
    private BigDecimal amount;
    private String currency;
    private BillingPeriod billingPeriod; // MONTHLY, YEARLY, WEEKLY, DAILY
    private Boolean autoRenew;
    private Date canceledAt;
    private CancelReason cancelReason;
    private Map<String, Object> metadata;
    private Date createdAt;
    private Date updatedAt;
}
```

## Architecture

The Payment Service uses a microservice architecture with the following components:

- API Gateway: Spring Cloud Gateway for routing
- Payment Controller: Handles payment-related HTTP requests
- Subscription Controller: Handles subscription-related HTTP requests
- Payment Service: Business logic for payment processing
- Subscription Service: Business logic for subscription management
- Provider Adapters: Integration with payment providers (Stripe, PayPal, Adyen)
- Repository Layer: Data access to PostgreSQL
- Event Publisher: Publishes payment events to Kafka
- Event Consumer: Consumes events from other services

## Security Considerations

- PCI DSS compliance for payment processing
- Tokenization of payment details
- Field-level encryption for sensitive data
- HTTPS for all API endpoints
- API authentication with JWT or API keys
- Rate limiting for payment endpoints
- Fraud detection system integration

## Integration Points

- Integrates with Auth Service for customer authentication
- Publishes events to Kafka for other services to consume
- Connects to multiple payment gateways
- Integrates with Notification Service for payment notifications
- Connects to Reporting Service for financial reporting 