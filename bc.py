#import functools
from functools import reduce
import hashlib as hl
import json
from collections import OrderedDict

MINING_REWARD = 10
genesis_block = {
        'previous_hash': ''
        ,'index': 0
        ,'transactions': []
        ,'nonce': 0
    }
bc = [genesis_block]
open_transactions = []
owner = "decoder"
participants = {owner}

def load_data():
    global bc
    global open_transactions
    with open('bc.txt', 'r') as f:
        file_content = f.readlines()
        bc = json.loads(file_content[0][:-1])
        upd_bc = []
        for block in bc:
            updated_block = {
                'previous_hash': block['previous_hash']
                ,'index': block['index']
                ,'transactions': [OrderedDict(
                    [('sender', txn['sender'])
                    ,('receiver', txn['receiver'])
                    ,('amount', txn['amount'])
                    ]
                    ) for txn in block['transactions']]
                ,'nonce': block['nonce']
            }
            upd_bc.append(updated_block)
        bc = upd_bc
        open_transactions = json.loads(file_content[1])
        upd_opn_txns = []
        for optn in open_transactions:
            tx = OrderedDict([('sender', optn['sender']), ('receiver', optn['receiver']), ('amount',optn['amount'])])
            upd_opn_txns.append(tx)
        open_transactions = upd_opn_txns

load_data()

def save_data():
    with open('bc.txt', 'w') as f:
        f.write(json.dumps(bc))
        f.write("\n")
        f.write(json.dumps(open_transactions))

def get_last_bc_val():
    if len(bc) < 1:
        return None
    return bc[-1]

def verify_txn(txn):
    sender_bal = get_balance(txn['sender'])
    return sender_bal >= txn['amount']

def add_txn(sender = owner, recipient=owner, amount=1.0):
    # transaction = {
    #     'sender' : sender,
    #     'receiver' : recipient, 
    #     'amount' : amount
    # }
    transaction = OrderedDict([('sender', sender), ('receiver', recipient), ('amount', amount)])
    if verify_txn(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False
#end add_txn

def hash_a_block(block_to_hash):
    return hl.sha256(json.dumps(block_to_hash, sort_keys=True).encode()).hexdigest()

def get_balance(participant):
    amount_sent = 0
    amount_received = 0
    
    tx_sender = [[ txn['amount'] for txn in b['transactions'] if txn['sender'] == participant] for b in bc]
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    """
    Logic to retrieve each added txn via a loop which will be rewritten into a reduce function
    for tx in tx_sender:
        if len(tx) > 0:
            for rec in tx:
                amount_sent += rec
    """
    #amount_sent = reduce(lambda x, y: x + y, reduce(lambda x, y: x + y, tx_sender), 0)
    """Using sum function"""
    amount_sent = reduce(lambda x, y: x + sum(y), tx_sender, 0)

    tx_rec = [[ txn['amount'] for txn in b['transactions'] if txn['receiver'] == participant] for b in bc]
    """
    for tx in tx_rec:
        #print(tx[0])
        if len(tx) > 0:
            for rec in tx:
                amount_received += rec
    """
    amount_received = reduce(lambda x, y: x + y, reduce(lambda x, y: x + y, tx_rec), 0)
    
    return amount_received - amount_sent
    
def verify_proof(txns, prev_hash, nonce):
    str_to_hash = (str(txns) +str(prev_hash) + str(nonce)).encode()
    hashed_str = hl.sha256(str_to_hash).hexdigest()
    print(str_to_hash)
    print(hashed_str)
    return hashed_str[0:2] == '00'

def proof_of_work():
    last_block = bc[-1]
    last_block_hash = hash_a_block(last_block)
    nonce = 0
    while not verify_proof(open_transactions, last_block_hash, nonce):
        nonce += 1
    return nonce

def mine_block():
    last_block = bc[-1]
    block_hash = hash_a_block(last_block)

    nonce = proof_of_work()

    # reward_txn = {
    #     'sender': 'MINING',
    #     'receiver': owner,
    #     'amount': MINING_REWARD
    # }
    reward_txn = OrderedDict([('sender', 'MINING'), ('receiver', owner), ('amount', MINING_REWARD)])
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_txn)

    block = {
        'previous_hash': block_hash
        ,'index': len(bc)
        ,'transactions': copied_transactions
        ,'nonce': nonce
    }
    bc.append(block)
    return True

def get_txn_val():
    tx_recepient = input("Enter recepient: ")
    tx_amount = float(input("Txn amount: "))
    return (tx_recepient, tx_amount)

def get_user_choice():
    return input("Choice: ")

def print_bc_elements():
    for b in bc:
        print(b)
        print("-" * 40)
    else:
        print (bc)
        print("=" * 40)

def verify_chain():
    for (index, block) in enumerate(bc):
        if index == 0:
            continue
        if block['previous_hash'] != hash_a_block(bc[index - 1]):
            return False
        print(index)
        print(block['transactions'])
        if not verify_proof(block['transactions'][:-1], block['previous_hash'], block['nonce']):
            print(str(index) + " Invalid Proof of work!!!")
            return False
    return True

def verify_all_txns():
    return all([verify_txn(tx) for tx in open_transactions])

wait_for_input = True

while wait_for_input:
    print("\n")
    print("-" * 40)
    print("Please choose")
    print("-" * 40)
    print("1. Add a new transaction value.")
    print("2. Mine a new block.")
    print("3. Output the block chain.")
    print("4. Print participants")
    print("5. Verify all transactions.")
    print("h. Manipulate the blockchain.")
    #print("v. Verify the blockchain.")
    print("q. Exit.")
    
    user_choice = get_user_choice()
    
    if user_choice == '1':
        (recipient, amount) = get_txn_val()
        if add_txn(recipient=recipient, amount=amount):
            print("Added Transaction")
        else:
            print("Add Transaction Failed")
        print(open_transactions)

    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    
    elif user_choice == '3':
        print_bc_elements()
        
    elif user_choice =='4':
        print(participants)

    elif user_choice =='5':
        print(verify_all_txns())

    elif user_choice == 'h':
        if len(bc) > 0:
            bc[0] = {
                'previous_hash': ''
                ,'index': 0
                ,'transactions': [{
                    'sender' : 'Don',
                    'receiver' : 'Basha', 
                    'amount' : 80_000_000
                }]
            }

    elif user_choice == 'q':
        wait_for_input = False

    else:
        print("\nInvalid Choice, enter again\n")

    if not verify_chain():
        print( "Blockchain compromised!!!")
        #break
    else:
       print( "Blockchain verified")

print("Balance of {name} is: {balance:.6f}".format(name="decoder", balance=get_balance('decoder')))
#print(get_balance('decoder'))
