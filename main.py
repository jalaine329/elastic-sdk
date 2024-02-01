from datetime import datetime
from utils import get_credentials
from report_generators import generate_ilm_policy_report, generate_shard_size_report, generate_api_key_report, monitor_share_report
from config import clusters

def main_menu():
    print("Main Menu: ")
    print("1. Generate ILM Policy Report")
    print("2. Generate Shard Size Report")
    print("3. Generate API Report")
    print("4. Generate Monitoring Report")
    print("5. Exit")
    choice = input("Enter your choice: ")

    if choice == '1':
        generate_ilm_policy_report(clusters, username, password, current_date)
    elif choice == '2':
        generate_shard_size_report(clusters, username, password, current_date)
    elif choice == '3':
        generate_api_key_report(clusters, username, password, current_date)
    elif choice == '4':
        monitor_share_report(clusters, username, password, current_date)
    elif choice == '5':
        print("Exiting the program.")
        exit()
    else:
        print("Invalid choice. Please select a valid option.")
        main_menu()

# main script
if __name__ == "__main__":
    # auth creds, cluster selection and cluster initialization
    username, password = get_credentials()

    # get the current date in YYYYMMDD format
    current_date = datetime.now().strftime('%Y%m%d')

    while True:
        main_menu()
