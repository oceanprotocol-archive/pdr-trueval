import ccxt


def get_true_val(topic, contract_address, initial_timestamp, end_timestamp):
    """Returns the true val between end_timestamp and initial_timestamp"""
    kraken = ccxt.kraken()

    # question: the topics are given as "ETH-USD" but the API expects "ETH/USD".
    # do we expect the topic in any specific format? can we rely on this replacement?
    topic = topic.replace("-", "/")

    price_initial = kraken.fetch_ohlcv(topic, "1m", since=initial_timestamp, limit=1)
    price_end = kraken.fetch_ohlcv(topic, "1m", since=end_timestamp, limit=1)

    # question: should this part also do something with the contract or just return the value?
    # it is unclear from the specs

    # question: if equal, should we bias for true, false or maybe random?
    return price_end[0][1] >= price_initial[0][1]
