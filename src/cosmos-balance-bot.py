#!/usr/bin/python3

'''
Reece Williams (Reecepbcups | PBCUPS Validator [$OSMO, $DIG]) | April 21st, 2022
- Twitter & Discord Integration + Endpoints

Install:
- pip install --no-cache-dir -r requirements/requirements.txt

Run:
- python src/cosmos-balance-bot.py

Docker:
- docker build -t reecepbcups/balancebot .
- docker run reecepbcups/balancebot
'''

import datetime
import time
import json
import os
from typing import Dict

# from discord import Webhook, RequestsWebhookAdapter

# from ChainApis import chainAPIs
from pyibc_api import CHAIN_APIS, get_all_chains
from pyibc_utils.convert import simplify_balances_dict
from pyibc_chain.queries import get_balances
from utils.notifications import discord_notification

NOTIFIERS = { # {wallet: { "note: "optional note", "warning": 50.0, "low": 10.0}}
    "good": [0x00FF00,"https://image.similarpng.com/very-thumbnail/2021/05/Checkmark-green-tick-isolated-on-transparent-background-PNG.png"],
    "warning": [0xFFFF00,"https://media.istockphoto.com/vectors/warning-sign-yellow-exclamation-mark-icon-danger-sign-attention-sign-vector-id1165690157?k=20&m=1165690157&s=612x612&w=0&h=nU2Iow3Lbg66noibsRdlZkvwnHwEC6mOddnY024i3mQ="],
    "low": [0xFF0000,"https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Cross_red_circle.svg/2048px-Cross_red_circle.svg.png"],
}


def main():
    print("Initial run...")
    runChecks()

    if USE_PYTHON_RUNNABLE: 
        # Can't use schedule bc its thread blocking = kuber thinks it dies
        prev = time.time()        
        while True:
            now = time.time()
            if now - prev > SCHEDULE_MINUTES*60:            
                prev = now
                print("Checks would be run here")
                runChecks()

# Don't touch below --------------------------------------------------

PREFIX = "COSMOSBALBOT" # cosmos balance bot docker prefix. Useful for sensitive info
def getENV(path, default):    
    value = os.getenv(f"{PREFIX}_{path}", default)
    return value

def str2bool(v) -> bool: 
    return str(v).lower() in ("yes", "true", "t", "1")

with open('secrets.json', 'r') as f:
    secrets = json.load(f)

    DEBUGGING = bool(getENV("DEBUGGING", False))

    DISCORD = secrets["DISCORD"]["ENABLED"]    

    USE_PYTHON_RUNNABLE = bool(getENV(f"SCHEDULER_USE_PYTHON_RUNNABLE", secrets["SCHEDULER"]["USE_PYTHON_RUNNABLE"]))
    SCHEDULE_MINUTES = int(getENV(f"SCHEDULER_IF_ABOVE_IS_TRUE_HOW_MANY_MINUTES_BETWEEN_CHECKS", secrets["SCHEDULER"]["IF_ABOVE_IS_TRUE_HOW_MANY_MINUTES_BETWEEN_CHECKS"]))

    WALLETS = secrets['WALLETS']
    _wallets = os.getenv(f"{PREFIX}_WALLETS") # only works on local linmux docker run
    if _wallets is not None: # grabs from file, but if there is an env variable it uses that
        WALLETS = dict(eval(_wallets))['WALLETS']
        print("using" + _wallets + " from the env variable")
    print(WALLETS)

    SIMPLIFY_UDENOM = secrets['SIMPLIFY_UDENOM_VALUES_TO_READABLE'] # will divided values by 1_000_000 if true
    
    NOTIFY_GOOD_BALANCES = str2bool(os.getenv('COSMOSBALBOT_NOTIFY_GOOD_BALANCES', str(secrets['NOTIFY_GOOD_BALANCES'])))
    # print("value: " + f"{NOTIFY_GOOD_BALANCES}")

    # loop through all os variables & print out keys for debugging
    for key in os.environ:
        if key.startswith(PREFIX):
            print(f"\tOUR KEYS: {key} = {os.getenv(key)}")    

    if DISCORD:
        discSecrets = secrets['DISCORD']
        WEBHOOK_URL = os.getenv(f"{PREFIX}_DISCORD_WEBHOOK_URL", discSecrets['WEBHOOK_URL'])
        USERNAME = discSecrets['USERNAME']

def getStatusValues(walletAddress, balance: float):
    '''
    Gets the status values of the account relative to thresholds in secrets.json.
    & returns all these values for a given wallets check
    '''
    WARNING_LEVEL = WALLETS[walletAddress]['warning']
    LOW_LEVEL = WALLETS[walletAddress]['low']

    status = "" # good, warning, low
    titleMsg = "" # ex: "CHAIN LOW (<100)"

    if balance > WARNING_LEVEL:
        status = "good"
        titleMsg += f"{status.upper()} ( >{WARNING_LEVEL} )"
    elif balance < WARNING_LEVEL and balance > LOW_LEVEL:
        status = "warning"
        titleMsg += f"{status.upper()} ( <{WARNING_LEVEL} )"
    else:
        status = "low"
        titleMsg += f"{status.upper()} ( <{LOW_LEVEL} )"

    HEX_COLOR = NOTIFIERS[status][0]
    IMG_URL = NOTIFIERS[status][1]

    return status, titleMsg, HEX_COLOR, IMG_URL

def getAddressNote(walletAddress) -> str:
    note = ""
    if "note" in WALLETS[walletAddress]:
        note = WALLETS[walletAddress]["note"]
    return note

def postUpdate(chain, walletAddress, balanceDict):
    if balanceDict == {}:
        return

    balance = balanceDict[list(balanceDict.keys())[0]] # main coin balance
    if isinstance(balance, str):
        balance = balance.replace(',', '')

    status, titleMsg, hexColor, imgUrl = getStatusValues(walletAddress, float(balance))
    
    # if we only want to show warning & low balances, this skips good balances beig shown
    if NOTIFY_GOOD_BALANCES == False and status == "good":
        print(f"{walletAddress} is good, notify good balances is just off")
        return {}

    betterBalance = ""
    for d in balanceDict.keys():
        betterBalance += f"{d}: {balanceDict[d]}\n"

    # A short note/desc of the account. Returns "" if none is found
    note = getAddressNote(walletAddress)

    message = f"{str(chain).upper()} {titleMsg} | {walletAddress} | {betterBalance} |{note}"
    print(message.replace("\n", "\\n"))

    # print("Exit 0 in post_update for debugging"); exit(0)
    try:
        if DISCORD:
            values={"Balance": [f'{betterBalance}', False]}
            if len(note) > 0:
                values["Note"] = [f"{note}", False]
            if DEBUGGING:                 
                values["DEBUGGING"] = [f"{SCHEDULE_MINUTES=}", False]

            discord_notification(
                url=WEBHOOK_URL, 
                title=f"{chain.upper()} BALANCE {titleMsg}", 
                description=walletAddress, 
                color=hexColor, 
                values=values, 
                imageLink=imgUrl, 
                footerText=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            )

    except Exception as err:
        print( str(err) + " OR Tweet failed due to being duplicate")

def santizeBalances(balances: Dict) -> Dict:
    sanitized = {}
    for denom, balance in balances.items():
        if denom.startswith('ibc/'):
            continue # skip non native assets
        elif denom.startswith('gamm'):
            continue # skip osmo pools
        sanitized[denom] = balance
    return sanitized

def runBalanceCheckForWallet(chain, wallet):
    balances = get_balances(chain, wallet)
    simplified = simplify_balances_dict(balances)
    sanitized = santizeBalances(simplified)
    postUpdate(chain, wallet, sanitized)

def runChecks():   
    print("Running checks...") 

    # Go through all wallets & ChainAPis matching. If the wallet starts with a ChainAPI keyname
    # check the balance of that wallet using the given LCD API
    checkedWallets = []
    for wallet in WALLETS:
        for chain in get_all_chains():
            if wallet.startswith(chain):
                checkedWallets.append(wallet)
                runBalanceCheckForWallet(chain, wallet)

    print(f"Wallets checked {time.ctime()}, waiting...")

    # Tell user which wallets were not checked due to no endpoints
    if len(checkedWallets) != len(WALLETS):
        try:
            _temp = WALLETS
            for wallet in checkedWallets:
                # _temp.remove(wallet)
                del _temp[wallet]
            print("\n(ERROR): Left over wallets (MAKE SURE TO ADD AN ENDPOINT TO ChainApis.py): \n" + ',\n'.join(_temp.keys()))
        except Exception as err:
            print(str(err))
            print("Checked wallets: " + str(checkedWallets))


if __name__ == "__main__":   
    main()