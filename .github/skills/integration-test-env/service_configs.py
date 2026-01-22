"""Predefined service configurations for integration testing."""

from typing import Any, Dict

# Service configurations with Docker images and settings
SERVICE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "postgres": {
        "image": "postgres:15-alpine",
        "environment": {
            "POSTGRES_USER": "test",
            "POSTGRES_PASSWORD": "test",
            "POSTGRES_DB": "testdb",
        },
        "ports": {"5432/tcp": 5432},
        "health_check": {
            "test": ["CMD-SHELL", "pg_isready -U test"],
            "interval": 2,
            "timeout": 30,
        },
        "connection_template": "postgresql://test:test@localhost:{port}/testdb",
    },
    "mysql": {
        "image": "mysql:8.0",
        "environment": {
            "MYSQL_ROOT_PASSWORD": "test",
            "MYSQL_DATABASE": "testdb",
            "MYSQL_USER": "test",
            "MYSQL_PASSWORD": "test",
        },
        "ports": {"3306/tcp": 3306},
        "health_check": {
            "test": ["CMD", "mysqladmin", "ping", "-h", "localhost"],
            "interval": 2,
            "timeout": 30,
        },
        "connection_template": "mysql://test:test@localhost:{port}/testdb",
    },
    "mongodb": {
        "image": "mongo:7",
        "environment": {
            "MONGO_INITDB_ROOT_USERNAME": "test",
            "MONGO_INITDB_ROOT_PASSWORD": "test",
        },
        "ports": {"27017/tcp": 27017},
        "health_check": {
            "test": ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"],
            "interval": 2,
            "timeout": 30,
        },
        "connection_template": "mongodb://test:test@localhost:{port}/",
    },
    "redis": {
        "image": "redis:7-alpine",
        "ports": {"6379/tcp": 6379},
        "health_check": {
            "test": ["CMD", "redis-cli", "ping"],
            "interval": 1,
            "timeout": 10,
        },
        "connection_template": "redis://localhost:{port}",
    },
    "rabbitmq": {
        "image": "rabbitmq:3-management-alpine",
        "environment": {
            "RABBITMQ_DEFAULT_USER": "test",
            "RABBITMQ_DEFAULT_PASS": "test",
        },
        "ports": {"5672/tcp": 5672, "15672/tcp": 15672},
        "health_check": {
            "test": ["CMD", "rabbitmq-diagnostics", "ping"],
            "interval": 2,
            "timeout": 30,
        },
        "connection_template": "amqp://test:test@localhost:{port}/",
    },
    "elasticsearch": {
        "image": "elasticsearch:8.11.0",
        "environment": {
            "discovery.type": "single-node",
            "xpack.security.enabled": "false",
            "ES_JAVA_OPTS": "-Xms512m -Xmx512m",
        },
        "ports": {"9200/tcp": 9200},
        "health_check": {
            "test": ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health"],
            "interval": 5,
            "timeout": 60,
        },
        "connection_template": "http://localhost:{port}",
    },
    "minio": {
        "image": "minio/minio:latest",
        "environment": {
            "MINIO_ROOT_USER": "test",
            "MINIO_ROOT_PASSWORD": "testtest",
        },
        "ports": {"9000/tcp": 9000, "9001/tcp": 9001},
        "command": ["server", "/data", "--console-address", ":9001"],
        "health_check": {
            "test": ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"],
            "interval": 5,
            "timeout": 30,
        },
        "connection_template": "http://localhost:{port}",
    },
}


def get_service_config(service_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific service.

    Args:
        service_name: Name of the service (e.g., 'postgres', 'redis')

    Returns:
        Service configuration dictionary

    Raises:
        ValueError: If service is not supported
    """
    if service_name not in SERVICE_CONFIGS:
        supported = ", ".join(SERVICE_CONFIGS.keys())
        raise ValueError(
            f"Service '{service_name}' not supported. Supported: {supported}"
        )

    return SERVICE_CONFIGS[service_name].copy()


def list_supported_services() -> list[str]:
    """Return list of all supported service names."""
    return list(SERVICE_CONFIGS.keys())
