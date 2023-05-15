import time
import os
import threading
from datetime import datetime, timedelta, timezone
from threading import Thread

from pdr_trueval.trueval import get_true_val

threads_lock = threading.Lock()

class NewTrueVal(Thread):
    def __init__(self,topic,predictor_contract,current_block_num,epoch):
        # execute the base constructor
        Thread.__init__(self)
        # set a default value
        self.values = { "last_submited_epoch": epoch,
                      "contract_address": predictor_contract.contract_address   
                      }
        self.topic = topic
        self.epoch = epoch
        self.predictor_contract = predictor_contract
        self.current_block_num = current_block_num
        

    def run(self):
        """ Get timestamp of previous epoch-2 , get the price """
        """ Get timestamp of previous epoch-1, get the price """
        """ Compare and submit trueval """
        blocks_per_epoch = self.predictor_contract.get_blocksPerEpoch()
        initial_block = self.predictor_contract.get_block((self.epoch-2)*blocks_per_epoch)
        end_block = self.predictor_contract.get_block((self.epoch-1)*blocks_per_epoch)
        slot = (self.epoch-1)*blocks_per_epoch
        
        true_val=get_true_val(self.topic['name'],self.topic['address'],initial_block['timestamp'],end_block['timestamp'])
        print(f"Contract:{self.predictor_contract.contract_address} - Submiting true_val {true_val} for slot:{slot}")
        try:
            self.predictor_contract.submit_trueval(true_val,slot)
        except Exception as e:
                print(e)
                pass    
