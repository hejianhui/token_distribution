import sys
from web3 import Web3


def process_addresses(file_name):
    f = open('./' + file_name, 'r', encoding='utf-8-sig')  # remove '\uffe'
    addresses_list = [line.strip('\n').split(',') for line in list(f)]
    f.close()

    valid_addresses = open('./valid_addresses.csv', 'w')
    invalid_addresses = open('./invalid_addresses.csv', 'w')
    for to_send in addresses_list:
        to_send[0] = "".join(to_send[0].split())  # remove '\xa0'
        if Web3.isAddress(to_send[0]):
            valid_addresses.write(Web3.toChecksumAddress(to_send[0]) + ',' + to_send[1] + '\n')
        else:
            print('not a valid address in airdrop list 1:', to_send[0])
            print(to_send)
            invalid_addresses.write(to_send[0] + ',' + to_send[1] + '\n')

    valid_addresses.close()
    invalid_addresses.close()


if __name__ == '__main__':
    process_addresses(sys.argv[1])
