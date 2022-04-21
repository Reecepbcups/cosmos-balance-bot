# cosmos-balance-query bot

<img src="https://user-images.githubusercontent.com/31943163/164518627-e950400b-0ee9-4aa6-89b6-2508546f3b9c.pngpng" alt="bot image" width="450"/>

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

## Run in docker
```
In secrets.json "SCHEDULER", enable "USE_PYTHON_RUNNABLE".
(If this is off, the bot would run 1 time with docker. Could be used with a crontab)

docker build -t username/querybot .
docker run username/querybot
```

## Install on a system
```
git clone https://github.com/Reecepbcups/cosmos-balance-query.git

cd cosmos-balance-query

# Ensure you have python installed first. May just be `python` depending on your system
python3 -m pip install --no-cache-dir -r requirements.txt

# Edit secrets.json to your values, wallets, thresholds, etc.

python3 cosmos-balance-query-bot.py
