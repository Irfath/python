import oci
import sys
import os
import json
from datetime import datetime
from helpers.ocisdk import OCISDK
from helpers.utils import getProfilesFromConfig
import csv

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
TENANCY_OCID = 'ocid1.tenancy.oc1..aaaaaaaaxckvxcrpggjrgzbzg4rt2c436k5qdo3w3nnqqk6xyhuzikd4rubq'

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

# Load the config file and initialize the BlockstorageClient and IdentityClient
config = oci.config.from_file(OCI_CONFIG_FILE_PATH, SELECTED_PROFILE)
blockstorage_client = oci.core.BlockstorageClient(config)
identity_client = oci.identity.IdentityClient(config)
compute_client = oci.core.ComputeClient(config)

compartment_id='ocid1.compartment.oc1..aaaaaaaak43yymo6paopwm2chr34pzn6csll67ohhclrgeb6bwe5s5vojoba'

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

#block volume
def get_instance_name(volume_id):
    try:
        attachments = blockstorage_client.list_volume_attachments(compartment_id=compartment_id, volume_id=volume_id).data
        if attachments:
            instance_id = attachments[0].instance_id
            instance = compute_client.get_instance(instance_id).data
            return instance.display_name
        return None
    except oci.exceptions.ServiceError as e:
        print(f"Service error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Get all block volumes in the specified compartment
block_volumes = list_block_volumes(compartment_id)

print(f"Total number of block volumes: {len(block_volumes)}")

print("Display_Name,volume_OCID,Size (in GB),Lifecycle State, Instance Name")
for volume in block_volumes:
    instance_name = get_instance_name(volume.id)
    print(f"Display Name: {volume.display_name}, Volume_OCID: {volume.id}, Size (in GB): {volume.size_in_gbs}, Lifecycle State: {volume.lifecycle_state}, Instance Name: {instance_name}")

#  data  CSV
volume_data = [["Display Name", "Volume_OCID", "Size (in GB)", "Lifecycle State", "Instance Name"]]
for volume in block_volumes:
    instance_name = get_instance_name(volume.id)
    volume_data.append([volume.display_name, volume.id, volume.size_in_gbs, volume.lifecycle_state, instance_name])

csv_file_path = r'C:\Users\irfath\Desktop\CodeGen Knowledge\Python\OCI_test\Reports\block_volume_details2.csv'

with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(volume_data)

print(f"Block Volume Details have been written to {csv_file_path}")
