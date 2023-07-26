First cut: it may work, with errors

## Flow
- reads from subgraph list of template3 contracts, this gets list of all template3 deployed contracts
- for every contract, monitors when epoch is changing
- once an epoch is ended, calculate the true_val and submit.


## How to run

For full flow see [README](https://github.com/oceanprotocol/pdr-trueval/blob/main/README_local_full_flow.md)

```bash
export RPC_URL=http://127.0.0.1:8545
export SUBGRAPH_URL="http://172.15.0.15:8000/subgraphs/name/oceanprotocol/ocean-subgraph"
export PRIVATE_KEY="xx"
```
where:
  - you can also export SOURCE_FILTER, TIMEFRAME_FILTER, PAIR_FILTER *(comma-separated lists) to limit predictions based on NFT data. E.g. export PAIR_FILTER=eth-usdt,eth-btc


Install requirements if needed
```bash
pip install -r requirements.txt
```

Start:
```bash
python3 main.py
```
## Additional ENV variables used to filter:

 - PAIR_FILTER = if we do want to act upon only same pair, like  "BTC/USDT,ETH/USDT"
 - TIMEFRAME_FILTER = if we do want to act upon only same timeframes, like  "5m,15m"
 - SOURCE_FILTER = if we do want to act upon only same sources, like  "binance,kraken"
 - OWNER_ADDRS = if we do want to act upon only same publishers, like  "0x123,0x124"

## Fork and customize
  The actual true_val is fetch by calling function get_true_val is in trueval.py.

  We call get_true_val with 4 args:
   - topic:  this is pair object
   - initial_timestamp:   blocktime for begining of epoch - 2
   - end_timestamp:   blocktime for begining of epoch -1

  Function returns true_val, which gets submited to contract

  You need to change the code to support more complex flows. Now, it's based on ccxt


