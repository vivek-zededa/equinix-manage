import requests


# Replace with your Equinix Metal API token
API_TOKEN = 'qy2ugN8KaaD22ht9DtvDf2pCxYtx3oiL'

# Set the base URL for the Equinix Metal API
BASE_URL = 'https://api.equinix.com/metal/v1'

# Set the headers for the API request, including the Authorization token
headers = {
    'X-Auth-Token': API_TOKEN,
    'Content-Type': 'application/json'
}
# Function to fetch all devices (VMs) for a given project
def manage_equinix_vms(project_info,delete=True,skip_do_not_delete_tag=True):
    for project_id in project_info.values():
        url = f"{BASE_URL}/projects/{project_id}/devices"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            devices = response.json()['devices']
            running_vms = [device for device in devices if device['state'] in ['active','inactive']]
            print(f"\nFound {len(running_vms)} VMs in project {project_id}: with states running|stopped")
            for vm in running_vms:
                total_vm_cost = fetch_equinix_vm_cost(project_id,vm['hostname'])
                print(f"VM Name: {vm['hostname']}, VM ID: {vm['id']}, Current State: {vm['state']}, Owner: {vm['created_by']['full_name']}, Tags: {vm['tags']}, Total Cost Incurred: ${total_vm_cost:.2f}")
                if delete:
                    if skip_do_not_delete_tag and 'DO_NOT_DELETE' in vm['tags']:
                        print(f"Skipping deletion of VM {vm['hostname']} (ID: {vm['id']}) because it has the 'DO_NOT_DELETE' tag.")
                        continue
                    delete_equinix_vm(vm['id'])
        else:
            print(f"Error fetching VMs: {response.status_code} - {response.text}")


def fetch_equinix_vm_cost(project_id, vm_name):
    url = f"{BASE_URL}/projects/{project_id}/usages"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        usage_data = response.json()
        total_cost = 0.0
        for usage in  usage_data['usages']:
            if usage['name'] == vm_name:
                total_cost += usage['total']
        return total_cost
    else:
        print(f"Error fetching usage data: {response.status_code} - {response.text}")


def delete_equinix_vm(vm_id):
    # API URL to delete a device (VM) using its ID
    url = f"{BASE_URL}/devices/{vm_id}"

    try:
        # Send the DELETE request to the API to delete the VM
        response = requests.delete(url, headers=headers)

        # Check if the deletion was successful
        if response.status_code == 204:
            print(f"VM with ID {vm_id} successfully deleted.")
        elif response.status_code == 404:
            print(f"VM with ID {vm_id} not found.")
        else:
            print(f"Failed to delete VM with ID {vm_id}. Status Code: {response.status_code}")
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Replace with your specific project ID
projects_info_dict = \
    {
    'test': 'e6df9343-8781-4f27-b942-8f9675d5e0e7',
    'development' : 'ce48ed95-821d-4f9e-89d5-330f7ee52ba4'
    }

# Fetch and print the list of running VMs
manage_equinix_vms(projects_info_dict)
