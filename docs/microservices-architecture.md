# Home Finance Manager - Microservices Architecture

## Overview
Refactoring the monolithic home-finance-manager into a microservices architecture with the following services:

## Services

### 1. hfm-api-gateway
- **Purpose**: Central entry point for all client requests
- **Responsibilities**: 
  - Request routing to appropriate microservices
  - Authentication and authorization
  - Rate limiting and API versioning
  - Request/response transformation
- **Technology**: FastAPI, Uvicorn
- **Port**: 8000

### 2. hfm-transaction-management-service
- **Purpose**: Handle all transaction-related operations
- **Responsibilities**:
  - CRUD operations for transactions
  - Transaction categorization
  - Transaction history and search
  - Transaction validation and processing
- **Database**: PostgreSQL
- **Port**: 8001

### 3. hfm-user-account-management-service
- **Purpose**: User and account management
- **Responsibilities**:
  - User registration and authentication
  - Account creation and management
  - User profile management
  - Account balance tracking
- **Database**: PostgreSQL
- **Port**: 8002

### 4. hfm-user-notification-service
- **Purpose**: Handle all notification functionality
- **Responsibilities**:
  - Email notifications
  - Push notifications
  - SMS notifications
  - Notification preferences
  - Notification history
- **Database**: PostgreSQL/Redis
- **Port**: 8003

### 5. hfm-budget-analysis-service
- **Purpose**: Budget planning and financial analysis
- **Responsibilities**:
  - Budget creation and tracking
  - Spending analysis
  - Financial reports and insights
  - Budget alerts and recommendations
- **Database**: PostgreSQL
- **Port**: 8004

## Inter-Service Communication
- **Synchronous**: HTTP/REST APIs via API Gateway
- **Asynchronous**: Message queues (Redis/RabbitMQ) for events
- **Service Discovery**: Docker Compose networking

## Database Strategy
- Each service has its own database (Database per Service pattern)
- Shared data accessed via APIs
- Event-driven architecture for data consistency

## Development Setup
- Docker Compose for local development
- Shared dependencies via base Docker images
- Common configuration management