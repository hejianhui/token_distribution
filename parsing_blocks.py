import requests
import json

URL = 'http://127.0.0.1:21336'
BEGIN_HEIGHT = 92000
END_HEIGHT = 95000


def check_duplicate(current_height, tx_hash):
    for height in range(current_height + 1, END_HEIGHT):
        postdata = json.dumps({'method': 'getblockbyheight', 'params': {'height': current_height}})
        response = requests.post(URL, data=postdata, headers={'Content-Type': 'application/json'}).json()
        result = response['result']
        for tx in result['tx']:
            for input in tx['vin']:
                if input['txid'] == tx_hash:
                    print('duplicate transaction hash found, tx hash:', tx_hash)
                    return True
        return False


address_set = list()
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
