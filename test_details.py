import oci
import sys
import os
import csv
import json  
from datetime import datetime
from helpers.ocisdk import OCISDK
from helpers.utils import getProfilesFromConfig

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

# Initialize OCISDK
ocisdk = OCISDK()

# ==============================================
# =============== Select Profile ===============
# ==============================================
SELECTED_PROFILE = ""

# Set your root compartment ID (this should be the tenancy OCID)
TENANCY_OCID = 'ocid1.compartment.oc1..aaaaaaaak43yymo6paopwm2chr34pzn6csll67ohhclrgeb6bwe5s5vojoba'

try:
    # Load OCI Configs
    OCI_CONFIG_FILE_PATH = os.path.expanduser("~/.oci/config")
    profiles = getProfilesFromConfig(OCI_CONFIG_FILE_PATH)
    SELECTED_PROFILE = profiles[0]

except Exception as e:
    print(f"Error: Cannot read config file or empty config file. Details: {e}")
    sys.exit()

# If multiple profiles are found, prompt the user to select one
if len(profiles) > 1:
    print("Please select config name : \n")

    for i, prof in enumerate(profiles):
        print(f"\t{i+1} : {prof}")

    try:
        ind = int(input("\nEnter the profile number : "))
        SELECTED_PROFILE = profiles[ind - 1]
    except Exception as e:
        print(f"Error: Invalid input. Details: {e}")
        sys.exit()

print(f"Selected Profile: {SELECTED_PROFILE}")

# Load the config file and initialize the BlockstorageClient and ComputeClient
config = oci.config.from_file(OCI_CONFIG_FILE_PATH, SELECTED_PROFILE)
blockstorage_client = oci.core.BlockstorageClient(config)
compute_client = oci.core.ComputeClient(config)

compartment_id = 'ocid1.compartment.oc1..aaaaaaaaqebxly4yqahee72qluopghprzfeqy6mazf5fcl6ghruerlcodjua'

# Function to list all block volumes in a compartment
def list_block_volumes(compartment_id):
    try:
        volumes = []
        response = blockstorage_client.list_volumes(compartment_id=compartment_id)
        volumes.extend(response.data)
        
        # Handle pagination if necessary
        while response.has_next_page:
            response = blockstorage_client.list_volumes(compartment_id=compartment_id, page=response.next_page)
            volumes.extend(response.data)
        
        return volumes

    except oci.exceptions.ServiceError as e:
        print(f"Service error: {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

# Function to list all instances in a compartment and sum their OCPUs and memory
def get_total_resources(compartment_id):
    try:
        total_ocpus = 0
        total_memory_gb = 0
        response = compute_client.list_instances(compartment_id=compartment_id)
        instances = response.data
        
        # Handle pagination if necessary
        while response.has_next_page:
            response = compute_client.list_instances(compartment_id=compartment_id, page=response.next_page)
            instances.extend(response.data)
        
        for instance in instances:
            shape_details = compute_client.get_instance(instance.id).data.shape_config
            total_ocpus += shape_details.ocpus
            total_memory_gb += shape_details.memory_in_gbs  # Assuming `memory_in_gbs` is available

        return total_ocpus, total_memory_gb

    except oci.exceptions.ServiceError as e:
        print(f"Service error: {e}")
        return 0, 0
    except Exception as e:
        print(f"Error: {e}")
        return 0, 0

# Get all block volumes in the specified compartment
block_volumes = list_block_volumes(compartment_id)

print(f"Total number of block volumes: {len(block_volumes)}")

# Initialize a variable to hold the sum of sizes
total_size_gb = 0



print("Display_Name,volume_OCID,Size (in GB),Lifecycle State")
for volume in block_volumes:
#    print(f"Display Name: {volume.display_name}, Volume_OCID: {volume.id}, Size (in GB): {volume.size_in_gbs}, Lifecycle State: {volume.lifecycle_state}")
    total_size_gb += volume.size_in_gbs


# Save the block volume data to a CSV file
volume_data = [["Display Name", "Volume_OCID", "Size (in GB)", "Lifecycle State"]]
for volume in block_volumes:
    volume_data.append([volume.display_name, volume.id, volume.size_in_gbs, volume.lifecycle_state])

csv_file_path = r'Reports\block_volume_details2.csv'

with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(volume_data)

print(f"Block Volume Details have been written to {csv_file_path}")


# Get the total number of OCPUs and total memory in the specified compartment
total_ocpus, total_memory_gb = get_total_resources(compartment_id)


print(f"\nTotal size of all block volumes: {total_size_gb} GB")
print(f"\nTotal number of OCPUs in the compartment: {total_ocpus}")
print(f"Total memory (in GB) in the compartment: {total_memory_gb}")

