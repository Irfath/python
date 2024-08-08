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

# Load the config file and initialize the IdentityClient
config = oci.config.from_file(OCI_CONFIG_FILE_PATH, SELECTED_PROFILE)
identity_client = oci.identity.IdentityClient(config)

# Function to list all users in the tenancy
def list_users(tenancy_ocid):
    try:
        users = []
        response = identity_client.list_users(compartment_id=tenancy_ocid)
        users.extend(response.data)
        
        # Handle pagination if necessary
        while response.has_next_page:
            response = identity_client.list_users(compartment_id=tenancy_ocid, page=response.next_page)
            users.extend(response.data)
        
        return users

    except oci.exceptions.ServiceError as e:
        print(f"Service error: {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


# Fetch and print user details
users = list_users(TENANCY_OCID)
if users:
    for user in users:
        user_details = {
        #    "name": user.name,
         #   "email": user.email
          # "active": user.lifecycle_state == "ACTIVE"
        }
       # print(json.dumps(user_details, cls=DateTimeEncoder, indent=4))
else:
    print("No users found.")


# Prepare data for CSV
user_data = [["User Name", "User emaiL","Active status"]]  # Header row
for user in users:
    user_data.append([user.name, user.email, user.lifecycle_state])

# Print the names of all compartments
print("USER Names and EMAILS:")
for user in users:
    print(user)
