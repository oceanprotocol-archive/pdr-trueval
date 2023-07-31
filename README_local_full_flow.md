
WARNING:  Highly WIP, most likely you will get errors or branches are out of date, etc.. 

# Overview

This is the end-to-end flow for using Predictoor.

**First: get components running**, via one of:
  - [Full barge](#full-barge-approach) -- For dapp devs not changing backend
  - [Partial barge](#partial-barge-approach) -- For backend devs to easily change backend components

**Then: [observe](#observe)** them running!

**Finally: [customize](#customize)** backend for non-random truevals, predictions, and trades.

# Full Barge Approach

This flows runs everything in barge (including pdr-trader, pdr-trueval, pdr-predictoor and pdr-publisher)
Useful for UI developers, when they don't care about data, as long it's there (some random values are enough)

Open new terminal, call it "barge".

### Terminal 1: Barge

In (terminal 1) bash console:
```console
# Install
export ADDRESS_FILE="${HOME}/.ocean/ocean-contracts/artifacts/address.json"
git clone https://github.com/oceanprotocol/barge.git
cd barge
git checkout predictoor

# always fetch the latest versions. Eg check hub.docker.com/r/oceanprotocol/ocean-contracts/tags
docker pull oceanprotocol/ocean-contracts:FIXME
docker pull oceanprotocol/subgraph:FIXME
docker pull oceanprotocol/pdr-trader:v0.0.1
docker pull oceanprotocol/pdr-trueval:v0.0.1
docker pull oceanprotocol/pdr-predictoor:v0.0.1
docker pull oceanprotocol/pdr-publisher:v0.0.1
docker pull oceanprotocol/pdr-dfbuyer:v0.0.1

# Run
./start_ocean.sh --predictoor --with-pdr-trueval --with-pdr-trader --with-pdr-predictoor --with-pdr-publisher --with-pdr-dfbuyer
```

This will start barge with a custom version of ganache (auto-mine a block every 12 sec), contracts (predictoor), subgraph (predictoor)
- WARNING!! Barge will start more slowly. Deploying contracts takes a couple of minutes.
- Watch the output to know when to proceed further or check if file "/ocean-subgraph/ready" exists.

After barge is deployed, pdr* will wait for two epochs to pass, before consuming values. Wait for that first :)


# Partial Barge Approach

This flows runs only contracts and subgraph in barge.
Useful for pdr-* developers

Create five terminals, for:
1. [barge](#Terminal-1-Barge)
2. [ocean.py](#Terminal-2-oceanpy)
3. [pdr-trueval](#Terminal-3-pdr-trueval)
4. [pdr-predictoor](#Terminal-4-pdr-predictoor)
5. [pdr-trader](#Terminal-5-pdr-trader)

Let's go through each terminal in order.


### Terminal 1: Barge

In (terminal 1) bash console:
```console
# clone barge
export ADDRESS_FILE="${HOME}/.ocean/ocean-contracts/artifacts/address.json"
git clone https://github.com/oceanprotocol/barge.git
cd barge

# use predictoor branch
git checkout predictoor

# ensure the line below has newest version at hub.docker.com/r/oceanprotocol/ocean-contracts/tags
docker pull oceanprotocol/ocean-contracts:predictoor2

# ensure the line below has newest version at https://hub.docker.com/r/oceanprotocol/subgraph/tags
docker pull oceanprotocol/subgraph:predictoor

# start!
./start_ocean.sh --predictoor
```

This will start barge with a custom version of ganache (auto-mine a block every 12 sec), contracts (predictoor), subgraph (predictoor)
WARNING:   Barge will start more slowly, deploying contracts takes a couple of minutes.  Watch the output to know when to proceed further or check if file "/ocean-contracts/artifacts/ready" exists

Go to next step when barge is ready and contracts are deployed

## Terminal 2: ocean.py

Since there is no easy way now to create a template3 datatoken, we will use ocean.py.  

Note: This flow will be replaced once we advance will all components into a more MVP state.

In bash console:
```console
# Install
git clone https://github.com/oceanprotocol/ocean.py
cd ocean.py
git checkout predictoor-with-barge
sudo apt-get update -y
sudo apt-get install -y
sudo apt-get install -y python3-dev gcc 
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_dev.txt

# Set envvars
export ADDRESS_FILE="${HOME}/.ocean/ocean-contracts/artifacts/address.json"
export OPF_DEPLOYER_PRIVATE_KEY="0xc594c6e5def4bab63ac29eed19a134c130388f74f019bc74b8f4389df2837a58"
export PREDICTOOR_PRIVATE_KEY="0xef4b441145c1d0f3b4bc6d61d29f5c6e502359481152f869247c7a4244d45209"
export TRADER_PRIVATE_KEY="0x8467415bb2ba7c91084d932276214b11a3dd9bdb2930fefa194b666dd8020b99"

# Open Python terminal
python
```

Inside the Python terminal:
```python
import brownie
from brownie.network import accounts as br_accounts
import os
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.models.datatoken_base import DatatokenBase
from ocean_lib.web3_internal.utils import connect_to_network
from ocean_lib.ocean.util import from_wei, to_wei
from ocean_lib.example_config import get_config_dict
from ocean_lib.web3_internal.constants import ZERO_ADDRESS, MAX_UINT256
# add accounts
deployer = br_accounts.add(os.getenv("OPF_DEPLOYER_PRIVATE_KEY"))
predictoor = br_accounts.add(os.getenv("PREDICTOOR_PRIVATE_KEY"))
trader = br_accounts.add(os.getenv("TRADER_PRIVATE_KEY"))
connect_to_network("development")
ADDRESS_FILE = "~/.ocean/ocean-contracts/artifacts/address.json"
address_file = os.path.expanduser(ADDRESS_FILE)
print(f"Load contracts from address_file: {address_file}")
config = get_config_dict("development")
config["ADDRESS_FILE"] = address_file
ocean = Ocean(config)
OCEAN = ocean.OCEAN_token

# transfer OCEAN to predictoor & trader
OCEAN.transfer(predictoor.address, to_wei(2000.0), {"from": deployer})
OCEAN.transfer(trader.address, to_wei(2000.0), {"from": deployer})

#create NFT
data_nft = ocean.data_nft_factory.create({"from": deployer}, "DN", "DN")

#settings for template 3
S_PER_MIN = 60
S_PER_HOUR = 60 * 60
# for our ganache, have one epoch per minute (every 60 blocks)
s_per_block = 1  # depends on the chain
s_per_epoch = 1 * S_PER_MIN
s_per_subscription = 24 * S_PER_HOUR
min_predns_for_payout = 3  # ideally, 100+
stake_token = OCEAN
DT_price = 2 # priced in OCEAN

#create template3
initial_list = data_nft.getTokensList()
data_nft.createERC20(
        3,
        ["ETH-USDT", "ETH-USDT"],
        [deployer.address, deployer.address, deployer.address, OCEAN.address, OCEAN.address],
        [MAX_UINT256, 0, s_per_block, s_per_epoch, s_per_subscription, 30],
        [],
        {"from": deployer},
    )
new_elements = [
        item for item in data_nft.getTokensList() if item not in initial_list
    ]
assert len(new_elements) == 1, "new datatoken has no address"
DT = DatatokenBase.get_typed(config, new_elements[0])
DT.setup_exchange({"from": deployer}, to_wei(DT_price))
print("Done")
```

### Terminal 3: pdr-trueval

In bash console:
```console
# Install
git clone https://github.com/oceanprotocol/pdr-trueval.git
cd pdr-trueval
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set envvars
export ADDRESS_FILE="${HOME}/.ocean/ocean-contracts/artifacts/address.json"
export RPC_URL=http://127.0.0.1:8545
export SUBGRAPH_URL="http://172.15.0.15:8000/subgraphs/name/oceanprotocol/ocean-subgraph"
export PRIVATE_KEY="0xc594c6e5def4bab63ac29eed19a134c130388f74f019bc74b8f4389df2837a58"

# Run
python3 main.py
```


### Terminal 4: pdr-predictoor

In bash console:
```console
# Install
git clone https://github.com/oceanprotocol/pdr-predictoor.git
cd pdr-predictoor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set envvars
export ADDRESS_FILE="${HOME}/.ocean/ocean-contracts/artifacts/address.json"
export RPC_URL=http://127.0.0.1:8545
export SUBGRAPH_URL="http://172.15.0.15:8000/subgraphs/name/oceanprotocol/ocean-subgraph"
export PRIVATE_KEY="0xef4b441145c1d0f3b4bc6d61d29f5c6e502359481152f869247c7a4244d45209"

# Run
python3 main.py
```

### Terminal 5: pdr-trader

In bash console:
```console
# Install
git clone https://github.com/oceanprotocol/pdr-trader.git
cd pdr-trader
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set envvars
export ADDRESS_FILE="${HOME}/.ocean/ocean-contracts/artifacts/address.json"
export RPC_URL=http://127.0.0.1:8545
export SUBGRAPH_URL="http://172.15.0.15:8000/subgraphs/name/oceanprotocol/ocean-subgraph"
export PRIVATE_KEY="0x8467415bb2ba7c91084d932276214b11a3dd9bdb2930fefa194b666dd8020b99"

# Run
python3 main.py
```

# Observe

Now, relax & watch as pdr-predictoor is submiting random predictions , pdr-trueval submits random true_vals for each epoch and pdr-trader signals trades.

You can query [subgraph](http://172.15.0.15:8000/subgraphs/name/oceanprotocol/ocean-subgraph/graphql) and see populated data  [PR](https://github.com/oceanprotocol/ocean-subgraph/pull/678) here for entities 

# Customize

Here's what you can do next.

Customize [pdr-trueval](https://github.com/oceanprotocol/pdr-trueval) to submit real data, not random.

Customize [pdr-predictoor](https://github.com/oceanprotocol/pdr-predictoor) to submit real predictions, not random.

Customize [pdr-trader](https://github.com/oceanprotocol/pdr-trader) to actually trade.

# Appendix: On Private Keys

This file uses these private keys from barge:
 - OPF_DEPLOYER_PRIVATE_KEY:  `0xc594c6e5def4bab63ac29eed19a134c130388f74f019bc74b8f4389df2837a58`  - contracts owner, ocean token owner
 - PREDICTOOR_PRIVATE_KEY: `0xef4b441145c1d0f3b4bc6d61d29f5c6e502359481152f869247c7a4244d45209`  - predictoor
 - TRADER_PRIVATE_KEY: `0x8467415bb2ba7c91084d932276214b11a3dd9bdb2930fefa194b666dd8020b99`  - trader
