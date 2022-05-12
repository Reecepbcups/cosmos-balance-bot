VERSION=1.0

docker build -t reecepbcups/cosmos-balance-bot:$VERSION .
docker push reecepbcups/cosmos-balance-bot:$VERSION