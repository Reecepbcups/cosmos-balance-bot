#!/usr/bin/python3

'''
Reece Williams (Reecepbcups | PBCUPS Validator) | February 9th, 2022
- Twitter bot to monitor and report on COSMOS governance proposals
- (Mar 8) Discord webhook to post proposals 
- (Mar 12) Discord Threads to allow for discussion of new proposals 

python3 -m pip install requests tweepy schedule discord

*Get REST lcd's in chain.json from https://github.com/cosmos/chain-registry
'''

import datetime
import discord
import json
import os
from numpy import r_
import requests
import schedule
import time
import tweepy

from discord import Webhook, RequestsWebhookAdapter

from ChainApis import chainAPIs

# == Configuration ==

DISCORD = False
TWITTER = False
TELEGRAM = True
# If false, it is up to you to schedule via crontab -e such as: */30 * * * * cd /root/twitterGovBot && python3 twitterGovernanceBot.py
USE_PYTHON_RUNNABLE = False

NOTIFIERS = { # {wallet: { "good": 100.0, "warning": 50.0, "low": 10.0}}
    "good": [0x00FF00,"https://image.similarpng.com/very-thumbnail/2021/05/Checkmark-green-tick-isolated-on-transparent-background-PNG.png"],
    "warning": [0xFFFF00,"https://media.istockphoto.com/vectors/warning-sign-yellow-exclamation-mark-icon-danger-sign-attention-sign-vector-id1165690157?k=20&m=1165690157&s=612x612&w=0&h=nU2Iow3Lbg66noibsRdlZkvwnHwEC6mOddnY024i3mQ="],
    "low": [0xFF0000,"https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Cross_red_circle.svg/2048px-Cross_red_circle.svg.png"],
}


# Don't touch below --------------------------------------------------

with open('test-secrets.json', 'r') as f:
    secrets = json.load(f)

    WALLETS = secrets['WALLETS'] # {wallet: { "good": 100.0, "warning": 50.0, "low": 10.0}}
    SIMPLIFY_UDENOM = secrets['SIMPLIFY_UDENOM_VALUES_TO_READABLE']# divided values by 1_000_000
    ALWAYS_NOTIFY = secrets['ALWAYS_NOTIFY']

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

    HEX_COLOR = 0xFFFFF
    IMG_URL = "https://cdn.pixabay.com/photo/2015/12/16/17/41/bell-1096280_960_720.png"
    titleMsg = f" Notification"

    if ALWAYS_NOTIFY:
        # continue on
        pass
    else:
        # balanceDict[list(balanceDict.keys())[0]] > WALLETS[walletAddress]
        balance = balanceDict[list(balanceDict.keys())[0]]

        for threshold in WALLETS[walletAddress].keys():
            amt = WALLETS[walletAddress][threshold]

            if threshold == "good":
                if balance > WALLETS[walletAddress][threshold]:
                    HEX_COLOR = NOTIFIERS[threshold][0]
                    IMG_URL = NOTIFIERS[threshold][1]
                    titleMsg = f"{threshold.upper()} ( >{amt} )"
                    break

            if balance < amt:
                HEX_COLOR = NOTIFIERS[threshold][0]
                IMG_URL = NOTIFIERS[threshold][1]
                titleMsg = f"{threshold.upper()} ( <{amt} )"
                continue
            

    betterBalance = ""
    for d in balanceDict.keys():
        betterBalance += f"{d}: {balanceDict[d]}\n"

    message = f"{str(chain).upper()} {titleMsg} | {walletAddress} | {betterBalance}"
    print(message)

    # print("Exit 0 in post_update for debugging"); exit(0)

    # if ALWAYS_NOTIFY, notify no matter what.
    # else, if balanceDict of first key > WALLETS["walletAddress]



        # print(f"Wallet does not meet threshold. {} > {WALLETS[walletAddress]}")
        # return

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
                print("BREAKING ON PURPOSE")
                exit(1)

    print(f"Wallets checked {time.ctime()}, waiting...")

    # Tell user which wallets were not checked due to no endpoints
    if len(checkedWallets) != len(WALLETS):
        _temp = WALLETS
        for wallet in checkedWallets:
            _temp.remove(wallet)
        print("Left over wallets (no endpoints): " + str(_temp))



if __name__ == "__main__":        

    # informs user & setups of legnth of time between runs
    # SCHEDULE_SECONDS = 30*60

    # if DISCORD:
    #     print("DISCORD module enabled")
    # if TWITTER:
    #     print("TWITTER module enabled")
    # if TELEGRAM:
    #     print("TELEGRAM module enabled")

    runChecks()

    # If user does not use a crontab, this can be run in a screen/daemon session
    # if USE_PYTHON_RUNNABLE:      
    #     schedule.every(SCHEDULE_SECONDS).seconds.do(runChecks)  
    #     while True:
    #         print("Running runnable then waiting...")
    #         schedule.run_pending()
    #         time.sleep(SCHEDULE_SECONDS)
            

    
