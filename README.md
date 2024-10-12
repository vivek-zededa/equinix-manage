
# Equinix Metal VM Management Script

This Python script is designed to manage virtual machines (VMs) on Equinix Metal by interacting with the Equinix Metal API. It can retrieve VM information, calculate their cost, and delete VMs based on user-defined conditions. This script can be executed from Jenkins or from the command line, and it accepts parameters such as the project name and API token.

## Features

- Retrieve and list running and stopped VMs within a specified project.
- Calculate the total cost incurred by individual VMs.
- Optionally delete VMs, with support for skipping VMs that are tagged with `DO_NOT_DELETE`.
- Pass API token and project name as command-line parameters for flexibility.

## Requirements

- Python 3.x
- `requests` library

You can install the `requests` library by running:
```bash
pip install requests
```

## Usage

The script can be run directly from the command line or integrated into a Jenkins job. Here are the instructions for both use cases:

### Command-Line Usage

1. Clone or download the script.

2. Run the script with the following parameters:
   - `--token`: Your Equinix Metal API token.
   - `--project`: The name of the project you want to manage (e.g., `Zededa Test` or `Zededa Development`).

   Example:
   ```bash
   python manage_vms.py --token "your_api_token" --project "Zededa Test"
   ```

### Parameters

- `--token`: The API token for authenticating with Equinix Metal.
- `--project`: The name of the project where the VMs are hosted.

### Example

```bash
python manage_vms.py --token "qy2ugN8KaaD22ht9DtvDf2pCxYtx3oiL" --project "Zededa Test"
```

### Jenkins Integration

You can integrate this script into a Jenkins pipeline or freestyle job as follows:

1. Create a Jenkins job that executes shell commands.
2. Pass the required parameters (`--token`, `--project`) as Jenkins parameters.
3. Add the following command in your Jenkins job:
   ```bash
   python manage_vms.py --token "$API_TOKEN" --project "$PROJECT_NAME"
   ```

### Error Handling

- If an invalid project name is provided, the script will print an error message.
- If there is an issue with the API request (e.g., invalid token or API server issues), the script will print the appropriate error message and continue to the next operation.

## Functions

### `manage_equinix_vms(api_token, project_id, delete=True, skip_do_not_delete_tag=True)`

Fetch and manage Equinix VMs for a given project. Optionally, it can delete VMs based on the `delete` flag and can skip VMs tagged with `DO_NOT_DELETE`.

### `fetch_devices(api_token, project_id)`

Fetch all devices (VMs) for a given project.

### `fetch_equinix_vm_cost(api_token, project_id, vm_name)`

Fetch total cost incurred for a specific VM within the specified project.

### `delete_equinix_vm(api_token, vm_id)`

Delete a VM using its ID.

### `print_vm_info(vm, total_vm_cost)`

Print detailed information about a specific VM, including its name, state, owner, tags, and cost incurred.

## License

This script is distributed under the MIT License.
