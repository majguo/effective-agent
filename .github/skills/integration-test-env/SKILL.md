# Integration Test Environment Setup Skill

Expert skill for automatically setting up integration testing environments with Docker containers for databases, message queues, and other services.

## Capabilities

This skill can:
- Detect required services from code (databases, message queues, caches)
- Spin up Docker containers for integration testing
- Wait for services to be healthy and ready
- Provide connection strings and credentials
- Clean up environments after testing

## When to Use

Automatically invoked when users ask:
- "Set up integration test environment"
- "I need a test database for my app"
- "Start Postgres for testing"
- "Create test environment with Redis and RabbitMQ"
- "Spin up integration testing infrastructure"

## Services Supported

**Databases:**
- PostgreSQL
- MySQL
- MongoDB
- Redis (cache/database)

**Message Queues:**
- RabbitMQ
- Redis (also as queue)

**Other:**
- Elasticsearch
- MinIO (S3-compatible storage)

## Example Usage

User: "Set up PostgreSQL and Redis for integration testing"

The skill will:
1. Start PostgreSQL container on available port
2. Start Redis container on available port
3. Wait for both services to be healthy
4. Return connection information:
   - PostgreSQL: `postgresql://test:test@localhost:5432/testdb`
   - Redis: `redis://localhost:6379`

## Implementation Details

- Uses async Docker operations for fast startup
- Automatic port conflict resolution
- Health checks ensure services are ready before returning
- Proper cleanup on shutdown
- Persistent volumes for data preservation (optional)

## Configuration

Services are preconfigured with sensible defaults:
- Test credentials (username: test, password: test)
- Isolated networks per environment
- Named volumes for data persistence
- Exposed ports for local access

## Code Detection

The skill can analyze code to detect requirements:
- SQLAlchemy/Alembic → PostgreSQL/MySQL
- pymongo → MongoDB
- celery → RabbitMQ/Redis
- redis-py → Redis
- elasticsearch-py → Elasticsearch
