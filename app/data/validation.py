def validate_quote(q,max_delay_minutes):
    if q.price<=0:return False,'INVALID_PRICE'
    if q.data_timestamp.tzinfo is None or q.received_at.tzinfo is None:return False,'TIMESTAMP_NOT_TIMEZONE_AWARE'
    delay=(q.received_at-q.data_timestamp).total_seconds()
    if delay < -60:return False,'FUTURE_DATA_TIMESTAMP'
    if delay > max_delay_minutes*60:return False,'STALE_DATA'
    return True,'OK'
