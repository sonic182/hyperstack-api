
# Hyperstack CLI

A command-line interface for interacting with the Hyperstack API to manage cloud environments and resources.

This is very incomplete api client, not published to pip. See official client instead -> https://github.com/NexGenCloud/hyperstack-sdk-python

## Installation

```bash
pip install hyperstack
```

## Authentication

The CLI requires an API key to authenticate with Hyperstack. You can provide it in one of three ways:

1. Using the `--api-key` command line argument
2. Setting the `HYPERSTACK_KEY` environment variable
3. Creating a credentials file at `~/.hyperstack/credentials` with the format:
   ```
   key = your_api_key_here
   ```

## Usage

```bash
hyperstack [--api-key API_KEY] [--format {json,pretty}] COMMAND [OPTIONS]
```

### Global Arguments

- `--api-key`: Your Hyperstack API key
- `--format`: Output format (`json` or `pretty`). Default is `pretty`.

### Available Commands

#### Environment Management

- `create-environment`: Create a new environment
- `get-environment`: Get details of a specific environment
- `list-environments`: List all environments
- `update-environment`: Update an existing environment
- `delete-environment`: Delete an environment

#### Keypair Operations

- `create-keypair`: Create a new SSH keypair

#### Resource Information

- `get-flavors`: List available instance flavors
- `get-images`: List available system images
- `get-gpu-stocks`: Get information on GPU availability

#### Virtual Machine Operations

- `create-vm`: Create a new virtual machine
- `list-vms`: List all virtual machines
- `get-vm`: Get details of a specific virtual machine
- `start-vm`: Start a virtual machine
- `stop-vm`: Stop a virtual machine
- `reboot-vm`: Hard reboot a virtual machine
- `hibernate-vm`: Hibernate a virtual machine
- `restore-vm`: Restore a hibernated virtual machine
- `delete-vm`: Delete a virtual machine

## Examples

### Create a new environment

```bash
hyperstack create-environment --name "my-environment" --region "CANADA-1"
```

### Create a virtual machine (CPU instance)

```bash
hyperstack create-vm \
  --name "my-cpu-vm" \
  --environment-name "my-environment" \
  --image-name "Ubuntu Server 22.04 LTS R550 CUDA 12.4 with Docker" \
  --flavor-name "n3-RTX-A4000x1" \
  --key-name "my-ssh-key-name" \
  --assign-floating-ip
```

### List all virtual machines in an environment

```bash
hyperstack list-vms --environment "my-environment"
```

### Get GPU availability information

```bash
hyperstack get-gpu-stocks
```

## License

MIT
