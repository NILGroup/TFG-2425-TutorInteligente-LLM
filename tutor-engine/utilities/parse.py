from datetime import datetime

def convert_to_datetime(timestamp_str):
    format = "%Y/%m/%d_%H:%M:%S.%f"
    return datetime.strptime(timestamp_str, "%Y/%m/%d_%H:%M:%S.%f")