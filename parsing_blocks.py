import requests
import json
from web3 import Web3

URL = 'http://127.0.0.1:20336'
BEGIN_HEIGHT = 167000
END_HEIGHT = 169419


def check_duplicate(airdrop_addresses):
    no_duplicate_addresses = list()
    print('airdrop address:', airdrop_addresses)
    for airdrop_address in airdrop_addresses:
        find_flag = 0
        print('checking airdrop transaction', airdrop_address['tx_hash'])
        print('checking airdrop transaction height', airdrop_address['height'])
        for block in all_inputs[(airdrop_address['height'] - BEGIN_HEIGHT + 1):]:
            for tx in block:
                for vin in tx:
                    if vin == airdrop_address['tx_hash']:
                        print('duplicated hash found:', airdrop_address)
                        print('duplicated hash found, input is:', vin)
                        find_flag = 1

        if not find_flag:
            print('no duplicate input after.', airdrop_address)
            no_duplicate_addresses.append(airdrop_address)
        else:
            print('duplicate input find.', airdrop_address)
    return no_duplicate_addresses

# print('no duplicate:', no_duplicate_addresses)


addresses_set = list()
invalid_address_set = list()
all_inputs = list()
request_height = BEGIN_HEIGHT
while True:
    block_txs = list()
    postdata = json.dumps({'method': 'getblockbyheight', 'params': {'height': request_height}})
    response = requests.post(URL, data=postdata, headers={'Content-Type': 'application/json'}).json()
    result = response['result']
    print("current height:", request_height)
    request_height += 1

    for tx in result['tx']:
        if tx['type'] == 2:

            input_txs = [vin['txid'] for vin in tx['vin']]
            block_txs.append(input_txs)

            for attribute in tx['attributes']:
                if attribute['usage'] == 0x81:
                    data_decoded = bytes.fromhex(attribute['data']).decode()
                    if data_decoded.startswith('AIRDROP'):
                        print(data_decoded)
                        erc20_address = data_decoded.split(':')[-1]
                        vout_total = sum(float(vout['value']) for vout in tx['vout'])
                        # validate address
                        if not Web3.isAddress(erc20_address):
                            invalid_address_set.append([erc20_address, str(result['height']), str(vout_total)])
                            continue
                        print('erc20 address:', erc20_address)
                        print('tx hash:', tx['hash'])
                        print("total value:", vout_total)
                        addresses_set.append({
                            'address': erc20_address,
                            'total_value': vout_total,
                            'height': result['height'],
                            'tx_hash': tx['hash'],
                            'input_txids': input_txs
                        })

    all_inputs.append(block_txs)
    if request_height == END_HEIGHT + 1:
        break

print('all inputs:', all_inputs)
print('address set:', addresses_set)
no_dup = check_duplicate(addresses_set)
print(no_dup)
with open('./addresses.csv', 'w') as f:
    for item in no_dup:
        print('this item:', item)
        f.write(item['address'] + ',' + str(item['total_value']) + '\n')

with open('./invalid_addresses.csv', 'w') as f:
    for item in invalid_address_set:
        f.write(','.join(item) + '\n')
