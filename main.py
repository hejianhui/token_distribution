#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from web3 import Web3, HTTPProvider, utils, exceptions
from ethtoken.abi import EIP20_ABI

import sys

from config import *

# test_abi='[{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"who","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"},{"name":"extraData","type":"bytes"}],"name":"approveAndCall","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]'
from csvreader import CsvReader


class ContributeTokens(object):
    def __init__(self, api_endpoint, contract_address, private_key, source_addr):
        self.web3 = Web3(HTTPProvider(api_endpoint))
        self.erc20 = self.web3.eth.contract(address=contract_address, abi=EIP20_ABI)
        self.private_key = private_key
        self.source_addr = self.web3.toChecksumAddress(source_addr)
        self.nonce = -1

        # print(self.web3.personal.importRawKey(private_key,'123456'))
        # print("")

    def transfer(self, address, amount, gas_price):
        """
        Function to transfer amount to the given address
        :param address:
        :param amount:
        :return:
        """
        address = self.web3.toChecksumAddress(address)
        try:
            # validate address
            utils.validation.validate_address(address)
        except exceptions.InvalidAddress as e:
            print(e)
            return

        # Get Nonce
        self.web3.eth.enable_unaudited_features()
        nonce = self.web3.eth.getTransactionCount(self.source_addr)
        print("Current Nonce:{}".format(nonce))
        # Update Nonce if needed
        if self.nonce < nonce:
            self.nonce = nonce
        else:
            # Probably in batch mode, need to auto add nonce.
            self.nonce += 1
        print("Fixed Nonce:{}".format(self.nonce))
        # Get Decimals
        dec = self.erc20.functions.decimals().call()
        # Get Balance
        balance = self.erc20.functions.balanceOf(self.source_addr).call()
        actual_amount = amount * pow(10, dec)
        if actual_amount < balance:
            print("Enough Balance")
            # encoded_amount=encode_single('uint256', int(actual_amount))
            txn_body = self.erc20.buildTransaction(
                {'from': self.source_addr, 'gas': 100000, 'gasPrice': self.web3.toWei(gas_price, 'gwei'),
                 'nonce': self.nonce}).transfer(address, int(actual_amount))
            signed_txn_body = self.web3.eth.account.signTransaction(txn_body, private_key=self.private_key)
            self.web3.eth.sendRawTransaction(signed_txn_body.rawTransaction)
        else:
            print('代币余额不足！')
            raise Exception("Not Enough Balance for transfer!")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: ")
        print("python3 main.py [CSV_FILE_PATH]")
        print("Example: ")
        print("python3 main.py test.csv")
        exit(0)

    else:
        print("Start sending TXs.")
        batch_list = CsvReader(sys.argv[1]).parse()

        handler = ContributeTokens(api_endpoint=api_endpoint, contract_address=contract_address,
                                   private_key=private_key,
                                   source_addr=source_addr)
        for tx in batch_list:
            handler.transfer(tx[0], float(tx[1]), gas_price)
        print("All TX Sent.")
