# Repository: Notification Service

## Overview

The Notification Service is responsible for sending various types of notifications to users across different channels (email, SMS, push notifications, in-app messages). It provides a unified API for other services to send notifications while abstracting the delivery mechanisms.

## Key Technologies

- Python (FastAPI)
- PostgreSQL for storage
- Redis for caching and rate limiting
- RabbitMQ for asynchronous processing
- Docker
- Kubernetes for deployment
- SendGrid, Twilio, Firebase Cloud Messaging integrations

## API Endpoints

### Notifications

- `POST /api/notifications`: Send a new notification
- `GET /api/notifications/{id}`: Get notification details
- `GET /api/notifications`: List notifications with filtering
- `DELETE /api/notifications/{id}`: Delete a notification

### Templates

- `POST /api/templates`: Create a notification template
- `GET /api/templates/{id}`: Get template details
- `PUT /api/templates/{id}`: Update a template
- `DELETE /api/templates/{id}`: Delete a template
- `GET /api/templates`: List templates
- `POST /api/templates/{id}/render`: Preview a rendered template

### Preferences

- `GET /api/users/{userId}/preferences`: Get user notification preferences
- `PUT /api/users/{userId}/preferences`: Update user notification preferences
- `PUT /api/users/{userId}/preferences/{channel}/opt-out`: Opt-out from a notification channel
- `PUT /api/users/{userId}/preferences/{channel}/opt-in`: Opt-in to a notification channel

### Channels

- `GET /api/channels`: List available notification channels
- `GET /api/channels/{id}/status`: Check channel operational status

## Data Models

### Notification

```python
class Notification:
    id: str
    user_id: str
    template_id: str
    channels: List[Channel]  # EMAIL, SMS, PUSH, IN_APP
    status: NotificationStatus  # PENDING, SENT, DELIVERED, FAILED
    content: Dict[str, Any]  # Template variables
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    scheduled_for: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[Dict[Channel, datetime]]
    error: Optional[str]
```

### Template

```python
class Template:
    id: str
    name: str
    description: str
    channels: Dict[Channel, TemplateContent]
    variables: List[str]
    category: str  # TRANSACTIONAL, MARKETING, SYSTEM
    active: bool
    created_at: datetime
    updated_at: datetime
    created_by: str
    version: int
    is_default: bool
```

### UserPreference

```python
class UserPreference:
    user_id: str
    email_notifications: bool
    sms_notifications: bool
    push_notifications: bool
    in_app_notifications: bool
    quiet_hours_start: Optional[time]
    quiet_hours_end: Optional[time]
    time_zone: str
    categories: Dict[str, Dict[Channel, bool]]
    created_at: datetime
    updated_at: datetime
```

## Architecture

The Notification Service follows a microservice architecture with these components:

- API Layer: FastAPI endpoints for notification operations
- Service Layer: Business logic for notification processing
- Channel Adapters: Integrations with delivery channels (email, SMS, push, in-app)
- Template Engine: Renders templates with provided variables
- Queue Manager: Handles asynchronous delivery via RabbitMQ
- Scheduler: Manages scheduled notifications
- Analytics: Tracks delivery status and engagement
- Repository Layer: Data access to PostgreSQL

## Design Patterns

- Adapter Pattern: For channel integrations
- Template Method: For notification processing
- Strategy Pattern: For delivery mechanisms
- Observer Pattern: For status updates
- Factory Pattern: For notification creation

## Integration Points

- Consumes events from RabbitMQ for asynchronous notification requests
- Integrates with Auth Service for user validation
- Connects to User Service for user preferences and contact information
- Integrates with multiple delivery providers (SendGrid, Twilio, FCM)
- Publishes notification status events for other services to consume

## Technical Debt and Future Improvements

- Replace custom template engine with a more robust solution
- Improve delivery tracking and analytics
- Add support for more notification channels (WhatsApp, Slack)
- Implement more sophisticated rate limiting and batching
- Add A/B testing capability for notification templates 