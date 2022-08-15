FROM --platform=linux/amd64 python:3-alpine

LABEL Maintainer="reecepbcups"

WORKDIR /usr/app/src

COPY requirements/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./src/cosmos-balance-bot.py"]
