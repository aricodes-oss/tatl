import asyncio
from datetime import datetime

import discord
from discord.ext import commands, tasks

from tatl.bot import Bot
from tatl.db.models.subscription import Subscription


async def _unsubscribe_autocomplete(ctx: discord.AutocompleteContext) -> list[str]:
    return [
        s.user_login
        for s in Subscription.select().where(
            Subscription.channel_id == ctx.interaction.channel_id,
        )
    ]


class GoLive(commands.Cog):
    update_lock: asyncio.Lock = asyncio.Lock()

    def __init__(self, bot: Bot):
        self.bot = bot
        self.stream_updater.start()
        self.stream_poster.start()

    def cog_unload(self):
        self.stream_updater.cancel()
        self.stream_poster.cancel()
        return super().cog_unload()

    @tasks.loop(seconds=5)
    async def stream_poster(self):
        async with self.update_lock:
            subscriptions: list[Subscription] = list(
                Subscription.select().where(
                    Subscription.last_notified_at < Subscription.last_stream_start
                )
            )
            for sub in subscriptions:
                channel = await self.bot.fetch_channel(sub.channel_id)

                embed = discord.Embed(
                    title=f"{sub.user_login} just went live!",
                    description=f"{sub.user_login} just started streaming {sub.last_game_name}",
                    color=discord.Colour.blurple(),
                )
                embed.set_image(
                    url=sub.last_thumbnail_url.replace(
                        "{width}",
                        "1024",
                    ).replace(
                        "{height}",
                        "576",
                    )
                )
                embed.add_field(name="Link", value=f"https://twitch.tv/{sub.user_login}")
                await channel.send(embed=embed)

                sub.last_notified_at = datetime.utcnow()
                sub.save()

    @tasks.loop(seconds=5)
    async def stream_updater(self):
        user_ids = {s.user_id for s in Subscription.select()}
        streams = await self.bot.twitch.fetch_streams(user_ids=list(user_ids))

        async with self.update_lock:
            for stream in streams:
                Subscription.update(
                    {
                        Subscription.last_stream_start: stream.started_at,
                        Subscription.last_game_name: stream.game_name,
                        Subscription.last_thumbnail_url: stream.thumbnail_url,
                    }
                ).where(Subscription.user_id == stream.user.id).execute()

    group = discord.SlashCommandGroup("golive", "Manages Twitch golive notifications")

    @group.command(description="Adds a user to the golive notifications list")
    @discord.default_permissions(manage_messages=True)
    async def subscribe(
        self,
        ctx: discord.ApplicationContext,
        user_login: discord.Option(str),
    ) -> None:
        users = await self.bot.twitch.fetch_users(names=[user_login])
        if len(users) != 1:
            await ctx.respond(
                f"Unable to find user {user_login}. Expected 1 result, got {len(users)}"
            )
            return
        user = users[0]
        existing_subscriptions = Subscription.select().where(
            Subscription.user_id == user.id,
            Subscription.channel_id == ctx.channel_id,
        )

        if existing_subscriptions.count() > 0:
            await ctx.respond(
                f"This channel is already subscribed to {user.display_name} streams",
            )
            return

        Subscription.create(
            user_login=user.display_name,
            user_id=user.id,
            channel_id=ctx.channel_id,
        )
        await ctx.respond(f"Subscribed to {user.display_name} streams!")

    @group.command(description="Removes a user from the golive notifications list")
    @discord.default_permissions(manage_messages=True)
    async def unsubscribe(
        self,
        ctx: discord.ApplicationContext,
        user_login: discord.Option(
            str,
            autocomplete=discord.utils.basic_autocomplete(_unsubscribe_autocomplete),
        ),
    ) -> None:
        query = Subscription.delete().where(
            Subscription.user_login == user_login,
            Subscription.channel_id == ctx.channel_id,
        )
        count = query.execute()
        await ctx.respond(f"Deleted {count} subscriptions")


def setup(bot: Bot) -> None:
    bot.add_cog(GoLive(bot))
