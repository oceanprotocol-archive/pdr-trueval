import ccxt


def get_true_val(topic, initial_timestamp, end_timestamp):
    """ Given a topic, Returns the true val between end_timestamp and initial_timestamp
        Topic object looks like:
        
        {
            "name":"ETH-USDT",
            "address":"0x54b5ebeed85f4178c6cb98dd185067991d058d55",
            "symbol":"ETH-USDT",
            "blocks_per_epoch":"60",
            "blocks_per_subscription":"86400",
            "last_submited_epoch":0,
            "pair":"eth-usdt",
            "base":"eth",
            "quote":"usdt",
            "source":"kraken",
            "timeframe":"5m"
        }
    
    """
    try:
        exchange_class = getattr(ccxt, topic["source"])
        exchange_ccxt = exchange_class()
        price_initial = exchange_ccxt.fetch_ohlcv(topic['pair'], "1m", since=initial_timestamp, limit=1)
        price_end = exchange_ccxt.fetch_ohlcv(topic['pair'], "1m", since=end_timestamp, limit=1)
        return (price_end[0][1] >= price_initial[0][1],price_end[0][1],False)
    except Exception as e:
        return(False,0,True)
