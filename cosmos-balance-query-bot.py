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
import requests
import schedule
import time
import tweepy

from discord import Webhook, RequestsWebhookAdapter

from ChainApis import chainAPIs, customExplorerLinks

# == Configuration ==

# When true, will actually tweet / discord post
IN_PRODUCTION = False
DISCORD = True
TWITTER = False
# If false, it is up to you to schedule via crontab -e such as: */30 * * * * cd /root/twitterGovBot && python3 twitterGovernanceBot.py
USE_PYTHON_RUNNABLE = False
LOG_RUNS = False

# Don't touch below --------------------------------------------------

with open('secrets.json', 'r') as f:
    secrets = json.load(f)

    WALLETS = secrets['WALLETS'] # list of cosmos wallets pub keys

    if TWITTER:
        twitSecrets = secrets['TWITTER']
        APIKEY = twitSecrets['APIKEY']
        APIKEYSECRET = twitSecrets['APIKEYSECRET']
        ACCESS_TOKEN = twitSecrets['ACCESS_TOKEN']
        ACCESS_TOKEN_SECRET = twitSecrets['ACCESS_TOKEN_SECRET']  
        # Authenticate to Twitter & Get API
        auth = tweepy.OAuth1UserHandler(APIKEY, APIKEYSECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)      

    if DISCORD:
        discSecrets = secrets['DISCORD']
        WEBHOOK_URL = discSecrets['WEBHOOK_URL']
        USERNAME = discSecrets['USERNAME']
        AVATAR_URL = discSecrets['AVATAR_URL']
        HEX_COLOR = int(discSecrets['HEX_COLOR'], 16)
        READACTION_RATE_LIMIT = 0.1

def discord_post_to_channel(ticker, propID, title, description, chainExploreLink):
    # Auto replace description's <br> & \n ?
    if len(description) > 4096:
        description = description[:4090] + "....."

    embed = discord.Embed(title=f"${str(ticker).upper()} #{propID} | {title}", description=description, timestamp=datetime.datetime.utcnow(), color=HEX_COLOR) #color=discord.Color.dark_gold()
    embed.add_field(name="Link", value=f"{chainExploreLink}")
    embed.set_thumbnail(url=AVATAR_URL)
    webhook = Webhook.from_url(WEBHOOK_URL, adapter=RequestsWebhookAdapter()) # Initializing webhook
    webhook.send(username=USERNAME,embed=embed) # Executing webhook

def queryCheck(chain, walletAddr):
    queryEndpoint = chainAPIs[chain][0]


def post_update(ticker, propID, title, description=""):
    # chainExploreLink = get_explorer_link(ticker, propID)
    message = f"${str(ticker).upper()} | Proposal #{propID} | VOTING_PERIOD | {title} | {chainExploreLink}"
    
    twitterAt = chainAPIs[ticker][2] # @'s blockchains official twitter
    if len(twitterAt) > 1:
        twitterAt = f'@{twitterAt}' if not twitterAt.startswith('@') else twitterAt
        message += f" | {twitterAt}"
    print(message)

    if IN_PRODUCTION:
        try:
            if TWITTER:
                tweet = api.update_status(message)
                print(f"Tweet sent for {tweet.id}: {message}")
            if DISCORD:
                discord_post_to_channel(ticker, propID, title, description, "")
        except Exception as err:
            print("Tweet failed due to being duplicate OR " + str(err)) 

def runChecks():   
    print("Running checks...") 

    checkedWallets = []

    for chain in chainAPIs.keys():
        try:
            for wallet in WALLETS:
                if wallet.startswith(chain):
                    checkedWallets.append(wallet)
                    queryCheck()
            
        except Exception as e:
            print(f"{chain} checkProp failed: {e}")
    logRun()
    print(f"All chains checked {time.ctime()}, waiting")

if __name__ == "__main__":        

    # informs user & setups of legnth of time between runs
    if IN_PRODUCTION:
        SCHEDULE_SECONDS = 30*60
        print("[!] BOT IS RUNNING IN PRODUCTION MODE!!!!!!!!!!!!!!!!!!")
        time.sleep(5)
    else:
        SCHEDULE_SECONDS = 3
        print("Bot is in test mode...")

    if DISCORD:
        print("DISCORD module enabled")
    if TWITTER:
        print("TWITTER module enabled")
    # if TELEGRAM:
    #     print("TELEGRAM module enabled")

    runChecks()

    # If user does not use a crontab, this can be run in a screen/daemon session
    if USE_PYTHON_RUNNABLE:      
        schedule.every(SCHEDULE_SECONDS).seconds.do(runChecks)  
        while True:
            print("Running runnable then waiting...")
            schedule.run_pending()
            time.sleep(SCHEDULE_SECONDS)
            

    
