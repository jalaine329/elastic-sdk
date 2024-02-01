# elastic_management_app

## Description
This script currently has four different operations that can be performed: generating a report on the size of the different ILM policies within a cluster (generate_ilm_policy_report), generating a report on the sizes of shards located on a specific node within a selected cluster (generate_shard_size_report), generate a report showing which api keys are expiring in a selected cluster (generate_api_key_report) and generate a basic monitoring report about the health of a cluster (monitor_share_report).

When you start the application you get to choose which operation you would like to perform and on what cluster you would like to perform it. The operation is performed and then you choose if you would like to do something else or if you would like to exit.

## Installation
I need to figure out how best to install this. You should be able to pull it down to your local machine or one of the machines in a given cluster if they have the right software installed (python, elastic sdk, etc). You could also just copy it out of here and run it from your own ide.

## Roadmap
This is the first version. I am hoping to add additional operations as I develop them. I will be adding a delete_by and force_merge combined operation soon. I am open to any other suggestions.
