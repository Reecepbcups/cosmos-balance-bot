#!/usr/bin/python3

'''
Reece Williams (Reecepbcups | PBCUPS Validator [$OSMO, $DIG]) | April 21st, 2022
- Twitter & Discord Integration + Endpoints

Install:
- pip install --no-cache-dir -r requirements.txt

Run:
- python cosmos-balance-bot.py

Docker:
- docker build -t reecepbcups/balancebot .
- docker run reecepbcups/balancebot

*Get REST lcd's in chain.json from https://github.com/cosmos/chain-registry
'''

import datetime
import discord
import requests
import schedule
import time
import json
import tweepy
import os

from discord import Webhook, RequestsWebhookAdapter

from ChainApis import chainAPIs

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
    TWITTER = secrets["TWITTER"]["ENABLED"]
    TELEGRAM = secrets["TELEGRAM"]["ENABLED"]

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

    if TWITTER:
        APIKEY = os.getenv(f"{PREFIX}_TWITTER_APIKEY", secrets['TWITTER']['APIKEY'])
        APIKEYSECRET = os.getenv(f"{PREFIX}_TWITTER_APIKEYSECRET", secrets['TWITTER']['APIKEYSECRET'])
        ACCESS_TOKEN = os.getenv(f"{PREFIX}_TWITTER_ACCESS_TOKEN", secrets['TWITTER']['ACCESS_TOKEN'])
        ACCESS_TOKEN_SECRET = os.getenv(f"{PREFIX}_TWITTER_ACCESS_TOKEN_SECRET", secrets['TWITTER']['ACCESS_TOKEN_SECRET'])

        TWITTER_ACCOUNTS_TO_TAG = secrets['TWITTER']['ACCOUNTS_TO_TAG']

        # Authenticate to Twitter & Get API
        auth = tweepy.OAuth1UserHandler(APIKEY, APIKEYSECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)      

    if DISCORD:
        discSecrets = secrets['DISCORD']
        WEBHOOK_URL = os.getenv(f"{PREFIX}_DISCORD_WEBHOOK_URL", discSecrets['WEBHOOK_URL'])
        USERNAME = discSecrets['USERNAME']


def simplifyBalances(balances: dict):
    '''
    After using getBalances(chain, wallet) function return -> dict:
    Reduces [{"denom": "ucraft","amount": "69908452"},{"denom": "uexp","amount": "1000100"}]
    To: {'ucraft':69908452, 'uexp':1000100}
    '''
    output = {}
    for balance in balances:
        denom = balance['denom']
        amount = balance['amount']

        if denom.startswith('ibc/'):
            continue # skip non native assets
        elif denom.startswith('gamm'):
            continue # skip osmo pools
        
        # removes the u denom & divde by 1mil. So ucraft 1000000 = craft 1
        if SIMPLIFY_UDENOM and denom.startswith('u'):
            output[denom[1::]] = int(amount) / 1_000_000
        else:
            output[denom] = int(amount)

    # print(chain, walletAddr, output)
    return dict(output)

def getBalances(chain, walletAddr) -> dict:
    '''
    Gets the balances JSON from chain & returns those values
    # [{"denom": "ucraft","amount": "69908452"},{"denom": "uexp","amount": "1000100"}]
    '''

    queryEndpoint = chainAPIs[chain][0] + walletAddr

    r = requests.get(queryEndpoint, headers={
        'accept': 'application/json', 
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'}
    ) 

    if r.status_code != 200:
        print(f"Error: {r.status_code} on {chainAPIs[chain][0]}")
        return {}

    # http://65.108.125.182:1317/cosmos/bank/v1beta1/balances/craft10r39fueph9fq7a6lgswu4zdsg8t3gxlqd6lnf0
    return r.json()['balances']
    

def getStatusValues(walletAddress, balance):
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

    status, titleMsg, hexColor, imgUrl = getStatusValues(walletAddress, balance)
    
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
        if TWITTER:
            for acc in TWITTER_ACCOUNTS_TO_TAG:
                twitterAt = f'@{acc}' if not acc.startswith('@') else acc
                message += f" | {twitterAt}"

            tweet = api.update_status(message)
            print(f"Tweet sent for {tweet.id}: {message}")

        if DISCORD:
            embed = discord.Embed(title=f"{chain.upper()} BALANCE {titleMsg}", description=walletAddress, timestamp=datetime.datetime.utcnow(), color=hexColor) #color=discord.Color.dark_gold()
            if len(note) > 0:
                embed.add_field(name="Note", value=f"{note}", inline=False)
            embed.add_field(name="Balance", value=f"{betterBalance}")
            if DEBUGGING: embed.add_field(name="DEBUGGING", value=f"{SCHEDULE_MINUTES=}")
            embed.set_thumbnail(url=imgUrl)
            webhook = Webhook.from_url(WEBHOOK_URL, adapter=RequestsWebhookAdapter()) # Initializing webhook
            webhook.send(username=USERNAME,embed=embed) # Executing webhook

    except Exception as err:
        print( str(err) + " OR Tweet failed due to being duplicate")


def runBalanceCheckForWallet(chain, wallet):
    balances = getBalances(chain, wallet)
    simplified = simplifyBalances(balances)
    postUpdate(chain, wallet, simplified)

def runChecks():   
    print("Running checks...") 

    # Go through all wallets & ChainAPis matching. If the wallet starts with a ChainAPI keyname
    # check the balance of that wallet using the given LCD API
    checkedWallets = []
    for wallet in WALLETS:
        for chain in chainAPIs.keys():
            if wallet.startswith(chain):
                checkedWallets.append(wallet)
                runBalanceCheckForWallet(chain, wallet)

    print(f"Wallets checked {time.ctime()}, waiting...")

    # Tell user which wallets were not checked due to no endpoints
    if len(checkedWallets) != len(WALLETS):
        _temp = WALLETS
        for wallet in checkedWallets:
            _temp.remove(wallet)
        print("Left over wallets (no endpoints): " + str(_temp))


import threading
if __name__ == "__main__":   
    main()