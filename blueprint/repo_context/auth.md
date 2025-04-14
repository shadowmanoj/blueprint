# Authentication System

This document provides information about our authentication and authorization system.

## Overview

Our authentication system uses JSON Web Tokens (JWT) to authenticate users and manage sessions. All API requests (except for public endpoints) require a valid JWT token in the Authorization header.

## Authentication Flow

1. User logs in with email/password or OAuth provider
2. Backend validates credentials and generates a JWT token
3. The token is returned to the client
4. The client includes this token in the Authorization header for subsequent requests
5. Server verifies the token signature and extracts user information

## JWT Structure

Our JWT tokens have the following structure:

```
Header.Payload.Signature
```

### Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload
```json
{
  "sub": "123",  // User ID
  "email": "user@example.com",
  "roles": ["user"],
  "iat": 1625097600,  // Issued at timestamp
  "exp": 1625184000   // Expiration timestamp
}
```

## Token Lifetime

- Access tokens: 1 hour
- Refresh tokens: 30 days

## Authorization Model

We use a role-based access control (RBAC) system to manage permissions.

### Roles

1. **guest** - Unauthenticated users with limited access
2. **user** - Regular authenticated users
3. **admin** - Administrative users with advanced privileges
4. **service** - Special role for service-to-service communication

### Permissions

Permissions are granted to roles and checked at the API endpoint level. 

Example permission check:
```python
@requires_permission('subscriptions:read')
def get_subscriptions():
    # ...
```

## Implementation Details

### User Service Role
The User Service is the central authority for authentication and authorization. It:
- Stores user credentials securely
- Issues and signs JWT tokens
- Validates tokens for other services
- Manages user roles and permissions

### Inter-service Authentication
For service-to-service communication, we use:
- API keys for simple cases
- Service JWT tokens for more complex scenarios

### Security Measures

1. **Password Storage**:
   - Passwords are hashed using bcrypt with appropriate work factors
   - No plain-text passwords are ever stored

2. **Token Security**:
   - Tokens are signed with a strong secret
   - Tokens have limited lifetime
   - Tokens can be revoked in case of security issues

3. **Rate Limiting**:
   - Authentication endpoints are rate-limited to prevent brute force attacks

4. **MFA Support**:
   - Support for Multi-Factor Authentication (MFA) via TOTP
   - Backup codes for recovery

## Integration with External Systems

Our authentication system supports integration with:

1. OAuth providers:
   - Google
   - Facebook
   - Apple
   - GitHub

2. Enterprise SSO:
   - SAML 2.0
   - OIDC

## Testing Authentication

For testing purposes:
- Development environment has pre-configured test users
- Test JWT tokens can be generated via the `/api/auth/test-token` endpoint (development only)
- CI/CD pipelines use ephemeral test credentials 