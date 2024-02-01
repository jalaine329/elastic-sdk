from utils import convert_size_to_bytes, format_size, normalize_shard_size
from elasticsearch_interface import init_es_client, select_cluster
from datetime import datetime
import os
import csv

# function to generate ILM policy report
def generate_ilm_policy_report(clusters, username, password, current_date):
    try:
        selected_cluster_name, cluster_urls = select_cluster(clusters)

        # output file to write to
        current_directory = os.getcwd()
        csv_name = f"{selected_cluster_name.replace(' ', '').lower()}_ilm_policy_report_{current_date}.csv"
        txt_name = f"{selected_cluster_name.replace(' ', '').lower()}_ilm_policy_report_{current_date}.txt"
        output_csv_file = os.path.join(current_directory, csv_name)
        output_text_file = os.path.join(current_directory, txt_name)

        # go to the cluster and auth
        es = init_es_client(cluster_urls, username, password)

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
                text_file.write(f"Total Disk Space Used {policy_name}: {formatted_total_space}\n")
                text_file.write("=" * 50 + "\n\n")

            print("\nCSV report successfully created at:", output_csv_file, output_text_file)

    except Exception as ex:
        print(f"\n An unexpected error occurred: {ex}")
        print("An error occurred while generating the report.")

    # additional status report
    print("\nILM report completed")

# function to generate shard size report
def generate_shard_size_report(clusters, username, password, current_date):
    try:
        selected_cluster_name, cluster_urls = select_cluster(clusters)

        # go to the cluster and auth
        es = init_es_client(cluster_urls, username, password)

        # send a get request to retrieve information about nodes
        node_list = es.cat.nodes(format="json", s="name:asc")

        # print the available nodes to the screen to allow the user to select which node to work w/
        print("Available nodes: ")
        for idx, node_info in enumerate(node_list, start=1):
            print(f"{idx}. {node_info['name']}")
        selected_node = int(input("Enter the number of the node you want to use: ")) - 1
        selected_node_name = node_list[selected_node]['name']

        # define csv and txt file paths using cwd
        current_dir = os.getcwd()
        csv_name = f"{selected_node_name.replace(' ', '').lower()}_shardfinder_report_{current_date}.csv"
        output_csv_file = os.path.join(current_dir, csv_name)
        txt_name = f"{selected_node_name.replace(' ', '').lower()}_shardfinder_report_{current_date}.txt"
        output_txt_file = os.path.join(current_dir, txt_name)  

        # retrieve the shard data for the desired node
        shard_data = es.cat.shards(format="json")  

        # create a list to store shard info
        shard_info_list = []

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
            writer.writerow([node, index, format_size(store_size), shard_number])

            print(f"Shard sizes for {selected_node_name} in {selected_cluster_name} written to '{output_csv_file}'")

            # sort the shard info list by shard size in descending order
            shard_info_list.sort(reverse=True, key=lambda x: x[0])

            # prepare the output text file
            with open(output_txt_file, "w") as f:

                # write header
                f.write("Node, Index, Shard Size\n")

                # iterate through sorted shard info list and write to the text file
                for shard_size, shard_info in shard_info_list:
                    node, index, shard_number = shard_info
                    f.write(f"{node}, {index}, {format_size(shard_size)}\n")

            print(f"Shard sizes for {selected_node_name} in {selected_cluster_name} written to '{output_txt_file}'")

    except Exception as e:
        print(f"An error occurred: {e}")

# function to generate a list of all non-alert api keys on a selected aess cluster
def generate_api_key_report(clusters, username, password, current_date):
    try:
        selected_cluster_name, cluster_urls = select_cluster(clusters)

        # go to the cluster and auth
        es = init_es_client(cluster_urls, username, password)

        # define file path using cwd
        current_dir = os.getcwd()
        txt_name = f"{selected_cluster_name.replace(' ', '').lower()}_apikey_report_{current_date}.txt"
        output_txt_file = os.path.join(current_dir, txt_name)

        # get api keys
        api_keys_response = es.security.get_api_key()

        # write desired info to file
        with open(output_txt_file, "w") as file:
            file.write("{} API Key Report\n".format(selected_cluster_name)) # add which cluster the report is for
            file.write("GET API Keys API\n\n")
            
            # check the response structure
            if 'api_keys' in api_keys_response:
                api_keys = api_keys_response['api_keys']
                
                # write the desired parts of the output to file
                for api_key in api_keys:
                    api_key_name = api_key['name']

                    # check if the API key name contains "Alerting:" and skip writing if it does
                    if "Alerting:" in api_key_name:
                        continue

                    file.write("API ID: {}\n".format(api_key['id']))
                    file.write("Name: {}\n".format(api_key['name']))
                    file.write("Invalidated: {}\n".format(api_key['invalidated']))
                    file.write("Username: {}\n".format(api_key['username']))
                    file.write("Realm: {}\n".format(api_key['realm']))

                    # change expiration from ms if it exists and then send info to file
                    if 'expiration' in api_key:
                        init_time = api_key['expiration']
                        datetime_obj = datetime.fromtimestamp(init_time / 1000.0)
                        formatted_datetime = datetime_obj.strftime('%m-%d-%Y %H:%M:%S')
                        file.write("Expiration: {}\n\n".format(formatted_datetime))
                    else:
                        file.write("\n")
            else:
                print("No API Keys found in the response.")

            # show that the file has been successfully written to
            print("The list of API keys has been written to:", output_txt_file)

    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
        print("An error occurred while generating the report.")

# function to generate a monitoring report for a selected cluster
def monitor_share_report(clusters, username, password, current_date):
    try:
        selected_cluster_name, cluster_urls = select_cluster(clusters)

        # go to the cluster and auth
        es = init_es_client(cluster_urls, username, password)

        # GET _cluster/health
        # adjust this to have the name and number of nodes that you have in your own cluster or clusters
        cluster_health = es.cluster.health()
        if cluster_health['cluster_name'] == "cluster1":
            number_nodes = 1
        elif cluster_health['cluster_name'] == "cluster2":
            number_nodes = 3
        else:
            number_nodes = 3

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
    
    except Exception as ex:
        print(f"\n An unexpected error occurred: {ex}")
        print("An error occurred while generating the report.")
