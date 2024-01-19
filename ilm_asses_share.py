from datetime import datetime, timezone, timedelta
from elasticsearch import Elasticsearch
import csv
import os
import re

# get the current date in YYYYMMDD format
current_date = datetime.now().strftime('%Y%m%d')

# auth creds
username = input("Enter your Elasticsearch username: ")
password = input("Enter your Elasticsearch password: ")

# elastic cluster info
clusters = {
    "cluster1": ["https://node1.com:9200", "https://node2.com:9200", "https://node3.com:9200"],
    "cluster2": ["https://node1.com:9200", "https://node2.com:9200", "https://node3.com:9200"]
}

# prompt the user to choose a cluster
print("Available Clusters:")
for idx, cluster_name in enumerate(clusters.keys(), start=1):
    print(f"{idx}. {cluster_name}")
selected_cluster = int(input("Enter the number of the cluster you want to use: ")) - 1
selected_cluster_name = list(clusters.keys())[selected_cluster]
cluster_urls = clusters[selected_cluster_name]

# elastic cluster info
cluster_selection = cluster_urls

# output file to write to
current_directory = os.getcwd()
csv_name = f"{selected_cluster_name.replace(' ', '').lower()}_ilm_policy_report_{current_date}.csv"
txt_name = f"{selected_cluster_name.replace(' ', '').lower()}_ilm_policy_report_{current_date}.txt"
output_csv_file = os.path.join(current_directory, csv_name)
output_text_file = os.path.join(current_directory, txt_name)

def convert_size_to_bytes(size_str):
    # this function converts size strings like '88k' or '5.2M' to bytes
    size_str = size_str.lower()
    units = { 'k': 1024, 'm': 1024**2, 'g': 1024**3, 't': 1024**4}
    match = re.match(r'^([\d.]+)([kmgtp]?)', size_str)
    if match:
        number = float(match.group(1))
        unit = match.group(2)
        return int(number * units.get(unit,1))
    else:
        return 0 # return 0 for unknown format    

# convert bytes to the appropriate format (B, KB, MB, GB, TB)
def format_size(size_bytes):    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            break
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} {unit}"

try:
    # go to the cluster and auth
    es = Elasticsearch(cluster_selection, http_auth=(username, password), verify_certs=False, timeout=30)

    # use get_lifecycle method to retrieve ILM policies
    ilm_policies_info = es.ilm.get_lifecycle()

    with open(output_csv_file, mode='w', newline='') as csv_file, open(output_text_file, mode='w', newline='') as text_file:
        fieldnames = ['ILM Policy', 'Index', 'Primary Size on Disk (bytes)', 'Total Size on Disk (bytes)']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # iterate through each ILM policy for the indices attached to it
        for policy_name, policy_data in ilm_policies_info.items():
            indices_attached = policy_data.get('in_use_by', {}).get('indices', [])
            templates = policy_data.get('in_use_by', {}).get('composable_templates', [])
            total_disk_space = 0 # Initialize total disk space for the ILM policy

            # Write to the text file
            text_file.write("=" * 50 + "\n")
            text_file.write(f"ILM Policy: {policy_name}")
            text_file.write("\n" + "=" * 50 + "\n")
            
            for index_name in indices_attached:
                # use cat.indices to get the size on disk of the primaries and total disk space
                cat_indices_info = es.cat.indices(index=index_name, format="json")
                primary_size = cat_indices_info[0]['pri.store.size']
                total_size = cat_indices_info[0]['store.size']

                # convert the size strings to bytes
                primary_size_bytes = convert_size_to_bytes(primary_size)
                total_size_bytes = convert_size_to_bytes(total_size)
                formatted_total_index = format_size(total_size_bytes)

                # write this data to text file
                text_file.write(f"Index: {index_name} Size: {formatted_total_index}\n")

                # write to doc
                writer.writerow({'ILM Policy': policy_name, 'Index': index_name, 'Primary Size on Disk (bytes)': primary_size_bytes, 'Total Size on Disk (bytes)': total_size_bytes})

                # add the total disk space of this index to the total for this ILM policy
                total_disk_space += total_size_bytes

                # print the total disk space used by this ILM policy
                print(f"Processed ILM Policy: {policy_name}")
                print(f"Index: {index_name}")
                print("\n" + "=" * 50 + "\n")
            
            # write final size
            formatted_total_space = format_size(total_disk_space)
            text_file.write("=" * 50 + "\n")
            text_file.write(f"ILM Policy: {policy_name}\n")
            text_file.write(f"Number of Templates: {len(templates)}\n")
            text_file.write(f"Number of Indices: {len(indices_attached)}\n")
            text_file.write(f"Total Disk Space Used: {formatted_total_space}\n")
            text_file.write("=" * 50 + "\n\n")

        print("\nCSV report successfully created at:", output_csv_file, output_text_file)

except Exception as ex:
    print(f"\n An unexpected error occurred: {ex}")
    print("An error occurred while generating the report.")

# additional status report
print("\nScript completed")
