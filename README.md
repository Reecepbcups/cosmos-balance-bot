# cosmos-balance-bot
A useful little bot for Relayers, Validators using restake.app, Akash Escrow Accounts, hot wallets, and anything else you want to track!

</br>

Contact 
[@Reecepbcups_](https://twitter.com/Reecepbcups_)

Delegate:
</br>

- [Dig-Chain](https://ping.pub/dig/staking/digvaloper1ms3k4d9j7rzpzmq3d4jg4j4kffldfnq66wxdpj)

</br>
<img src="https://user-images.githubusercontent.com/31943163/164914003-4df196f6-99a0-44ba-9537-d3901aabfb7f.png" alt="bot image" width="300"/>

## Setup:
```
Open secrets.json

NOTIFY_GOOD_BALANCES:(default: false)
    - When `true`, every time the bot is run it will post for all wallets even if the account is good
    - When `false`, only notifications will post if the wallet is in warning or low funds

SIMPLIFY_UDENOM_VALUES_TO_READABLE: (default: true)
    - When `true` the bot will simplify the udenom values to readable values like "juno = 1" instead of "ujuno = 1000000"
    (If you set this to false, ensure you also change all wallet denoms too.)

WALLETS: dict{dict{"status": float64}}
    - Each section specifies a wallets public address warning and low level thresholds
    - Depending on the section, the notification title & color will change in relation to the warning

TWITTER:
- Keys & Secrets to connect to a twitter bot account. This requires a developer.twitter.com account

Discord:
- Webhook URL (channel settings -> Integrations -> webhook -> create new & copy URL)
- Username: What you want the webhook bot to be called
- Accounts to tag - doesn't work yet
```

## Run in akash
```sh
git clone https://github.com/Reecepbcups/cosmos-balance-bot.git
cd cosmos-balance-bot

# open secrets.json & add in your wallet keys & tolerance levels
# Ensure DISCORD ENABLED is true. (It should be by default)
# You can put the other values if you wish, however there is support for environment variables

docker login

# Build the image & push to docker hub
docker build -t username/balance-bot .
docker push username/balance-bot:latest

# open the akashalytics deploy panel tool
# https://www.akashlytics.com/deploy
#
# - Create Deployment
# - From a File
#
# - Select cosmos-balance-bot/akash-deploy/cosmos-balance-deploy.yml
#    - Update the image: to point to your location (username/balance-bot:latest)
#    - Change the minute check and discord webhook URL to match your needs
#      [If none is provided, your secrets.json will be used as default.]
#
# - You can alter the compute resources, however CPU is the majority of the cost.
#          0.25CPU, 0.5GB RAM, and 1GB storage are recommended minimum.
```

## Install on a system
```
git clone https://github.com/Reecepbcups/cosmos-balance-bot

cd cosmos-balance-bot

# Ensure you have python installed first. May just be `python` depending on your system
python3 -m pip install --no-cache-dir -r requirements.txt

# Edit secrets.json to your values, wallets, thresholds, etc.

python3 cosmos-balance-query-bot.py
