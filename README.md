# Payment Service

Simplified payment processing microservice for RideShare Pro.

## Features

- 💳 Payment method management (add, list, delete cards)
- 💰 Transaction processing (mock payments)
- 🔐 JWT authentication
- 🏥 Health checks
- 🐳 Docker containerization
- ☸️ Kubernetes deployment ready

## Quick Start

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start with Docker Compose:**
```bash
docker-compose up -d
```

4. **Or run directly:**
```bash
cd src
python main.py
```

The service will be available at: `http://localhost:8000`

### API Documentation

Interactive API docs: `http://localhost:8000/docs`

## API Endpoints

### Payment Methods
- `POST /api/payments/payment-methods` - Add payment method
- `GET /api/payments/payment-methods` - List payment methods
- `DELETE /api/payments/payment-methods/{id}` - Delete payment method

### Transactions
- `POST /api/payments/process` - Process payment
- `GET /api/payments/transactions` - Get transaction history
- `GET /api/payments/transactions/{id}` - Get specific transaction

### Health
- `GET /api/payments/health` - Health check

## Database Schema

### payment_methods
- `id` (UUID) - Primary key
- `user_id` (UUID) - User identifier
- `card_last_four` (String) - Last 4 digits of card
- `card_brand` (String) - Card brand (visa, mastercard, etc.)
- `is_default` (Boolean) - Default payment method flag
- `created_at` (DateTime) - Creation timestamp

### transactions
- `id` (UUID) - Primary key
- `ride_id` (UUID) - Associated ride
- `user_id` (UUID) - User identifier
- `amount` (Decimal) - Payment amount
- `status` (String) - Transaction status
- `payment_method_id` (UUID) - Payment method used
- `created_at` (DateTime) - Creation timestamp

## Deployment

### Kubernetes

1. **Apply secrets:**
```bash
kubectl apply -f k8s/secrets.yaml
```

2. **Deploy service:**
```bash
kubectl apply -f k8s/deployment.yaml
```

3. **Set up autoscaling:**
```bash
kubectl apply -f k8s/hpa.yaml
```

## Testing

Example API calls:

```bash
# Add payment method
curl -X POST "http://localhost:8000/api/payments/payment-methods" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "card_last_four": "4242",
    "card_brand": "visa",
    "is_default": true
  }'

# Process payment
curl -X POST "http://localhost:8000/api/payments/process" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "ride_id": "123e4567-e89b-12d3-a456-426614174000",
    "amount": 25.50
  }'
```

## Architecture

This service follows microservice patterns:
- Async/await with FastAPI
- PostgreSQL for persistence
- JWT for authentication
- Container-ready deployment
- Kubernetes-native scaling

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - JWT signing secret
- `APP_HOST` - Application host (default: 0.0.0.0)
- `APP_PORT` - Application port (default: 8000)
