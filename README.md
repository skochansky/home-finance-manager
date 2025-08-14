# Home Finance Manager - Microservices Architecture

A microservices-based home finance management system built with FastAPI and PostgreSQL.

## Architecture Overview

The system consists of 5 main components:

1. **API Gateway** (Port 8000) - Central entry point for all client requests
2. **Transaction Management Service** (Port 8001) - Handle all transaction operations
3. **User Account Management Service** (Port 8002) - User authentication and account management
4. **User Notification Service** (Port 8003) - Handle notifications and preferences
5. **Budget Analysis Service** (Port 8004) - Budget planning and financial analysis

## Services

### 🏛️ API Gateway
- Request routing to microservices
- Authentication middleware
- CORS configuration
- Service health monitoring

### 💳 Transaction Management Service
- CRUD operations for transactions
- Transaction categorization and search
- Transaction history and filtering
- Database: PostgreSQL (transactions)

### 👤 User Account Management Service
- User registration and authentication
- JWT token management
- Account creation and management
- User profile management
- Database: PostgreSQL (accounts)

### 🔔 Notification Service
- Email, SMS, and push notifications
- Notification preferences management
- Notification queue with Redis
- Database: PostgreSQL (notifications) + Redis

### 📊 Budget Analysis Service
- Budget creation and tracking
- Spending analysis and insights
- Budget alerts and recommendations
- Financial reports
- Database: PostgreSQL (budget_analysis)

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.12+ (for local development)
- Poetry (for dependency management)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd home-finance-manager
```

2. Start all services:
```bash
docker-compose up --build
```

3. Access the API Gateway:
```
http://localhost:8000
```

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info

#### Transactions
- `GET /api/v1/transactions/{user_id}` - Get user transactions
- `POST /api/v1/transactions` - Create new transaction

#### Accounts
- `GET /api/v1/accounts` - Get user accounts
- `POST /api/v1/accounts` - Create new account

#### Notifications
- `GET /api/v1/notifications/{user_id}` - Get user notifications
- `GET /api/v1/preferences/{user_id}` - Get notification preferences

#### Budget Analysis
- `GET /api/v1/budgets/{user_id}` - Get user budgets
- `GET /api/v1/budgets/{user_id}/analysis` - Get budget analysis
- `GET /api/v1/insights/{user_id}/spending` - Get spending insights

### Development

#### Running Individual Services

Each service can be run independently for development:

```bash
# Transaction Service
cd hfm-transaction-management-service
poetry install
poetry run python src/main.py

# Account Service
cd hfm-user-account-management-service
poetry install
poetry run python src/main.py

# Notification Service
cd hfm-user-notification-service
poetry install
poetry run python src/main.py

# Budget Service
cd hfm-budget-analysis-service
poetry install
poetry run python src/main.py

# API Gateway
poetry install
poetry run python src/main.py
```

#### Environment Variables

Each service supports the following environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string (notifications service)
- `SECRET_KEY` - JWT secret key (account service)
- Service URLs for inter-service communication

### Database Schema

Each service maintains its own database:

- **transactions**: Transaction records
- **accounts**: Users and their financial accounts
- **notifications**: Notifications and preferences
- **budget_analysis**: Budgets and financial analysis

### Inter-Service Communication

- **Synchronous**: HTTP/REST APIs via API Gateway
- **Asynchronous**: Redis queues for notifications
- **Service Discovery**: Docker Compose networking

## Deployment

### Production Considerations

1. **Security**:
   - Change default passwords and secret keys
   - Configure CORS appropriately
   - Use HTTPS in production
   - Implement proper authentication middleware

2. **Scalability**:
   - Use container orchestration (Kubernetes)
   - Implement load balancing
   - Add caching layers
   - Database connection pooling

3. **Monitoring**:
   - Add health checks
   - Implement logging and metrics
   - Set up service monitoring
   - Error tracking and alerting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.