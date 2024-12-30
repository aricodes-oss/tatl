import discord
import twitchio


class Bot(discord.Bot):
    twitch: twitchio.Client | None = None
