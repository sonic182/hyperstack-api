import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

from hyperstack import Hyperstack


def get_api_key_from_credentials():
    """Read API key from ~/.hyperstack/credentials file."""
    credentials_path = Path.home() / ".hyperstack" / "credentials"

    if not credentials_path.exists():
        return None

    try:
        with open(credentials_path, "r") as f:
            content = f.read()
            # Match a line that starts with "key =" followed by the key
            match = re.search(r"key\s*=\s*(.+)", content)
            if match:
                return match.group(1).strip()
    except Exception:
        return None

    return None


async def run_command(args: argparse.Namespace):
    """Run the selected Hyperstack command with provided arguments."""
    client = Hyperstack(api_key=args.api_key)

    if args.command == "create-environment":
        return await client.create_environment(name=args.name, region=args.region)

    elif args.command == "get-environment":
        return await client.get_environment(environment_id=args.environment_id)

    elif args.command == "list-environments":
        return await client.list_environments(
            search=args.search,
            page=args.page,
            page_size=args.page_size,
        )

    elif args.command == "update-environment":
        return await client.update_environment(
            environment_id=args.environment_id, new_name=args.new_name
        )

    elif args.command == "delete-environment":
        return await client.delete_environment(environment_id=args.environment_id)

    elif args.command == "create-keypair":
        # Read public key from file or argument
        public_key = args.public_key
        if args.public_key_file:
            with open(args.public_key_file, "r") as f:
                public_key = f.read().strip()

        return await client.create_keypair(
            name=args.name,
            environment_name=args.environment_name,
            public_key=public_key,
        )

    elif args.command == "get-flavors":
        return await client.get_flavors()

    elif args.command == "get-images":
        return await client.get_images()

    elif args.command == "get-gpu-stocks":
        return await client.get_gpu_stocks()

    elif args.command == "create-vm":
        return await client.create_virtual_machine(
            name=args.name,
            environment_name=args.environment_name,
            image_name=args.image_name,
            flavor_name=args.flavor_name,
            key_name=args.key_name,
            create_bootable_volume=args.create_bootable_volume,
            user_data=args.user_data,
            assign_floating_ip=args.assign_floating_ip,
            count=args.count,
        )

    # Added missing commands
    elif args.command == "list-vms":
        return await client.list_virtual_machines(
            search=args.search,
            environment=args.environment,
            page=args.page,
            page_size=args.page_size,
        )

    elif args.command == "get-vm":
        return await client.get_virtual_machine(vm_id=args.vm_id)

    elif args.command == "start-vm":
        return await client.start_virtual_machine(vm_id=args.vm_id)

    elif args.command == "stop-vm":
        return await client.stop_virtual_machine(vm_id=args.vm_id)

    elif args.command == "reboot-vm":
        return await client.hard_reboot_virtual_machine(vm_id=args.vm_id)

    elif args.command == "hibernate-vm":
        return await client.hibernate_virtual_machine(vm_id=args.vm_id)

    elif args.command == "restore-vm":
        return await client.restore_hibernated_virtual_machine(vm_id=args.vm_id)

    elif args.command == "delete-vm":
        return await client.delete_virtual_machine(vm_id=args.vm_id)


def main():
    parser = argparse.ArgumentParser(
        description="Command-line interface for Hyperstack API"
    )
    parser.add_argument(
        "--api-key",
        help="Hyperstack API key (defaults to HYPERSTACK_KEY env variable or ~/.hyperstack/credentials)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "pretty"],
        default="pretty",
        help="Output format (json or pretty formatted)",
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Hyperstack command to run", required=True
    )

    # Create environment command
    env_parser = subparsers.add_parser(
        "create-environment", help="Create a new environment"
    )
    env_parser.add_argument("--name", required=True, help="Name for the environment")
    env_parser.add_argument(
        "--region",
        required=True,
        choices=["CANADA-1", "NORWAY-1"],
        help="Region where the environment will be created",
    )

    # Get environment command
    get_env_parser = subparsers.add_parser(
        "get-environment", help="Fetch details of a specific environment"
    )
    get_env_parser.add_argument(
        "--environment-id", required=True, help="The ID of the environment to retrieve"
    )

    # List environments command
    list_env_parser = subparsers.add_parser(
        "list-environments", help="Fetch a list of environments"
    )
    list_env_parser.add_argument(
        "--search", help="Search for environments by name, ID, or region"
    )
    list_env_parser.add_argument("--page", type=int, help="Page number to retrieve")
    list_env_parser.add_argument(
        "--page-size", type=int, help="Number of environments per page"
    )

    # Update environment command
    update_env_parser = subparsers.add_parser(
        "update-environment", help="Update an existing environment"
    )
    update_env_parser.add_argument(
        "--environment-id", required=True, help="The ID of the environment to update"
    )
    update_env_parser.add_argument(
        "--new-name", required=True, help="New name for the environment"
    )

    # Delete environment command
    delete_env_parser = subparsers.add_parser(
        "delete-environment", help="Permanently delete an environment"
    )
    delete_env_parser.add_argument(
        "--environment-id", required=True, help="The ID of the environment to delete"
    )

    # Create keypair command
    keypair_parser = subparsers.add_parser(
        "create-keypair", help="Create a new keypair"
    )
    keypair_parser.add_argument("--name", required=True, help="Name for the keypair")
    keypair_parser.add_argument(
        "--environment-name", required=True, help="Name of the environment"
    )
    keypair_parser.add_argument("--public-key", help="SSH public key in OpenSSH format")
    keypair_parser.add_argument(
        "--public-key-file", help="File containing SSH public key"
    )

    # Get flavors command
    subparsers.add_parser("get-flavors", help="Fetch available instance flavors")

    # Get images command
    subparsers.add_parser("get-images", help="Fetch available system images")

    # Get GPU stocks command
    subparsers.add_parser(
        "get-gpu-stocks",
        help="Fetch information on current and upcoming GPU availability",
    )

    # Create VM command
    vm_parser = subparsers.add_parser("create-vm", help="Create a new virtual machine")
    vm_parser.add_argument("--name", required=True, help="Name for the virtual machine")
    vm_parser.add_argument(
        "--environment-name", required=True, help="Name of the environment"
    )
    vm_parser.add_argument(
        "--image-name", required=True, help="Name of the image to use"
    )
    vm_parser.add_argument(
        "--flavor-name", required=True, help="Name of the flavor to use"
    )
    vm_parser.add_argument(
        "--key-name", required=True, help="Name of the keypair to use"
    )
    vm_parser.add_argument(
        "--create-bootable-volume", action="store_true", help="Create a bootable volume"
    )
    vm_parser.add_argument("--user-data", default="", help="User data for cloud-init")
    vm_parser.add_argument(
        "--user-data-file", help="File containing user data for cloud-init"
    )
    vm_parser.add_argument(
        "--assign-floating-ip",
        action="store_true",
        default=True,
        help="Assign a floating IP",
    )
    vm_parser.add_argument(
        "--count", type=int, default=1, help="Number of instances to create"
    )

    # List Virtual Machines command
    list_vms_parser = subparsers.add_parser(
        "list-vms", help="Fetch a list of virtual machines"
    )
    list_vms_parser.add_argument(
        "--search", help="Search for virtual machines by name or ID"
    )
    list_vms_parser.add_argument(
        "--environment", help="Filter by environment name or ID"
    )
    list_vms_parser.add_argument("--page", type=int, help="Page number to retrieve")
    list_vms_parser.add_argument(
        "--page-size", type=int, help="Number of virtual machines per page"
    )

    # Get VM details command
    get_vm_parser = subparsers.add_parser(
        "get-vm", help="Fetch details of a specific virtual machine"
    )
    get_vm_parser.add_argument(
        "--vm-id", required=True, help="The ID of the virtual machine"
    )

    # Start VM command
    start_vm_parser = subparsers.add_parser("start-vm", help="Start a virtual machine")
    start_vm_parser.add_argument(
        "--vm-id", required=True, help="The ID of the virtual machine to start"
    )

    # Stop VM command
    stop_vm_parser = subparsers.add_parser(
        "stop-vm", help="Stop (shut down) a virtual machine"
    )
    stop_vm_parser.add_argument(
        "--vm-id", required=True, help="The ID of the virtual machine to stop"
    )

    # Reboot VM command
    reboot_vm_parser = subparsers.add_parser(
        "reboot-vm", help="Hard-reboot a virtual machine"
    )
    reboot_vm_parser.add_argument(
        "--vm-id", required=True, help="The ID of the virtual machine to reboot"
    )

    # Hibernate VM command
    hibernate_vm_parser = subparsers.add_parser(
        "hibernate-vm", help="Hibernate a virtual machine"
    )
    hibernate_vm_parser.add_argument(
        "--vm-id", required=True, help="The ID of the virtual machine to hibernate"
    )

    # Restore hibernated VM command
    restore_vm_parser = subparsers.add_parser(
        "restore-vm", help="Restore a virtual machine from hibernation"
    )
    restore_vm_parser.add_argument(
        "--vm-id",
        required=True,
        help="The ID of the hibernated virtual machine to restore",
    )

    # Delete VM command
    delete_vm_parser = subparsers.add_parser(
        "delete-vm", help="Permanently delete a virtual machine"
    )
    delete_vm_parser.add_argument(
        "--vm-id", required=True, help="The ID of the virtual machine to delete"
    )

    args = parser.parse_args()

    # Set API key from environment or credentials file if not provided via CLI
    if not args.api_key:
        args.api_key = os.environ.get("HYPERSTACK_KEY")
        if not args.api_key:
            args.api_key = get_api_key_from_credentials()
            if not args.api_key:
                parser.error(
                    "API key not found. Please provide it via --api-key, "
                    "HYPERSTACK_KEY environment variable, or ~/.hyperstack/credentials file."
                )

    # Load user-data from file if specified
    if hasattr(args, "user_data_file") and args.user_data_file:
        with open(args.user_data_file, "r") as f:
            args.user_data = f.read()

    # Validate keypair args
    if args.command == "create-keypair" and not (
        args.public_key or args.public_key_file
    ):
        parser.error("create-keypair requires either --public-key or --public-key-file")

    try:
        result = asyncio.run(run_command(args))

        if args.format == "json":
            print(json.dumps(result))
        else:
            print(json.dumps(result, indent=2))

    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
