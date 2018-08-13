from ethereum.utils import *
import bitcoin
import os
key = os.urandom(32)
private_key = key.hex()
public_key = bitcoin.privkey_to_pubkey(key).hex()
print(private_key)
print(public_key)
address = '0x' + privtoaddr(key).hex()
print(address)
