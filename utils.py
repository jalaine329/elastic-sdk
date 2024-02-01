import re

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
    
# convert a string to type int in bytes    
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
    
# convert bytes to the appropriate format (B, KB, MB, GB)
def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            break
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} {unit}"

# get user credentials
def get_credentials():
    username = input("Enter your Elasticsearch username: ")
    password = input("Enter you Elasticsearch password: ")
    return username, password
