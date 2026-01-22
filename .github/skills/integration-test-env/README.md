# Integration Test Environment Skill

A GitHub Copilot skill for automatically setting up integration testing environments with Docker containers.

## Structure

```
integration-test-env/
├── SKILL.md              # Skill documentation for Copilot
├── skill.py              # Main orchestration logic
├── docker_manager.py     # Portable Docker utilities (copied from main utils)
├── service_configs.py    # Predefined service configurations
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Usage

### Direct Execution

```bash
cd .copilot/skills/integration-test-env

# Install dependencies
pip install -r requirements.txt

# Run example
python skill.py
```

### Via GitHub Copilot

Once this skill is in your workspace, Copilot will automatically detect it and use it when you ask:

- "Set up integration test environment"
- "Start PostgreSQL for testing"
- "I need Redis and RabbitMQ for integration tests"

## Supported Services

- **PostgreSQL** - Relational database
- **MySQL** - Relational database
- **MongoDB** - Document database
- **Redis** - Cache/database/queue
- **RabbitMQ** - Message queue
- **Elasticsearch** - Search engine
- **MinIO** - S3-compatible storage

## Features

- ✅ Automatic service detection from code
- ✅ Concurrent startup for fast initialization
- ✅ Health checks ensure services are ready
- ✅ Clean connection strings provided
- ✅ Proper cleanup on shutdown
- ✅ Portable across environments (self-contained)

## Example

```python
from skill import IntegrationTestEnvironment

async def setup_tests():
    env = IntegrationTestEnvironment(name_prefix="myapp")
    
    # Start multiple services
    services = await env.start_services(["postgres", "redis"])
    
    # Get connection info
    db_connection = services["postgres"]["connection"]
    # postgresql://test:test@localhost:5432/testdb
    
    # Run your integration tests...
    
    # Cleanup
    await env.stop_all()
```

## Why Portable?

This skill includes its own copy of `docker_manager.py` so it can:
- Be used independently without project dependencies
- Be shared across different projects
- Work in any environment with Docker installed
- Be version-controlled separately if needed

## Development

To extend with new services:

1. Add service configuration to `service_configs.py`
2. Include Docker image, ports, environment variables, and health check
3. Test with `python skill.py`
