import ccxt


def get_true_val(topic, contract_address, initial_timestamp, end_timestamp):
    """Returns the true val between end_timestamp and initial_timestamp"""
    kraken = ccxt.kraken()

    topic = topic.replace("-", "/")
    try:
        price_initial = kraken.fetch_ohlcv(topic, "1m", since=initial_timestamp, limit=1)
        price_end = kraken.fetch_ohlcv(topic, "1m", since=end_timestamp, limit=1)
        return (price_end[0][1] >= price_initial[0][1],price_end[0][1],False)
    except Exception as e:
        return(False,0,True)
