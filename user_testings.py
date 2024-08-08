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
### Farah      : ocid1.tenancy.oc1..aaaaaaaaiqsiivkfwfaaprcuradzeoij4uactsr6cqw657qratep7bkry4xq
### Codegen    : ocid1.tenancy.oc1..aaaaaaaaxckvxcrpggjrgzbzg4rt2c436k5qdo3w3nnqqk6xyhuzikd4rubq
### CodegenMSP : ocid1.tenancy.oc1..aaaaaaaaab74q4ydororotrz5q5vyjkl5albvhc6ymzlpi6542fz3mfrggea
try:
    # Load OCI Configs
    OCI_CONFIG_FILE_PATH = os.path.expanduser("~/.oci/config")
    profiles = getProfilesFromConfig(OCI_CONFIG_FILE_PATH)
    SELECTED_PROFILE = profiles[0]

    print(OCI_CONFIG_FILE_PATH)

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

# Function to list all groups for a user
def get_user_groups(user_ocid):
    try:
        user_group_memberships = identity_client.list_user_group_memberships(compartment_id=TENANCY_OCID, user_id=user_ocid).data
        groups = [identity_client.get_group(membership.group_id).data.name for membership in user_group_memberships]
        return groups
    except oci.exceptions.ServiceError as e:
        print(f"Service error: {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

# Function to check if a user has API key access
def has_api_key(user_ocid):
    try:
        api_keys = identity_client.list_api_keys(user_ocid).data
        return len(api_keys) > 0
    except oci.exceptions.ServiceError as e:
        print(f"Service error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Fetch and print user details with group memberships, permission level, and creation date
users = list_users(TENANCY_OCID)
if users:
    for user in users:
        user_groups = get_user_groups(user.id)
        api_key_access = has_api_key(user.id)
        user_details = {
            "name": user.name,
            "email": user.email,
            "active": user.lifecycle_state == "ACTIVE",
            "groups": user_groups,
            "permission_level": "API Key Access" if api_key_access else "Console Access",
            "creation_date": user.time_created,
            "MFA_Status": user.is_mfa_activated
        }
        print(f"USERSS: {user.name}, EMAILL: {user.email}, Active_STAT: {user.lifecycle_state}, GROUPS: {', '.join(user_groups)}, Permission_Level: {'API Key Access' if api_key_access else 'Console Access'}, Creation_Date: {user.time_created},MFA_Status: {user.is_mfa_activated}")
else:
    print("No users found.")

# Prepare data for CSV
user_data = [["User Name", "User Email", "Active Status", "Groups", "Permission Level", "Creation Date","MFA Status"]]  # Header row
for user in users:
    user_groups = get_user_groups(user.id)
    api_key_access = has_api_key(user.id)
    user_data.append([user.name, user.email, user.lifecycle_state, ", ".join(user_groups),  user.time_created,user.is_mfa_activated])

# Print the names of all compartments
print("USER Names, EMAILS, Groups, Permission Levels, Creation Dates,MFA_Status")
for user in users:
    user_groups = get_user_groups(user.id)
    api_key_access = has_api_key(user.id)
    print(f"USERSS: {user.name}, EMAILL: {user.email}, Active_STAT: {user.lifecycle_state}, GROUPS: {', '.join(user_groups)}, Permission_Level: {'API Key Access' if api_key_access else 'Console Access'}, Creation_Date: {user.time_created},MFA_Status: {user.is_mfa_activated}")



# Specify the path to the CSV file
csv_file_path = r'C:\Users\irfath\Desktop\CodeGen Knowledge\Python\OCI_test\Reports\user_details-codegen1.csv'

# Write the compartment names and OCIDs to the CSV file
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(user_data)

print("CSV file created successfully.")



