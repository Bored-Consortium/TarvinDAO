from datetime import datetime, timedelta


def get_end_time(value):
    return str(datetime.today() + timedelta(days=value))

