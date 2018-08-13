### Introduction
- An airdrop program, applicable for various kinds of tokens.
- It will check all the blocks between `BEGIN_HEIGHT` and `END_HEIGHT` (including `BEGIN_HEIGHT` and `END_HEIGHT`), to find out specific transactions in each block.

### USAGE
1. Execute `pip3 install -r requirements.txt` in the project.
2. Open `parsing blocks.py` and change the value of `URL`, `BEGIN_HEIGHT`, `END_HEIGHT`.  
Notice that BEGIN_HEIGHT should be less than END_HEIGHT. 
3. Run `python3 parsing_blocks.py` then a file named `addresses.csv` will appear in the project root path. It has two columns: the first is erc20 addresses and the second is values.
4. Open `config.py` to change api_endpoiont, contranct address and wallet address.
5. Run `python3 main.py [CSV_FILE_PATH]` to execute airdrop. 
