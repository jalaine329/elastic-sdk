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

# function to normalize shard size values to bytes
def normalize_shard_size(size_str):
    if size_str is not None:
        size_str = size_str.lower()

        if 'kb' in size_str:
            size = float(size_str.replace('kb', '')) * 1024
        elif 'mb' in size_str:
            size = float(size_str.replace('mb', '')) * 1024 * 1024
        elif 'gb' in size_str:
            size = float(size_str.replace('gb', '')) * 1024 * 1024 *1024
        elif 'b' in size_str:
            size = float(size_str.replace('b', ''))
        else:
            size = 0
    else:
        size = 0

    return int(size)

# function to format shard sizes to gb, mb or kb
def format_shard_size(size):
    if size >= 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"
    elif size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    elif size >= 1024:
        return f"{size / 1024:.2f} KB"
    else:
        return f"{size} B"

# go to the cluster and auth
es = Elasticsearch(cluster_urls, http_auth=(username, password), verify_certs=False)

# send a get request w/ basic auth
response = es.cluster.health()

# create a list of nodes in the selected cluster
node_list = []

# create a list to store shard info
shard_info_list = []

# send a get request to retrieve information about nodes
response = es.cat.nodes(format="json", s="name:asc")

# iterate through list and extract node names
for node_info in response:
    node_list.append(node_info['name'])
    
# print the available nodes to the screen to allow the user to select which node to work w/
print("Available nodes: ")
for idx, name in enumerate(node_list, start=1):
    print(f"{idx}. {name}")
selected_node = int(input("Enter the number of the node you want to use: ")) - 1
selected_node_name = node_list[selected_node]

# retrieve the shard data for the desired node
shard_data = es.cat.shards(format="json")

try:
    # retrieve the shard data for the desired node
    shard_data = es.cat.shards(format="json")

    # get the current working directory
    current_dir = os.getcwd()

    # define csv and txt file paths using cwd
    csv_name = f"{selected_node_name.replace(' ', '').lower()}_shardfinder_report_{current_date}.csv"
    output_csv_file = os.path.join(current_dir, csv_name)

    txt_name = f"{selected_node_name.replace(' ', '').lower()}_shardfinder_report_{current_date}.txt"
    output_txt_file = os.path.join(current_dir, txt_name)    

    # prepare the csv output file
    with open(output_csv_file, "w", newline='') as f:

        # create a csv writer
        writer = csv.writer(f)

        # write a header row
        writer.writerow(['Node', 'Index', 'Store Size', 'Shard Number' ])

        # iterate over each shard and print its size
        for shard in shard_data:
            if shard['node'] == selected_node_name:
                node = shard['node']
                index = shard['index']
                shard_number = str(shard['shard']).replace('\n','')
                store_size = normalize_shard_size(shard['store'])

                # append shard info as a tuple (shard size, shard data)
                shard_info_list.append((store_size, [node, index, shard_number]))

                # write shard info to the file
                writer.writerow([node,index,store_size,shard_number])
    
    print(f"Shard sizes for {selected_node_name} written to '{output_csv_file}'")

    # sort the shard info list by shard size in descending order
    shard_info_list.sort(reverse=True, key=lambda x: x[0])

    # prepare the output text file
    with open(output_txt_file, "w") as f:

        # write header
        f.write("Node, Index, Shard Size (bytes)\n")

        # iterate through sorted shard info list and write to the text file
        for shard_size, shard_info in shard_info_list:
            node, index, shard_number = shard_info
            f.write(f"{node}, {index}, {format_shard_size(shard_size)}\n")

    print(f"Shard sizes for {selected_node_name} written to '{output_txt_file}'")

except Exception as e:
    print(f"An error occurred: {e}")

