import sys
import os
import json
from datetime import datetime
from helpers.ocisdk import OCISDK
from helpers.utils import getProfilesFromConfig
import oci

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

# ==============================================
# =========== Delete Block Volume ==============
# ==============================================

def delete_block_volume(volume_id):
    try:
        # Get the block volume
        volume = blockstorage_client.get_volume(volume_id).data
        print(f"Found Block Volume: {volume.display_name}")

        # Delete the block volume
        blockstorage_client.delete_volume(volume_id)
        print(f"Block Volume '{volume.display_name}' is being deleted.")
    except oci.exceptions.ServiceError as e:
        print(f"Error: {e.message}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python delete_block_volume.py <volume_id>")
        sys.exit(1)

    volume_id = sys.argv[1]
    delete_block_volume(volume_id)
