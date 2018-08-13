import requests
import json
from web3 import utils, exceptions, Web3, HTTPProvider

URL = 'http://127.0.0.1:21336'
BEGIN_HEIGHT = 90000
END_HEIGHT = 97200


def check_duplicate(current_height, tx_hash):
    # print('check dup height:', current_height)
    # print('tx hash:', tx_hash)
    for height in range(current_height + 1, END_HEIGHT):
        print('current check height:', height)
        postdata = json.dumps({'method': 'getblockbyheight', 'params': {'height': height}})
        response = requests.post(URL, data=postdata, headers={'Content-Type': 'application/json'}).json()
        result = response['result']
        for tx in result['tx']:
            for input in tx['vin']:
                print('check, current txid:', input['txid'])
                if input['txid'] == tx_hash:
                    # print('duplicate transaction hash found, tx hash:', tx_hash)
                    return True

    return False


address_set = list()
invalid_address_set = list()
request_height = BEGIN_HEIGHT
while True:
    postdata = json.dumps({'method': 'getblockbyheight', 'params': {'height': request_height}})
    response = requests.post(URL, data=postdata, headers={'Content-Type': 'application/json'}).json()
    result = response['result']
    print("current height:", request_height)
    request_height += 1

    for tx in result['tx']:
        if tx['type'] == 2:
            for attribute in tx['attributes']:
                if attribute['usage'] != 0x00:
                    data_decoded = bytes.fromhex(attribute['data']).decode()
                    if data_decoded.startswith('AIRDROP'):
                        print(data_decoded)
                        erc20_address = data_decoded.split(':')[-1]
                        try:
                            # validate address
                            utils.validation.validate_address(Web3(HTTPProvider('')).toChecksumAddress(erc20_address))
                        except exceptions.InvalidAddress as e:
                            print(e)
                            invalid_address_set.append([erc20_address, str(result['height'])])
                            continue
                        print('erc20 address:', erc20_address)
                        print('tx hash:', tx['hash'])
                        vout_total = 0
                        for vout in tx['vout']:
                            vout_total += float(vout['value'])
                        print(vout_total)
                        if not check_duplicate(result['height'], tx['hash']):
                            address_set.append([erc20_address, str(vout_total), str(result['height'])])
    if request_height == END_HEIGHT + 1:
        break

print(address_set)
with open('./addresses.csv', 'w') as f:
    for item in address_set:
        f.write(','.join(item) + '\n')

with open('./invalid_addresses.csv', 'w') as f:
    for item in invalid_address_set:
        f.write(','.join(item) + '\n')
