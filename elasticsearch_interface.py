from elasticsearch import Elasticsearch

# prompt the user to choose a cluster and validate the input
def select_cluster(clusters):
    print("Available Clusters:")
    cluster_names = list(clusters.keys())
    for idx, cluster_name in enumerate(cluster_names, start=1):
        print(f"{idx}. {cluster_name}")
    while True:
        try:
            selected_cluster = int(input("Enter the number of the cluster you want to use: ")) - 1
            if 0 <= selected_cluster < len(cluster_names):
                return cluster_names[selected_cluster], clusters[cluster_names[selected_cluster]]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def init_es_client(cluster_urls, username, password):
    return Elasticsearch(cluster_urls, http_auth=(username, password), verify_certs=False)
