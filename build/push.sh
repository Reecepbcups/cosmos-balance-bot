VERSION=1.3

docker build -t reecepbcups/balance-bot:$VERSION .
docker push reecepbcups/balance-bot:$VERSION