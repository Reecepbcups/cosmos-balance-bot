# sudo docker build -t reecepbcups/cosmos-balance-query:latest .
# sudo docker run -it --rm --name query-bot reecepbcups/cosmos-balance-query

FROM python:3-alpine

LABEL Maintainer="reecepbcups"

WORKDIR /usr/app/src

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./cosmos-balance-bot.py"]
