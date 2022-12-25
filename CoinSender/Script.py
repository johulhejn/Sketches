from web3 import Web3
from eth_utils import ValidationError
import json

binance_mainnet_rpc_url = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(binance_mainnet_rpc_url))
wallet_address = "0xf035bcd04b399fe35f3f253e801898f5fD4e075d"  # your address
twt_contract_address = Web3.toChecksumAddress('0x4b0f1812e5df2a09796481ff14017e6005508003')  # TWT token

# initialization of TWT contract
ERC20_ABI = json.load(open('ERC20_ABI.json'))
twt_contract = web3.eth.contract(twt_contract_address, abi=ERC20_ABI)

web3.eth.account.enable_unaudited_hdwallet_features()

with open('mnemo') as m:
    for line in m:
        MNEMONIC = line.strip().lower()
        try:
            account = web3.eth.account.from_mnemonic(MNEMONIC)
        except ValidationError:
            print('Wrong mnemonic', MNEMONIC)
            continue
        private_key = account.privateKey  # hex address
        someone_address = account.address
        balance_of_token = twt_contract.functions.balanceOf(someone_address).call()
        print(balance_of_token)
        if balance_of_token <= 0:
            print(MNEMONIC, 'is empty')
            continue

        dict_transaction = {
            'chainId': web3.eth.chain_id(),
            'from': someone_address,
            'gasPrice': web3.eth.gas_price(),
            'nonce': web3.eth.getTransactionCount(someone_address)
        }

        gas = 20000
        amtToSend = balance_of_token - gas
        transaction = twt_contract.functions.transfer(someone_address, amtToSend).buildTransaction(dict_transaction)
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
