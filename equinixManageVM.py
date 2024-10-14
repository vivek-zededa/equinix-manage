import requests
import argparse

# Constants
API_TOKEN = 'your_api_token'  # Replace with your Equinix Metal API token
BASE_URL = 'https://api.equinix.com/metal/v1'


# Mapping of project names to their IDs
PROJECTS_INFO_DICT = {
    'Zededa Test': 'e6df9343-8781-4f27-b942-8f9675d5e0e7',
    'Zededa Development': 'ce48ed95-821d-4f9e-89d5-330f7ee52ba4'
}

def fetch_devices(api_token, project_id):
    """
    Fetch all devices (VMs) for a given project.

    Parameters:
        api_token (str): The API token for Equinix Metal.
        project_id (str): The ID of the project.

    Returns:
        list: A list of devices for the project.
    """
    url = f"{BASE_URL}/projects/{project_id}/devices"
    
    headers = {
        'X-Auth-Token': api_token,
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('devices', [])
    else:
        print(f"Error fetching VMs: {response.status_code} - {response.text}")
        return []


def fetch_equinix_vm_cost(api_token, project_id, vm_name):
    """
    Fetch total cost incurred for a specific VM.

    Parameters:
        project_id (str): The ID of the project.
        vm_name (str): The name of the VM.

    Returns:
        float: Total cost incurred for the VM.
    """
    url = f"{BASE_URL}/projects/{project_id}/usages"

    headers = {
        'X-Auth-Token': api_token,
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        usage_data = response.json()
        return sum(usage['total'] for usage in usage_data['usages'] if usage['name'] == vm_name)
    else:
        print(f"Error fetching usage data: {response.status_code} - {response.text}")
        return 0.0


def delete_equinix_vm(api_token, vm_id):
    """
    Delete a VM using its ID.

    Parameters:
        vm_id (str): The ID of the VM to delete.
    """
    url = f"{BASE_URL}/devices/{vm_id}"

    headers = {
        'X-Auth-Token': api_token,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            print(f"VM with ID {vm_id} successfully deleted.")
        elif response.status_code == 404:
            print(f"VM with ID {vm_id} not found.")
        else:
            print(f"Failed to delete VM with ID {vm_id}. Status Code: {response.status_code}, Error: {response.text}")

    except Exception as e:
        print(f"An error occurred during deletion: {str(e)}")

def print_vms_info(vms_info):
    """
    Print information about multiple VMs in a single table.

    Parameters:
        vms_info (list): A list of tuples containing VM information and their total cost.
    """
    # Define headers
    headers = ["VM Name", "VM ID", "Current State", "Owner", "Tags", "Total Cost ($)"]
    print("\n\n")

    # Ensure there are VMs to display
    if not vms_info:
        print("No VMs to display.")
        return

    # Calculate max width for each column
    col_widths = [len(header) for header in headers]
    for vm, _ in vms_info:
        col_widths[0] = max(col_widths[0], len(vm.get('hostname', 'N/A')))
        col_widths[1] = max(col_widths[1], len(vm.get('id', 'N/A')))
        col_widths[2] = max(col_widths[2], len(vm.get('state', 'N/A')))
        col_widths[3] = max(col_widths[3], len(vm['created_by'].get('full_name', 'Unknown Owner')))
        col_widths[4] = max(col_widths[4], len(', '.join(vm.get('tags', [])) or ['No tags']))

    # Print table headers
    header_row = " | ".join(f"{header:<{col_widths[i]}}" for i, header in enumerate(headers))
    print(header_row)
    print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))  # Adjusting line length for separators

    # Print table rows
    for vm, total_vm_cost in vms_info:
        row = [
            vm.get('hostname', 'N/A'),
            vm.get('id', 'N/A'),
            vm.get('state', 'N/A'),
            vm['created_by'].get('full_name', 'Unknown Owner'),
            ', '.join(vm.get('tags', [])) if vm.get('tags') else 'No tags',
            f"{total_vm_cost:.2f}"
        ]
        print(" | ".join(f"{str(item):<{col_widths[i]}}" for i, item in enumerate(row)))

    print("\n\n")


def should_delete_vm(vm, skip_do_not_delete_tag):
    """
    Determine if a VM should be deleted based on tags.

    Parameters:
        vm (dict): The VM information.
        skip_do_not_delete_tag (bool): Flag to skip deletion if 'DO_NOT_DELETE' tag is present.

    Returns:
        bool: True if the VM should be deleted, False otherwise.
    """
    if skip_do_not_delete_tag and 'DO_NOT_DELETE' in vm['tags']:
        print(f"Skipping deletion of VM {vm['hostname']} (ID: {vm['id']}) due to 'DO_NOT_DELETE' tag.")
        return False
    return True


def manage_equinix_vms(api_token, project_id, delete=False, skip_do_not_delete_tags=True):
    """
    Fetch and manage Equinix VMs for a given project.

    Parameters:
        project_id (str): The ID of the project.
        delete (bool): Flag to indicate whether to delete VMs.
        skip_do_not_delete_tag (bool): Flag to skip deletion of tagged VMs.
    """
    devices = fetch_devices(api_token, project_id)

    if devices:
        # List to collect VM info along with their total cost for table printing
        vms_info_list = []

        # Process each VM and collect info
        for vm in devices:
            total_vm_cost = fetch_equinix_vm_cost(api_token, project_id, vm['hostname'])
            vms_info_list.append((vm, total_vm_cost))

        # Print all VM details in a table
        print_vms_info(vms_info_list)

        # Handle deletion based on the delete flag and 'DO_NOT_DELETE' tag
        if delete:
            for vm, total_vm_cost in vms_info_list:
                if should_delete_vm(vm, skip_do_not_delete_tags):
                    delete_equinix_vm(api_token, vm['id'])
    else:
        print(f"No devices found for project ID {project_id}.")


def main(api_token, project_name, delete, skip_do_not_delete_tags):
    """
    Main function to manage VMs based on project name and API token passed as arguments.

    Parameters:
        api_token (str): The API token for Equinix Metal.
        project_name (str): The name of the project to manage VMs.
    """
    project_id = PROJECTS_INFO_DICT.get(project_name)
    if project_id:
        manage_equinix_vms(api_token, project_id, delete=delete, skip_do_not_delete_tags=skip_do_not_delete_tags)
    else:
        print(f"Project name '{project_name}' not found. Please check the project name.")


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Manage Equinix VMs.')
    parser.add_argument('--token', required=True, help='The API token for Equinix Metal.')
    parser.add_argument('--project', required=True, help='The name of the project to manage VMs.')
    parser.add_argument('--delete', action='store_true', help='Set this flag to delete VMs.')
    parser.add_argument('--skip-do-not-delete-tags', action='store_true',
                        help='Set this flag to skip deletion for VMs with the DO_NOT_DELETE tag.')

    args = parser.parse_args()
    main(args.token, args.project, args.delete, args.skip_do_not_delete_tags)
