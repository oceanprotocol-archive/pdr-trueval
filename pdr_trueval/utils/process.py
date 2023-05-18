import threading
from pdr_trueval.utils.subgraph import get_all_interesting_prediction_contracts
from pdr_trueval.utils.contract import PredictorContract
from pdr_trueval.utils.threads import NewTrueVal


""" Get all intresting topics that we can submit trueval """
topics = get_all_interesting_prediction_contracts()
def process_block(block):
    global topics
    """ Process each contract and see if we need to submit """
    print(f"Got new block: {block['number']}...")
    if not topics:
        topics = get_all_interesting_prediction_contracts()
    threads=[]
    for address in topics:
        topic = topics[address]
        predictor_contract = PredictorContract(address)
        epoch = predictor_contract.get_current_epoch()
        if epoch > topic['last_submited_epoch']:
            """ Let's make a prediction & claim rewards"""
            thr = NewTrueVal(topic,predictor_contract,block["number"],epoch)
            thr.start()
            threads.append(thr)
    """ Wait for all threads to finish"""
    for thr in threads:
        thr.join()
        address=thr.values['contract_address'].lower()
        new_epoch = thr.values['last_submited_epoch']
        topics[address]["last_submited_epoch"]=new_epoch
        


