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
    "cluster1" : ["https://node1.com:9200"],
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

def monitor(cluster_selection):
    # go to the cluster and auth
    es = Elasticsearch(cluster_selection, http_auth=(username, password), verify_certs=False)

    # GET _cluster/health
    cluster_health = es.cluster.health()
    if cluster_health['cluster_name'] == "cluster1":
        number_nodes = xx # add number of nodes in the cluster
    elif cluster_health['cluster_name'] == "cluster2":
        number_nodes = xx

    # GET _cat/nodes and sort returned data
    node_stats = es.cat.nodes(format="json")
    sorted_node_stats = sorted(node_stats, key=lambda x: x['name'])

    # GET _cat/allocation and sort returned data
    cat_allocation = es.cat.allocation(format="json")
    sorted_cat_allocation = sorted(cat_allocation, key=lambda x: x['node'])

    # get the current working directory
    current_dir = os.getcwd()

    # define file path using cwd
    txt_name = f"{selected_cluster_name.replace(' ', '').lower()}_monitor_report_{current_date}.txt"
    output_text_file = os.path.join(current_dir, txt_name)

    with open(output_text_file, "w") as file:
        file.write("Cluster Monitor Report\n\n")
        file.write("Cluster Health API\n")
        file.write("Cluster Name: {}\n".format(cluster_health['cluster_name']))
        file.write("Status: {}\n".format(cluster_health['status']))
        file.write("Number of Nodes: {} of {}\n".format(cluster_health['number_of_nodes'],number_nodes))
        file.write("Unassigned Shards: {}\n".format(cluster_health['unassigned_shards']))
        file.write("Percent Active Shards: {}\n\n".format(cluster_health['active_shards_percent_as_number']))

        file.write("Node Stats API\n")
        for node_info in sorted_node_stats:
            node_name = node_info['name']
            heap_percent = node_info['heap.percent']
            cpu = node_info['cpu']
            file.write(f"{node_name}, Heap Usage: {heap_percent}%, CPU Utilization: {cpu}%\n")
        
        file.write("\nShard and Disk Usage Info\n")
        for allocation_info in sorted_cat_allocation:
            cat_name = allocation_info['node']
            shards = allocation_info['shards']
            disk_percent = allocation_info['disk.percent']
            file.write(f"{cat_name}, shards allocated: {shards}, disk percent: {disk_percent}%\n")

    print("Cluster health info has been written to:", output_text_file)

monitor(cluster_selection)
