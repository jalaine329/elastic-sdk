# elastic-sdk
Python and some bash scripts used to automate various management, administration and troubleshooting tasks

# Python Scripts

## Description
This project is serving as a repository for my python scripts used for managing, administering, monitoring and troubleshooting elasticsearch clusters. At this point this project will be focusing on Elasticsearch administration and monitoring efforts.

Information about each of the scripts can be found in the "Usage" section.

## Installation
This is going to be unique to the environment you will be executing these scripts from. They have been created to be environment agnostic. As long as you have python installed along w/ the Elasticsearch python SDK you should be fine. I would suggest visiting the following website in order to properly install the SDK: [elastic-py docs](https://elasticsearch-py.readthedocs.io/en/v8.10.1/). 

## Usage
In this section you will be able to find a brief explanation of the purpose and proper usage of each of the scripts this project contains.

### menu.py
This will eventually be an application that allows you to chose from each of the different python scripts that make up this project. Most of these scripts serve some kind of administration, monitoring or troubleshooting function. This application will give you access to all these functions in one place and allow you to decide what type of function you would like to perform and on which cluster. At this point it is just the ilm_assess_share, shardfinder_share scripts, apikeys_share.py and monitor_share.py but as more functionality is added I will update this section to reflect where the application is at.

The use of this script should hopefully be straight forward. When you execute the script you will be asked what you want to do and you will be given a list of the options that you have. Once you select the function you would like to perform you will select which cluster you would like to perform it on and on down the line as you get into the specifics of each function.

### time_conversion.py
Small script to convert time from linux ms timestamp to something a bit more readable

### monitor_share.py
This script creates a quick report of the overall health of any cluster in a list of clusters. When you run this script you will be able to see the overall health of the cluster the percentage of nodes that are online and unassigned shards. Heap usage, CPU utilization by node, shards allocated and disk percent per node are also included. A good quick way of determining if anything major is going wrong with the cluster.

### ilm_assess_share.py
This script will create two reports that will help paint a clear picture of the Index Lifecycle Policies on the selected cluster. The first is a .csv file that has the information on each individual index that is attached to each of the different ILM policies. Each index also has a field for the amount of data its primary shards have as well as total amount of space on disk used by the index. This will allow for the efficient creation of a pivot table that will allow the creator to see which ILMs are utilizing the most space and any indices that are holding significantly more or less information than their peers. 

The second output is a text file with similar information. The text file shows the name of each ILM all attached indices and their sizes. At the end of each section dedicated to each ILM there is a summary with the ILM name, number of attached templates, number of attached indices and the total disk space that ILM is responsible for. Very similar information to the .csv, but depending on your needs hopefully it provides a little flexibility.

### apikeys_share.py
This script is used to create a report of the api keys that are active in whichever cluster the user decides to query. The report has been configured to eliminate api keys that have been configured for SIEM alerts. It should only return active API keys that have been configured on that cluster and have not expired yet. The next phase of this will be pulling successful or unsuccessful API authentication attempts out of the audit logs of each cluster to determine which API keys are actively being used and which API keys are attempting to authenticate, but have expired.

### shardfinder_share.py
This is the more advanced and dynamic version of shards_per_node.py. This script allows you to choose the cluster you want to focus on and then the specific node from within that cluster that you need to get information on the size of shards on that specific node. This is good for situations where a node is running out of space and the other nodes in the cluster have significantly more free space. In these situations there is often an index that isn't rolling over or the ILM hasn't been properly set up.

### shards_per_node.py
This script is to be used in situations where you have a node within one of the clusters that is running short on space. You can use this script to identify all of the shards on the node along with their size. This should enable you to have a quick look at the sizes of the shards on the node as well as when they were created. If you are able to find a large shard that isn't rolling over properly or a shard that is older than the retention policy dictates you will be able to quickly identify those situations and figure out what you want to do to move forward.

## Roadmap
At this point these scripts are each individual tasks that I am automating. The plan is to condense these scripts into applications where it makes sense. A lot of the scripts that have been included are complimentary and it would be nice to have one location from which to choose from a library of the compiled group of scripts.

## Contributing
I am open to contributions for this project in the form of new scripts that will improve the efficiency of administering or monitoring elasticsearch clusters. If you would like to make a change to any of the existing scripts please let me know.

## Authors and acknowledgment
Alex Laine

## Project status
This project is active. I am currently spending quite a bit of time developing python scripts that help me speed up the time it takes me to administer and monitor clusters. This has been partially a learning experience as well as the easiest solution for me to perform these tasks. The next step of this process will be to convert these scripts to Ansible so that people are able to execute these same tasks without the requirement of having python installed.

