
# Equinix VM Management Script

This script allows you to manage Equinix Metal VMs by fetching their details, displaying their current states, and optionally deleting them. You can specify a project, skip certain VMs based on tags, and view the total cost incurred by each VM.

## Features

- Fetch and display all VMs in a specified Equinix project.
- Display VM details such as name, ID, state, owner, tags, and total cost.
- Optionally delete VMs, with the ability to skip VMs tagged as `DO_NOT_DELETE`.
- Print VM details in a formatted table for easy viewing.

## Requirements

- Python 3.x
- The `requests` library (can be installed via `pip install requests`)
- An Equinix Metal API token

## Usage

### Command-line Arguments

- `--token`: **(Required)** The API token for Equinix Metal.
- `--project`: **(Required)** The name of the project to manage VMs.
- `--delete`: **(Optional)** Flag to trigger deletion of VMs.
- `--skip-do-not-delete-tags`: **(Optional)** Flag to skip deletion of VMs with the tag `DO_NOT_DELETE`.

### Example Usage

To fetch and display all VMs in the `Zededa Test` project:

```bash
python3 equinixManageVM.py --token your_api_token --project "Zededa Test"
```

To fetch VMs and delete them (excluding those tagged as `DO_NOT_DELETE`):

```bash
python3 equinixManageVM.py --token your_api_token --project "Zededa Test" --delete --skip-do-not-delete-tags
```

To force delete all VMs in the project:

```bash
python3 equinixManageVM.py --token your_api_token --project "Zededa Test" --delete
```

### Scheduled Execution (Jenkins Cron)

You can use this script in a Jenkins job and schedule it to run automatically (e.g., every Friday at 10 PM IST) by using the following cron expression in Jenkins:

```
0 16 * * 5
```

## Setup

1. Clone the repository and navigate to the directory:
   ```bash
   git clone https://github.com/vivek-zededa/equinix-manage.git
   cd equinix-manage
   ```

2. Install the required dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Execute the script using the appropriate arguments (see [Usage](#usage)).

## Project IDs

The project names and their corresponding IDs are stored in a dictionary inside the script. You can modify the following mapping to add your own projects:

```python
PROJECTS_INFO_DICT = {
    'Zededa Test': 'e6df9343-8781-4f27-b942-8f9675d5e0e7',
    'Zededa Development': 'ce48ed95-821d-4f9e-89d5-330f7ee52ba4'
}
```

## How It Works

1. **Fetching VMs:** The script makes an API call to Equinix Metal using the provided project ID and retrieves all devices (VMs) in that project.
   
2. **Displaying VMs:** It prints a formatted table with VM details, including the name, state, owner, tags, and cost.
   
3. **VM Deletion (Optional):** If the `--delete` flag is set, the script attempts to delete VMs. If the `--skip-do-not-delete-tags` flag is also set, it skips any VM tagged with `DO_NOT_DELETE`.

## Notes

- Ensure your API token has the necessary permissions to perform delete operations if you use the `--delete` flag.
- Handle your API token securely (avoid hardcoding it into scripts or committing it to version control). Use environment variables or Jenkins credentials management for security.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
