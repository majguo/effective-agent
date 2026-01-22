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
cd .github/skills/integration-test-env

# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run example (starts postgres and redis by default)
python skill.py

# Press Ctrl+C to stop and remove all containers
```

**Note**: Once the virtual environment is activated, use `python` and `pip` commands directly. They will automatically use the venv's Python interpreter.

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

- ✅ Automatic Docker image pulling if not available locally
- ✅ Handles container name conflicts (removes existing containers)
- ✅ Concurrent startup for fast initialization
- ✅ Health checks ensure services are ready
- ✅ Clean connection strings provided
- ✅ Proper cleanup on shutdown (stops AND removes containers)
- ✅ Graceful Ctrl+C handling with immediate container tracking
- ✅ Portable across environments (self-contained)

## Example

```python
from skill import IntegrationTestEnvironment

async def setup_tests():
    env = IntegrationTestEnvironment(name_prefix="myapp_test")
    
    # Start multiple services
    services = await env.start_services(["postgres", "redis"])
    
    # Get connection info
    db_connection = services["postgres"]["connection"]
    # postgresql://test:test@localhost:5432/testdb
    
    # Run your integration tests...
    
    # Cleanup (stops AND removes containers)
    await env.stop_all()
```

## How It Works

1. **Image Management**: Automatically pulls Docker images if they don't exist locally
2. **Conflict Resolution**: Removes any existing containers with the same name before creating new ones
3. **Immediate Tracking**: Containers are tracked as soon as they're created, ensuring proper cleanup even if interrupted during health checks
4. **Graceful Shutdown**: Pressing Ctrl+C triggers proper cleanup that stops and removes all containers
5. **No Orphans**: All containers are properly cleaned up, nothing left running in Docker Desktop

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
