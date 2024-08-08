import oci
import sys
import os
import paramiko
from helpers.ocisdk import OCISDK
from helpers.utils import getProfilesFromConfig

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

# SSH key details
SSH_KEY_PATH = r'C:\Users\irfath\Desktop\CodeGen Knowledge\Python\OCI_test\ssh-keys-bah\jump'
SSH_KEY_PASSPHRASE = '^~)0Mc(Nx^0.&54o'
SSH_USER = 'opc'


def execute_script_on_instance(instance_ip, script_path):
    try:
        key = paramiko.RSAKey(filename=SSH_KEY_PATH, password=SSH_KEY_PASSPHRASE)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(instance_ip, username=SSH_USER, pkey=key)

        sftp = ssh.open_sftp()
        sftp.put(script_path, '/tmp/script.sh')
        sftp.close()

        stdin, stdout, stderr = ssh.exec_command('chmod +x /tmp/script.sh && /tmp/script.sh')
        print(stdout.read().decode())
        print(stderr.read().decode())
        ssh.close()
    except Exception as e:
        print(f"Failed to execute script on instance {instance_ip}. Details: {e}")

# List of instance IPs
instance_ips = [
    '172.22.180.123'
    #'your_instance_ip_2',
    # Add more instance IPs as needed
]

# Path to the script file on your local machine
script_path = r'C:\Users\irfath\Desktop\CodeGen Knowledge\Python\OCI_test\irf_script.sh'

# Execute the script on each instance
for instance_ip in instance_ips:
    execute_script_on_instance(instance_ip, script_path)
    print(f'Executed script on instance {instance_ip}')
