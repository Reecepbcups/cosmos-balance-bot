VERSION=2.9

docker build -t reecepbcups/cosmos-balance-bot:$VERSION .
docker push reecepbcups/cosmos-balance-bot:$VERSION