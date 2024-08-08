import oci
import csv

# Specify the path to your OCI config file and the profile name
config_file_path = '~/.oci/config'  # e.g., '~/.oci/config'
config_profile_name = 'irfath_codegen'  # e.g., 'DEFAULT'

# Load the OCI config
config = oci.config.from_file(config_file_path, config_profile_name)

# Initialize the IdentityClient
identity_client = oci.identity.IdentityClient(config)

# Specify the OCID of the root compartment (typically your tenancy OCID)
root_compartment_id = config["tenancy"]

# List all compartments in the specified root compartment
compartments = oci.pagination.list_call_get_all_results(
    identity_client.list_compartments,
    root_compartment_id,
    compartment_id_in_subtree=True
).data

# Print the names of all compartments
print("Compartment Names and OCIDs:")
for compartment in compartments:
    print(f"Name: {compartment.name}, OCID: {compartment.id}")


# Prepare data for CSV
compartment_data = [["Compartment Name", "Compartment OCID"]]  # Header row
for compartment in compartments:
    compartment_data.append([compartment.name, compartment.id])

# Specify the path to the CSV file
csv_file_path = r'C:\Users\irfath\Desktop\CodeGen Knowledge\Python\OCI_test\Reports\compartment_names.csv'

# Write the compartment names and OCIDs to the CSV file
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(compartment_data)

print(f"Compartment names and OCIDs have been written to {csv_file_path}")