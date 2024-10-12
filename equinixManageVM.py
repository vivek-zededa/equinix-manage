import requests

# Constants
API_TOKEN = 'qy2ugN8KaaD22ht9DtvDf2pCxYtx3oiL'  # Replace with your Equinix Metal API token
BASE_URL = 'https://api.equinix.com/metal/v1'

# Set the headers for the API request, including the Authorization token
HEADERS = {
    'X-Auth-Token': API_TOKEN,
    'Content-Type': 'application/json'
}


def manage_equinix_vms(project_info, delete=True, skip_do_not_delete_tag=True):
    """
    Fetch and manage Equinix VMs for given projects.

    Parameters:
        project_info (dict): Dictionary of project names and their IDs.
        delete (bool): Flag to indicate whether to delete VMs.
        skip_do_not_delete_tag (bool): Flag to skip deletion of tagged VMs.
    """
    for project_id in project_info.values():
        devices = fetch_devices(project_id)

        if devices:
            running_vms = [device for device in devices if device['state'] in ['active', 'inactive']]
            print(f"\nFound {len(running_vms)} VMs in project {project_id} (states: running|stopped)")
            for vm in running_vms:
                total_vm_cost = fetch_equinix_vm_cost(project_id, vm['hostname'])
                print_vm_info(vm, total_vm_cost)

                if delete and should_delete_vm(vm, skip_do_not_delete_tag):
                    delete_equinix_vm(vm['id'])
        else:
            print(f"No devices found for project ID {project_id}.")


def fetch_devices(project_id):
    """
    Fetch all devices (VMs) for a given project.

    Parameters:
        project_id (str): The ID of the project.

    Returns:
        list: A list of devices for the project.
    """
    url = f"{BASE_URL}/projects/{project_id}/devices"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get('devices', [])
    else:
        print(f"Error fetching VMs: {response.status_code} - {response.text}")
        return []


def fetch_equinix_vm_cost(project_id, vm_name):
    """
    Fetch total cost incurred for a specific VM.

    Parameters:
        project_id (str): The ID of the project.
        vm_name (str): The name of the VM.

    Returns:
        float: Total cost incurred for the VM.
    """
    url = f"{BASE_URL}/projects/{project_id}/usages"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        usage_data = response.json()
        return sum(usage['total'] for usage in usage_data['usages'] if usage['name'] == vm_name)
    else:
        print(f"Error fetching usage data: {response.status_code} - {response.text}")
        return 0.0


def delete_equinix_vm(vm_id):
    """
    Delete a VM using its ID.

    Parameters:
        vm_id (str): The ID of the VM to delete.
    """
    url = f"{BASE_URL}/devices/{vm_id}"

    try:
        response = requests.delete(url, headers=HEADERS)

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


# Replace with your specific project ID
projects_info_dict = {
    'test': 'e6df9343-8781-4f27-b942-8f9675d5e0e7',
    'development': 'ce48ed95-821d-4f9e-89d5-330f7ee52ba4'
}

# Fetch and print the list of running VMs
manage_equinix_vms(projects_info_dict)
