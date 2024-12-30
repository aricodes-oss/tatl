import os
import pkgutil

from dotenv import load_dotenv
import discord
from twitchio import Client

from tatl import cogs
from tatl.db import connection, models
from tatl.bot import Bot

load_dotenv()
bot = Bot(intents=discord.Intents.default())
twitch_client = Client.from_client_credentials(
    os.getenv("TWITCH_CLIENT_ID"),
    os.getenv("TWITCH_CLIENT_SECRET"),
    loop=bot.loop,
)
bot.twitch = twitch_client
# Load all cog submodules dynamically
for _, module_name, _ in pkgutil.iter_modules(cogs.__path__, cogs.__name__ + "."):
    bot.load_extension(module_name)


@bot.event
async def on_ready():
    print(f"{bot.user} is Ret-2-Go!")


def main() -> None:
    connection.create_tables(models.all_models)
    bot.run(os.getenv("BOT_TOKEN"))
