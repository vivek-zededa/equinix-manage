import requests
import argparse

# Constants
BASE_URL = 'https://api.equinix.com/metal/v1'

# Mapping of project names to their IDs
PROJECTS_INFO_DICT = {
    'Zededa Test': 'e6df9343-8781-4f27-b942-8f9675d5e0e7',
    'Zededa Development': 'ce48ed95-821d-4f9e-89d5-330f7ee52ba4'
}

def manage_equinix_vms(api_token, project_id, delete=True, skip_do_not_delete_tag=True):
    """
    Fetch and manage Equinix VMs for a given project.

    Parameters:
        api_token (str): The API token for Equinix Metal.
        project_id (str): The ID of the project.
        delete (bool): Flag to indicate whether to delete VMs.
        skip_do_not_delete_tag (bool): Flag to skip deletion of tagged VMs.
    """
    devices = fetch_devices(api_token, project_id)

    if not devices:
        print(f"No devices found for project ID {project_id}.")
        return

    running_vms = [device for device in devices if device['state'] in ['active', 'inactive']]
    print(f"\nFound {len(running_vms)} VMs in project {project_id} (states: running|stopped)")

    for vm in running_vms:
        total_vm_cost = fetch_equinix_vm_cost(api_token, project_id, vm['hostname'])
        print_vm_info(vm, total_vm_cost)

        if delete and should_delete_vm(vm, skip_do_not_delete_tag):
            delete_equinix_vm(api_token, vm['id'])


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
        api_token (str): The API token for Equinix Metal.
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
        api_token (str): The API token for Equinix Metal.
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


def print_vm_info(vm, total_vm_cost):
    """
    Print information about a VM.

    Parameters:
        vm (dict): The VM information.
        total_vm_cost (float): Total cost incurred for the VM.
    """
    print(f"VM Name: {vm['hostname']}, VM ID: {vm['id']}, Current State: {vm['state']}, "
          f"Owner: {vm['created_by']['full_name']}, Tags: {vm['tags']}, Total Cost Incurred: ${total_vm_cost:.2f}")


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


def main(api_token, project_name):
    """
    Main function to manage VMs based on project name and API token passed as arguments.

    Parameters:
        api_token (str): The API token for Equinix Metal.
        project_name (str): The name of the project to manage VMs.
    """
    project_id = PROJECTS_INFO_DICT.get(project_name)
    if project_id:
        manage_equinix_vms(api_token, project_id)
    else:
        print(f"Project name '{project_name}' not found. Please check the project name.")


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Manage Equinix VMs.')
    parser.add_argument('--token', required=True, help='The API token for Equinix Metal.')
    parser.add_argument('--project', required=True, help='The name of the project to manage VMs.')

    args = parser.parse_args()
    main(args.token, args.project)
