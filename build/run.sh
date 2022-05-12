docker run \
    -it \
    -e COSMOSBALBOT_DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/0000000000000/EXAMPLE" \
    -e COSMOSBALBOT_SCHEDULER_USE_PYTHON_RUNNABLE=true \
    -e COSMOSBALBOT_DEBUGGING=true \
    -e COSMOSBALBOT_SCHEDULER_IF_ABOVE_IS_TRUE_HOW_MANY_MINUTES_BETWEEN_CHECKS=1 \
    reecepbcups/cosmos-balance-bot:latest