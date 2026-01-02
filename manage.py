#!/usr/bin/env python3
"""
Home Finance Manager - Microservices Management Script

Usage:
    ./manage.py start [service]     - Start all services or specific service
    ./manage.py stop [service]      - Stop all services or specific service
    ./manage.py restart [service]   - Restart all services or specific service
    ./manage.py status              - Show status of all services
    ./manage.py logs [service]      - Show logs for all services or specific service
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Service configuration
SERVICES = [
    "transaction-management",
    "user-account-management",
    "user-notification",
    "budget-analysis",
    "api-gateway"
]

SERVICE_PORTS = {
    "transaction-management": {"app": 8100, "db": 5434},
    "user-account-management": {"app": 8200, "db": 5435},
    "user-notification": {"app": 8300, "db": 5436},
    "budget-analysis": {"app": 8400, "db": 5433},
    "api-gateway": {"app": 8000}
}

NETWORK_NAME = "hfm-network"
PROJECT_ROOT = Path(__file__).parent


def run_command(cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Execute shell command"""
    try:
        return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def ensure_network():
    """Create Docker network if it doesn't exist"""
    print(f"Ensuring network '{NETWORK_NAME}' exists...")
    result = run_command(
        ["docker", "network", "inspect", NETWORK_NAME],
        check=False
    )

    if result.returncode != 0:
        print(f"Creating network '{NETWORK_NAME}'...")
        run_command(["docker", "network", "create", NETWORK_NAME])
        print("Network created!")
    else:
        print("Network already exists.")


def start_service(service: str):
    """Start a specific service"""
    service_path = PROJECT_ROOT / "services" / service

    if not service_path.exists():
        print(f"Error: Service '{service}' not found at {service_path}")
        sys.exit(1)

    print(f"\nStarting {service}...")
    # Build with full output, then start
    print(f"Building {service} with detailed output...")
    subprocess.run(["docker", "compose", "--progress", "plain", "build"], cwd=service_path)
    run_command(["docker-compose", "up", "-d"], cwd=service_path)
    print(f"{service} started!")


def stop_service(service: str):
    """Stop a specific service"""
    service_path = PROJECT_ROOT / "services" / service

    if not service_path.exists():
        print(f"Error: Service '{service}' not found at {service_path}")
        sys.exit(1)

    print(f"\nStopping {service}...")
    run_command(["docker-compose", "down"], cwd=service_path)
    print(f"{service} stopped!")


def start_all():
    """Start all services"""
    ensure_network()
    print("\nStarting all services...\n")

    for service in SERVICES:
        start_service(service)

    print("\n" + "="*50)
    print("All services started!")
    print("="*50)
    print("\nServices running on:")
    for service, ports in SERVICE_PORTS.items():
        app_port = ports.get("app")
        print(f"  - {service:30} http://localhost:{app_port}")

    print("\nDatabases running on:")
    for service, ports in SERVICE_PORTS.items():
        db_port = ports.get("db")
        if db_port:
            print(f"  - {service:30} localhost:{db_port}")

    print("\nUse './manage.py logs [service]' to view logs")
    print("Use './manage.py stop' to stop all services")


def stop_all():
    """Stop all services"""
    print("\nStopping all services...\n")

    # Stop in reverse order
    for service in reversed(SERVICES):
        stop_service(service)

    print("\n" + "="*50)
    print("All services stopped!")
    print("="*50)
    print(f"\nTo remove the network, run: docker network rm {NETWORK_NAME}")


def restart_service(service: str):
    """Restart a specific service"""
    stop_service(service)
    start_service(service)


def restart_all():
    """Restart all services"""
    stop_all()
    start_all()


def show_status():
    """Show status of all services"""
    print("\nService Status:")
    print("="*80)

    result = run_command(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"])
    print(result.stdout)


def show_logs(service: Optional[str] = None, follow: bool = False):
    """Show logs for service(s)"""
    if service:
        service_path = PROJECT_ROOT / "services" / service
        if not service_path.exists():
            print(f"Error: Service '{service}' not found")
            sys.exit(1)

        cmd = ["docker-compose", "logs"]
        if follow:
            cmd.append("-f")

        print(f"\nShowing logs for {service}...\n")
        subprocess.run(cmd, cwd=service_path)
    else:
        print("\nShowing logs for all services...\n")
        for svc in SERVICES:
            print(f"\n{'='*80}")
            print(f"Logs for {svc}")
            print(f"{'='*80}\n")
            service_path = PROJECT_ROOT / "services" / svc
            run_command(["docker-compose", "logs", "--tail=20"], cwd=service_path, check=False)


def print_usage():
    """Print usage information"""
    print(__doc__)
    print("\nAvailable services:")
    for service in SERVICES:
        print(f"  - {service}")


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]
    service = sys.argv[2] if len(sys.argv) > 2 else None

    # Validate service if provided
    if service and service not in SERVICES and command != "help":
        print(f"Error: Unknown service '{service}'")
        print(f"\nAvailable services: {', '.join(SERVICES)}")
        sys.exit(1)

    if command == "start":
        if service:
            ensure_network()
            start_service(service)
        else:
            start_all()

    elif command == "stop":
        if service:
            stop_service(service)
        else:
            stop_all()

    elif command == "restart":
        if service:
            restart_service(service)
        else:
            restart_all()

    elif command == "status":
        show_status()

    elif command == "logs":
        follow = "--follow" in sys.argv or "-f" in sys.argv
        show_logs(service, follow=follow)

    elif command == "help":
        print_usage()

    else:
        print(f"Error: Unknown command '{command}'")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
