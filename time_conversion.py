from datetime import datetime

# unix ms timestamp
timestamp_ms = int(input("The timestamp you want to convert: "))

# convert to a datetime obj
datetime_obj = datetime.fromtimestamp(timestamp_ms / 1000.0)

# format as a string (adjust the format as needed)
formatted_datetime = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

print(formatted_datetime)
