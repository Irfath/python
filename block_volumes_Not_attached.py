import oci
import sys
import os


from helpers.ocisdk import OCISDK
from helpers.utils import getProfilesFromConfig


ocisdk = OCISDK()


# ==============================================
# =============== Select Profile ===============
# ==============================================
SELECTED_PROFILE = ""


COMPARTMENT_ID = 'ocid1.compartment.oc1..aaaaaaaak43yymo6paopwm2chr34pzn6csll67ohhclrgeb6bwe5s5vojoba'


try:
    # load OCI Configs
    OCI_CONFIG_FILE_PATH =  os.getcwd() + "/configs/config.oci"  # '~/.oci/config'
    profiles = getProfilesFromConfig(OCI_CONFIG_FILE_PATH)

    SELECTED_PROFILE = profiles[0]

except:
    print("Error: Cannot read config file or empty config file.")
    sys.exit()

if len(profiles) > 1:
    print("Please select config name : \n")

    for i, prof in enumerate(profiles):
        print(f"\t{i+1} : {prof}")

    try:
        ind = int(input("\nEnter the profine number : "))
        SELECTED_PROFILE = profiles[ind - 1]
    except:
        print("Error : Invalid input")

print(f"Selected Profile X : {SELECTED_PROFILE}")


COMPARTMENT_ID = 'ocid1.compartment.oc1..aaaaaaaak43yymo6paopwm2chr34pzn6csll67ohhclrgeb6bwe5s5vojoba'



def get_instance_display_names(ocisdk, compartment_id, cfg_name):
    try:
        instances = ocisdk.getAllVMs(compartment_id, cfgName=cfg_name)
        display_names = [instance.display_name for instance in instances]
        return display_names
    except Exception as e:
        print(f"Error retrieving instance display names: {e}")
        return []
    

    instance_display_names = get_instance_display_names(ocisdk, COMPARTMENT_ID, selected_profile)
    print("Instance Display Names:")
    for display_name in instance_display_names:
        print(display_name)