# Stock Data Microservices

A microservices architecture for collecting, processing, and serving stock market data.

## Services

- Data ingestion service for real-time stock prices
- Data processing service for analytics and calculations  
- API service for client applications
- Database service for persistent storage

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/stock-data-microservices.git

# Start all services
docker-compose up -d
```

## API Endpoints

- `GET /api/stocks/{symbol}` - Get current stock price
- `GET /api/stocks/{symbol}/history` - Get historical data
- `GET /api/stocks/trending` - Get trending stocks

## Technologies

- Node.js/Express for API services
- Docker for containerization
- Database for data persistence
- Message queue for service communication