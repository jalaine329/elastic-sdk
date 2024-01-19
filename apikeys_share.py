from datetime import datetime, timezone, timedelta
from elasticsearch import Elasticsearch
import csv
import os

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
try:
    selected_cluster = int(input("Enter the number of the cluster you want to use: ")) - 1
    if selected_cluster < 0 or selected_cluster >= len(clusters):
        raise ValueError("Invalid cluster selection")
    
    selected_cluster_name = list(clusters.keys())[selected_cluster]
    cluster_urls = clusters[selected_cluster_name]

    # auth to the cluster of choice
    es = Elasticsearch(cluster_urls, http_auth=(username, password), verify_certs=False)

    # get the current working directory
    current_dir = os.getcwd()

    # define file path using cwd
    file_name = f"{selected_cluster_name.replace(' ', '').lower()}_apikey_report_{current_date}.txt"
    file_path = os.path.join(current_dir, file_name)

    # get api keys
    api_keys_response = es.security.get_api_key()

    # write desired info to file
    with open(file_path, "w") as file:
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
    print("The list of API keys has been written to:", file_path)

# error and exceptions
except ValueError as ve:
    print(f"Error: {ve}. Please choose a valid cluster.")
except Exception as ex:
    print(f"An unexpected error occurred: {ex}")
    print("An error occurred while generating the report.")
