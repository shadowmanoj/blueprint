# API Documentation

This document provides an overview of key APIs available across our services.

## Authentication

All API endpoints except those marked as public require authentication. Authentication is performed using JWT tokens.

### Authentication Endpoints

#### POST /api/auth/login

Authenticates a user and returns a JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 123,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### POST /api/auth/register

Registers a new user.

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response:**
```json
{
  "id": 124,
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "created_at": "2023-06-15T10:30:00Z"
}
```

## User Management

### User Endpoints

#### GET /api/users/me

Returns the profile of the currently authenticated user.

**Response:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2023-01-15T08:30:00Z",
  "roles": ["user"]
}
```

#### PUT /api/users/me

Updates the profile of the currently authenticated user.

**Request Body:**
```json
{
  "first_name": "Johnny",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "Johnny",
  "last_name": "Doe",
  "updated_at": "2023-06-15T11:30:00Z"
}
```

## Subscription Management

### Subscription Endpoints

#### GET /api/subscriptions

Returns all subscriptions for the current user.

**Response:**
```json
[
  {
    "id": 456,
    "plan_id": "premium-monthly",
    "status": "active",
    "current_period_start": "2023-06-01T00:00:00Z",
    "current_period_end": "2023-07-01T00:00:00Z"
  }
]
```

#### POST /api/subscriptions

Creates a new subscription for the current user.

**Request Body:**
```json
{
  "plan_id": "premium-monthly",
  "payment_method_id": 789
}
```

**Response:**
```json
{
  "id": 457,
  "plan_id": "premium-monthly",
  "status": "active",
  "current_period_start": "2023-06-15T00:00:00Z",
  "current_period_end": "2023-07-15T00:00:00Z"
}
```

#### PUT /api/subscriptions/{id}

Updates an existing subscription.

**Request Body:**
```json
{
  "plan_id": "premium-annual"
}
```

**Response:**
```json
{
  "id": 457,
  "plan_id": "premium-annual",
  "status": "active",
  "current_period_start": "2023-06-15T00:00:00Z",
  "current_period_end": "2024-06-15T00:00:00Z"
}
```

#### PATCH /api/subscriptions/{id}/pause

Pauses an active subscription.

**Request Body:**
```json
{
  "pause_start_date": "2023-07-01T00:00:00Z",
  "pause_end_date": "2023-10-01T00:00:00Z"
}
```

**Response:**
```json
{
  "id": 457,
  "plan_id": "premium-annual",
  "status": "paused",
  "pause_start_date": "2023-07-01T00:00:00Z",
  "pause_end_date": "2023-10-01T00:00:00Z"
}
```

#### POST /api/subscriptions/{id}/cancel

Cancels an active subscription.

**Response:**
```json
{
  "id": 457,
  "plan_id": "premium-annual",
  "status": "canceled",
  "canceled_at": "2023-06-15T12:30:00Z",
  "current_period_end": "2024-06-15T00:00:00Z"
}
```

## Payment Methods

### Payment Method Endpoints

#### GET /api/payment-methods

Returns all payment methods for the current user.

**Response:**
```json
[
  {
    "id": 789,
    "payment_type": "credit_card",
    "last_four": "4242",
    "expiry_date": "12/25",
    "is_default": true
  }
]
```

#### POST /api/payment-methods

Adds a new payment method for the current user.

**Request Body:**
```json
{
  "payment_type": "credit_card",
  "token": "tok_visa",
  "is_default": false
}
```

**Response:**
```json
{
  "id": 790,
  "payment_type": "credit_card",
  "last_four": "4242",
  "expiry_date": "12/25",
  "is_default": false
}
```

#### PUT /api/payment-methods/{id}

Updates an existing payment method.

**Request Body:**
```json
{
  "is_default": true
}
```

**Response:**
```json
{
  "id": 790,
  "payment_type": "credit_card",
  "last_four": "4242",
  "expiry_date": "12/25",
  "is_default": true
}
```

#### DELETE /api/payment-methods/{id}

Removes a payment method.

**Response:**
```
204 No Content
```

## Notification Preferences

### Notification Preference Endpoints

#### GET /api/notification-preferences

Returns notification preferences for the current user.

**Response:**
```json
[
  {
    "notification_type": "subscription_renewal",
    "channel": "email",
    "is_enabled": true
  },
  {
    "notification_type": "subscription_renewal",
    "channel": "sms",
    "is_enabled": false
  }
]
```

#### PUT /api/notification-preferences

Updates notification preferences for the current user.

**Request Body:**
```json
{
  "notification_type": "subscription_renewal",
  "channel": "sms",
  "is_enabled": true
}
```

**Response:**
```json
{
  "notification_type": "subscription_renewal",
  "channel": "sms",
  "is_enabled": true
}
``` 