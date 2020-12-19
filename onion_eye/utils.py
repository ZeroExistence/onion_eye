import datetime as dt

def data_converter(o):
    if isinstance(o, dt.datetime):
        return o.__str__()

def to_dt(o):
    return dt.datetime.fromisoformat(o)
