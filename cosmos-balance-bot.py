#!/usr/bin/python3

'''
Reece Williams (Reecepbcups | PBCUPS Validator [$OSMO, $DIG]) | April 21st, 2022
- Twitter & Discord Integration + Endpoints

Install:
- pip install --no-cache-dir -r requirements.txt

Run:
- python cosmos-balance-bot.py

Docker:
- docker build -t reecepbcups/querybot .
- docker run reecepbcups/querybot

*Get REST lcd's in chain.json from https://github.com/cosmos/chain-registry
'''

import datetime
import discord
import requests
import schedule
import time
import json
import tweepy

from discord import Webhook, RequestsWebhookAdapter

from ChainApis import chainAPIs

NOTIFIERS = { # {wallet: { "good": 100.0, "warning": 50.0, "low": 10.0}}
    "good": [0x00FF00,"https://image.similarpng.com/very-thumbnail/2021/05/Checkmark-green-tick-isolated-on-transparent-background-PNG.png"],
    "warning": [0xFFFF00,"https://media.istockphoto.com/vectors/warning-sign-yellow-exclamation-mark-icon-danger-sign-attention-sign-vector-id1165690157?k=20&m=1165690157&s=612x612&w=0&h=nU2Iow3Lbg66noibsRdlZkvwnHwEC6mOddnY024i3mQ="],
    "low": [0xFF0000,"https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Cross_red_circle.svg/2048px-Cross_red_circle.svg.png"],
}


# Don't touch below --------------------------------------------------

with open('secrets.json', 'r') as f:
    secrets = json.load(f)

    DISCORD = secrets["DISCORD"]["ENABLED"]
    TWITTER = secrets["TWITTER"]["ENABLED"]
    TELEGRAM = secrets["TELEGRAM"]["ENABLED"]

    USE_PYTHON_RUNNABLE = secrets["SCHEDULER"]["USE_PYTHON_RUNNABLE"]
    SCHEDULE_MINUTES = secrets["SCHEDULER"]["IF_ABOVE_IS_TRUE_HOW_MANY_MINUTES_BETWEEN_CHECKS"]

    WALLETS = secrets['WALLETS'] # {wallet: { "good": 100.0, "warning": 50.0, "low": 10.0}}
    SIMPLIFY_UDENOM = secrets['SIMPLIFY_UDENOM_VALUES_TO_READABLE']# divided values by 1_000_000
    NOTIFY_GOOD_BALANCES = secrets['NOTIFY_GOOD_BALANCES']

    if TWITTER:
        twitSecrets = secrets['TWITTER']
        APIKEY = twitSecrets['APIKEY']
        APIKEYSECRET = twitSecrets['APIKEYSECRET']
        ACCESS_TOKEN = twitSecrets['ACCESS_TOKEN']
        ACCESS_TOKEN_SECRET = twitSecrets['ACCESS_TOKEN_SECRET']  

        TWITTER_ACCOUNTS_TO_TAG = twitSecrets['ACCOUNTS_TO_TAG']

        # Authenticate to Twitter & Get API
        auth = tweepy.OAuth1UserHandler(APIKEY, APIKEYSECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)      

    if DISCORD:
        discSecrets = secrets['DISCORD']
        WEBHOOK_URL = discSecrets['WEBHOOK_URL']
        USERNAME = discSecrets['USERNAME']
        DISCORD_ACCOUNTS_TO_TAG = discSecrets['ACCOUNTS_TO_TAG']


def balanceCheck(chain, walletAddr) -> dict:
    queryEndpoint = chainAPIs[chain][0] + walletAddr

    r = requests.get(queryEndpoint, headers={
        'accept': 'application/json', 
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'}
    ) 

    if r.status_code != 200:
        print(f"Error: {r.status_code} on {chainAPIs[chain][0]}")
        return {}

    # http://65.108.125.182:1317/cosmos/bank/v1beta1/balances/craft10r39fueph9fq7a6lgswu4zdsg8t3gxlqd6lnf0
    balances = r.json()['balances']

    output = {}
    for balance in balances:
        denom = balance['denom']
        amount = balance['amount']
        
        # removes the u denom & divde by 1mil. So ucraft 1000000 = craft 1
        if SIMPLIFY_UDENOM and denom.startswith('u'):
            output[denom[1::]] = int(amount) / 1_000_000
        else:
            output[denom] = int(amount)

    # print(chain, walletAddr, output)
    return dict(output)
    
def post_update(chain, walletAddress, balanceDict):
    if balanceDict == {}:
        return

    balance = balanceDict[list(balanceDict.keys())[0]] # main coin balance

    # if SIMPLIFY_UDENOM_VALUES_TO_READABLE is true, we have to multiply amt?
    
    WARNING_LEVEL = WALLETS[walletAddress]['warning']
    LOW_LEVEL = WALLETS[walletAddress]['low']

    myValue = ""
    titleMsg = ""

    if balance > WARNING_LEVEL:
        myValue = "good"
        titleMsg += f"{myValue.upper()} ( >{WARNING_LEVEL} )"

    elif balance < WARNING_LEVEL and balance > LOW_LEVEL:
        myValue = "warning"
        titleMsg += f"{myValue.upper()} ( <{WARNING_LEVEL} )"

    else:
        myValue = "low"
        titleMsg += f"{myValue.upper()} ( <{LOW_LEVEL} )"

    HEX_COLOR = NOTIFIERS[myValue][0]
    IMG_URL = NOTIFIERS[myValue][1]
           
    # dont past if we do not want to show good balances
    if myValue == "good" and NOTIFY_GOOD_BALANCES == False:
        print(f"{walletAddress} is good, notify good balances is just off")
        return

    betterBalance = ""
    for d in balanceDict.keys():
        betterBalance += f"{d}: {balanceDict[d]}\n"

    message = f"{str(chain).upper()} {titleMsg} | {walletAddress} | {betterBalance}"
    print(message)

    # print("Exit 0 in post_update for debugging"); exit(0)

    try:
        if TWITTER:
            for acc in TWITTER_ACCOUNTS_TO_TAG:
                twitterAt = f'@{acc}' if not acc.startswith('@') else acc
                message += f" | {twitterAt}"

            tweet = api.update_status(message)
            print(f"Tweet sent for {tweet.id}: {message}")

        if DISCORD:
            embed = discord.Embed(title=f"{chain.upper()} BALANCE {titleMsg}", description=walletAddress, timestamp=datetime.datetime.utcnow(), color=HEX_COLOR) #color=discord.Color.dark_gold()
            # embed.add_field(name="Wallet", value=f"{walletAddress}")
            embed.add_field(name="Balance", value=f"{betterBalance}")
            if len(DISCORD_ACCOUNTS_TO_TAG) > 0:
                embed.add_field(name="Tags", value=', '.join(DISCORD_ACCOUNTS_TO_TAG), inline=False)
            embed.set_thumbnail(url=IMG_URL)
            webhook = Webhook.from_url(WEBHOOK_URL, adapter=RequestsWebhookAdapter()) # Initializing webhook
            webhook.send(username=USERNAME,embed=embed) # Executing webhook

    except Exception as err:
        print( str(err) + " OR Tweet failed due to being duplicate")

def runChecks():   
    print("Running checks...") 

    checkedWallets = []
    for wallet in WALLETS:
        for chain in chainAPIs.keys():
            if wallet.startswith(chain):
                checkedWallets.append(wallet)
                b = balanceCheck(chain, wallet)
                post_update(chain, wallet, b)

    print(f"Wallets checked {time.ctime()}, waiting...")

    # Tell user which wallets were not checked due to no endpoints
    if len(checkedWallets) != len(WALLETS):
        _temp = WALLETS
        for wallet in checkedWallets:
            _temp.remove(wallet)
        print("Left over wallets (no endpoints): " + str(_temp))



if __name__ == "__main__":        
    runChecks()

    # If user does not use a crontab, this can be run in a screen/daemon session
    if USE_PYTHON_RUNNABLE:      
        schedule.every(SCHEDULE_MINUTES).minutes.do(runChecks)  
        while True:
            # print("Running runnable then waiting...")
            schedule.run_pending()
            time.sleep(SCHEDULE_MINUTES*60)
            

    
