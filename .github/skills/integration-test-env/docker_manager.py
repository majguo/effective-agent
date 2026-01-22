"""Docker container management utilities using async operations."""

import asyncio
import logging
from typing import Any, Dict, Optional

import aiodocker
from aiodocker.exceptions import DockerError

# Module constants
_STOP_TIMEOUT_BUFFER = 5  # Additional seconds to wait after stop command
_MAX_STATUS_CHECK_ITERATIONS = 200  # Maximum status check attempts

logger = logging.getLogger(__name__)


async def remove_container_if_exists(container_name: str) -> None:
    """
    Remove a container if it exists (regardless of state).

    Args:
        container_name: Name of the container to remove

    Raises:
        DockerError: If container removal fails
    """
    try:
        async with aiodocker.Docker() as docker:
            try:
                container = await docker.containers.get(container_name)
                logger.info("Removing existing container: %s", container_name)
                await container.delete(force=True)
                logger.info("Container removed: %s", container_name)
            except DockerError as e:
                if e.status == 404:
                    # Container doesn't exist, nothing to remove
                    pass
                else:
                    raise
    except Exception as e:
        logger.error("Error removing container '%s': %s", container_name, e)
        raise


async def start_docker_container(
    container_name_or_id: str, timeout: int = 30
) -> Dict[str, Any]:
    """
    Start a Docker container asynchronously.

    Args:
        container_name_or_id: Name or ID of the container to start
        timeout: Maximum time to wait for container to start (seconds)

    Returns:
        dict: Container information after starting, including status and configuration

    Raises:
        DockerError: If container cannot be found or started
        asyncio.TimeoutError: If container doesn't start within timeout period
    """
    try:
        async with aiodocker.Docker() as docker:
            logger.info("Attempting to start container: %s", container_name_or_id)

            # Get container reference
            container = await docker.containers.get(container_name_or_id)

            # Start the container
            await container.start()

            # Wait for container to be running
            await asyncio.wait_for(
                _wait_for_container_running(container), timeout=timeout
            )

            # Get updated container info
            info = await container.show()
            logger.info("Container started successfully: %s", info["Name"])

            return info

    except DockerError as e:
        logger.error(
            "Docker error starting container '%s': %s", container_name_or_id, e
        )
        raise
    except asyncio.TimeoutError:
        logger.error(
            "Container '%s' failed to start within %ss", container_name_or_id, timeout
        )
        raise
    except Exception as e:
        logger.error(
            "Unexpected error starting container '%s': %s", container_name_or_id, e
        )
        raise


async def stop_docker_container(
    container_name_or_id: str, timeout: int = 30
) -> Dict[str, Any]:
    """
    Stop a Docker container asynchronously.

    Args:
        container_name_or_id: Name or ID of the container to stop
        timeout: Maximum time to wait for container to stop (seconds)

    Returns:
        dict: Container information after stopping, including status

    Raises:
        DockerError: If container cannot be found or stopped
        asyncio.TimeoutError: If container doesn't stop within timeout period
    """
    try:
        async with aiodocker.Docker() as docker:
            logger.info("Attempting to stop container: %s", container_name_or_id)

            # Get container reference
            container = await docker.containers.get(container_name_or_id)

            # Stop the container
            await container.stop(timeout=timeout)

            # Wait for container to be stopped
            await asyncio.wait_for(
                _wait_for_container_stopped(container),
                timeout=timeout + _STOP_TIMEOUT_BUFFER,
            )

            # Get updated container info
            info = await container.show()
            logger.info("Container stopped successfully: %s", info["Name"])

            return info

    except DockerError as e:
        logger.error(
            "Docker error stopping container '%s': %s", container_name_or_id, e
        )
        raise
    except asyncio.TimeoutError:
        logger.error(
            "Container '%s' failed to stop within %ss", container_name_or_id, timeout
        )
        raise
    except Exception as e:
        logger.error(
            "Unexpected error stopping container '%s': %s", container_name_or_id, e
        )
        raise


async def _wait_for_container_running(container: Any, check_interval: float = 0.5) -> None:
    """
    Wait for container to reach running state.

    Args:
        container: Container object to monitor
        check_interval: Time between status checks (seconds)

    Raises:
        DockerError: If container enters terminal state or max iterations reached
    """
    iterations = 0
    while iterations < _MAX_STATUS_CHECK_ITERATIONS:
        info = await container.show()
        state = info["State"]["Status"]

        if state == "running":
            return
        elif state in ["exited", "dead"]:
            raise DockerError(500, f"Container entered {state} state")

        await asyncio.sleep(check_interval)
        iterations += 1

    raise DockerError(
        500, "Maximum status check iterations reached waiting for container to run"
    )


async def _wait_for_container_stopped(
    container: Any, check_interval: float = 0.5
) -> None:
    """
    Wait for container to reach stopped/exited state.

    Args:
        container: Container object to monitor
        check_interval: Time between status checks (seconds)

    Raises:
        DockerError: If max iterations reached
    """
    iterations = 0
    while iterations < _MAX_STATUS_CHECK_ITERATIONS:
        info = await container.show()
        state = info["State"]["Status"]

        if state in ["exited", "stopped"]:
            return

        await asyncio.sleep(check_interval)
        iterations += 1

    raise DockerError(
        500, "Maximum status check iterations reached waiting for container to stop"
    )


async def _pull_image_if_missing(docker: Any, image: str) -> None:
    """
    Pull Docker image if it doesn't exist locally.

    Args:
        docker: Docker client instance
        image: Image name to pull

    Raises:
        DockerError: If image pull fails
    """
    try:
        # Check if image exists locally
        await docker.images.inspect(image)
        logger.info("Image already exists locally: %s", image)
    except DockerError as e:
        if e.status == 404:
            # Image doesn't exist, pull it
            logger.info("Pulling image: %s", image)
            await docker.images.pull(image)
            logger.info("Image pulled successfully: %s", image)
        else:
            raise


async def create_and_start_container(
    image: str,
    name: Optional[str] = None,
    ports: Optional[Dict[str, int]] = None,
    environment: Optional[Dict[str, str]] = None,
    volumes: Optional[Dict[str, Dict[str, str]]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create and start a new Docker container from an image.

    Args:
        image: Docker image name (e.g., "nginx:latest", "python:3.11")
        name: Optional container name
        ports: Port mappings {container_port: host_port}, e.g., {"80/tcp": 8080}
        environment: Environment variables as key-value pairs
        volumes: Volume mappings {host_path: {"bind": container_path, "mode": "rw"}}
        **kwargs: Additional container configuration options

    Returns:
        dict: Created container information

    Raises:
        DockerError: If container creation or start fails

    Example:
        >>> info = await create_and_start_container(
        ...     image="nginx:latest",
        ...     name="my_nginx",
        ...     ports={"80/tcp": 8080}
        ... )
    """
    try:
        async with aiodocker.Docker() as docker:
            # Pull image if not available locally
            await _pull_image_if_missing(docker, image)
            
            logger.info("Creating container from image: %s", image)

            # Build container configuration
            config = {
                "Image": image,
                "AttachStdin": False,
                "AttachStdout": False,
                "AttachStderr": False,
                **kwargs,
            }

            # Add optional configurations
            if environment:
                config["Env"] = [f"{k}={v}" for k, v in environment.items()]

            if ports:
                config["ExposedPorts"] = {port: {} for port in ports.keys()}
                config["HostConfig"] = {
                    "PortBindings": {
                        port: [{"HostPort": str(host_port)}]
                        for port, host_port in ports.items()
                    }
                }

            if volumes:
                if "HostConfig" not in config:
                    config["HostConfig"] = {}
                config["HostConfig"]["Binds"] = [
                    f"{host_path}:{vol_config['bind']}:{vol_config.get('mode', 'rw')}"
                    for host_path, vol_config in volumes.items()
                ]

            # Create container
            container = await docker.containers.create(config=config, name=name)
            logger.info("Container created: %s", container.id[:12])

            # Start container
            await container.start()
            logger.info("Container started: %s", container.id[:12])

            # Get container info
            info = await container.show()
            return info

    except DockerError as e:
        logger.error("Docker error creating container from '%s': %s", image, e)
        raise
    except Exception as e:
        logger.error("Unexpected error creating container: %s", e)
        raise
