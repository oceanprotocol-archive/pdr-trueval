
import glob
import json
import os
from eth_account import Account
from eth_account.signers.local import LocalAccount
from pathlib import Path
from web3 import Web3, HTTPProvider, WebsocketProvider
from web3.middleware import construct_sign_and_send_raw_middleware
from os.path import expanduser
home = expanduser("~")

rpc_url = os.environ.get("RPC_URL")
assert rpc_url is not None, "You must set RPC_URL environment variable"
private_key = os.environ.get("PRIVATE_KEY")
assert private_key is not None, "You must set PRIVATE_KEY environment variable"
assert private_key.startswith("0x"), "Private key must start with 0x hex prefix"

# instantiate Web3 instance
w3 = Web3(Web3.HTTPProvider(rpc_url))
account: LocalAccount = Account.from_key(private_key)
owner = account.address
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))


class PredictorContract:
    def __init__(self, address):
        self.contract_address = w3.to_checksum_address(address)
        self.contract_instance = w3.eth.contract(address=w3.to_checksum_address(address), abi=get_contract_abi('ERC20Template3'))
    
    def soonest_block_to_predict(self,block):
        return self.contract_instance.functions.soonestBlockToPredict(block).call()
    
    def get_current_epoch(self):
        return self.contract_instance.functions.curEpoch().call()
    
    def submit_trueval(self,true_val,block,float_value,cancel_round):
        gasPrice = w3.eth.gas_price
        try:
            tx = self.contract_instance.functions.submitTrueVal(block,true_val,float_value,cancel_round).transact({"from":owner,"gasPrice":gasPrice})
            print(f"Submit get receipt")
            print(tx)
            receipt = w3.eth.wait_for_transaction_receipt(tx)
            return receipt
        except: 
            return None
    
    def redeem_unused_slot_revenue(self,block):
        gasPrice = w3.eth.gas_price
        try:
            tx = self.contract_instance.functions.redeemUnusedSlotRevenue(block).transact({"from":owner,"gasPrice":gasPrice})
            print("redeem_unused_slot_revenue get receipt")
            receipt = w3.eth.wait_for_transaction_receipt(tx)
            return receipt
        except:
            return None
    
    def get_blocksPerEpoch(self):
        return self.contract_instance.functions.blocksPerEpoch().call()
    
    def get_block(self,block):
        return w3.eth.get_block(block)
    
def get_contract_abi(contract_name):
    """Returns the abi for a contract name."""
    path = get_contract_filename(contract_name)

    if not path.exists():
        raise TypeError("Contract name does not exist in artifacts.")

    with open(path) as f:
        data = json.load(f)
        return data['abi']

def get_contract_filename(contract_name):
    """Returns abi for a contract."""
    contract_basename = f"{contract_name}.json"

    # first, try to find locally
    address_filename = os.getenv("ADDRESS_FILE")
    path = None
    if address_filename:
        address_dir = os.path.dirname(address_filename)
        root_dir = os.path.join(address_dir, "..")
        os.chdir(root_dir)
        paths = glob.glob(f"**/{contract_basename}", recursive=True)
        if paths:
            assert len(paths) == 1, "had duplicates for {contract_basename}"
            path = paths[0]
            path = Path(path).expanduser().resolve()
            assert (
                path.exists()
            ), f"Found path = '{path}' via glob, yet path.exists() is False"
            return path
    # didn't find locally, so use use artifacts lib
    #path = os.path.join(os.path.dirname(artifacts.__file__), "", contract_basename)
    #path = Path(path).expanduser().resolve()
    #if not path.exists():
    #    raise TypeError(f"Contract '{contract_name}' not found in artifacts.")
    return path