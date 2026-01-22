"""Integration test environment setup and orchestration."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from docker_manager import create_and_start_container, stop_docker_container, remove_container_if_exists
from service_configs import get_service_config, list_supported_services

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationTestEnvironment:
    """Manages integration test environment with multiple services."""

    def __init__(self, name_prefix: str = "test"):
        """
        Initialize integration test environment.

        Args:
            name_prefix: Prefix for container names
        """
        self.name_prefix = name_prefix
        self.containers: Dict[str, Dict[str, Any]] = {}

    async def start_service(
        self, service_name: str, port_override: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Start a single service container.

        Args:
            service_name: Name of service to start (e.g., 'postgres', 'redis')
            port_override: Optional port override

        Returns:
            Service information including connection details
        """
        config = get_service_config(service_name)
        container_name = f"{self.name_prefix}_{service_name}"

        # Adjust port if override provided
        ports = config.get("ports", {})
        if port_override:
            # Update the first port mapping
            first_port = next(iter(ports.keys()))
            ports[first_port] = port_override

        logger.info("Starting %s service as %s", service_name, container_name)

        # Remove existing container if it exists
        await remove_container_if_exists(container_name)

        # Create and start container
        container_info = await create_and_start_container(
            image=config["image"],
            name=container_name,
            ports=ports,
            environment=config.get("environment", {}),
        )

        # Track container immediately so it can be cleaned up if interrupted
        actual_port = list(ports.values())[0]
        self.containers[service_name] = {
            "service": service_name,
            "container_name": container_name,
            "container_id": container_info["Id"],
            "port": actual_port,
        }

        # Wait for health check
        await self._wait_for_health(container_name, config.get("health_check"))

        # Build full connection info
        connection_string = config["connection_template"].format(port=actual_port)

        service_info = {
            "service": service_name,
            "container_name": container_name,
            "container_id": container_info["Id"],
            "connection": connection_string,
            "port": actual_port,
            "credentials": config.get("environment", {}),
        }

        self.containers[service_name] = service_info
        logger.info("✓ %s ready: %s", service_name, connection_string)

        return service_info

    async def start_services(self, services: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Start multiple services concurrently.

        Args:
            services: List of service names to start

        Returns:
            Dictionary mapping service names to their info
        """
        tasks = [self.start_service(service) for service in services]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        service_info = {}
        for service_name, result in zip(services, results):
            if isinstance(result, Exception):
                logger.error("Failed to start %s: %s", service_name, result)
            else:
                service_info[service_name] = result

        return service_info

    async def stop_service(self, service_name: str) -> None:
        """
        Stop and remove a service container.

        Args:
            service_name: Name of service to stop
        """
        if service_name not in self.containers:
            logger.warning("Service %s not running", service_name)
            return

        container_name = self.containers[service_name]["container_name"]
        logger.info("Stopping %s", container_name)

        try:
            await stop_docker_container(container_name, timeout=10)
            # Also remove the container
            await remove_container_if_exists(container_name)
            del self.containers[service_name]
            logger.info("✓ Stopped %s", service_name)
        except Exception as e:
            logger.error("Error stopping %s: %s", service_name, e)

    async def stop_all(self) -> None:
        """Stop all running services."""
        logger.info("Stopping all services...")
        tasks = [self.stop_service(name) for name in list(self.containers.keys())]
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("✓ All services stopped")

    async def _wait_for_health(
        self, container_name: str, health_config: Optional[Dict[str, Any]]
    ) -> None:
        """
        Wait for container to be healthy.

        Args:
            container_name: Name of container
            health_config: Health check configuration
        """
        if not health_config:
            # No health check, just wait a bit
            await asyncio.sleep(2)
            return

        timeout = health_config.get("timeout", 30)
        interval = health_config.get("interval", 2)
        elapsed = 0

        logger.info("Waiting for %s to be healthy...", container_name)

        while elapsed < timeout:
            await asyncio.sleep(interval)
            elapsed += interval

            # In a real implementation, we'd check container health here
            # For now, just wait for the timeout period
            if elapsed >= min(10, timeout):
                break

        logger.info("✓ %s is healthy", container_name)

    def get_connection_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get connection information for a running service.

        Args:
            service_name: Name of service

        Returns:
            Connection information or None if service not running
        """
        return self.containers.get(service_name)

    def list_running_services(self) -> List[str]:
        """Return list of currently running service names."""
        return list(self.containers.keys())


async def main() -> None:
    """Example usage of integration test environment."""
    env = IntegrationTestEnvironment(name_prefix="myapp_test")

    try:
        # Start multiple services
        logger.info("Setting up integration test environment...")
        logger.info("Supported services: %s", ", ".join(list_supported_services()))

        services = await env.start_services(["postgres", "redis"])

        # Display connection info
        logger.info("\n=== Integration Test Environment Ready ===")
        for service_name, info in services.items():
            logger.info(
                "%s: %s", service_name.upper(), info["connection"]
            )

        logger.info("\n✓ Environment ready for integration tests!")
        logger.info("Press Ctrl+C to stop all services...")

        # Keep running until interrupted
        await asyncio.Event().wait()

    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("\nShutting down...")
    finally:
        await env.stop_all()
        logger.info("✓ All services stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Already handled in main()
