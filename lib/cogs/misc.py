from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions, cooldown, BucketType
from discord import Embed, Message, Reaction

from discord.ext import timers

from discord.utils import get

from datetime import datetime


import json

with open("config.json") as config_file:
    config = json.load(config_file)

import random

from ..db import db  # pylint: disable=relative-beyond-top-level

owner_id = 308000668181069824

import os
from dotenv import load_dotenv

load_dotenv()


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="prefix", aliases=["ChangePrefix"], brief="Changes the prefix.")
    @has_permissions(manage_guild=True)
    async def change_prefix(self, ctx, new: str):
        """Changes the prefix for the server.\n`Manage Server` permission required."""
        if len(new) > 10:
            await ctx.reply(
                "The prefix can not be more than 10 characters.", delete_after=10
            )

        else:
            db.execute(
                "UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, ctx.guild.id
            )
            embed = Embed(
                title="Prefix Changed",
                description=f"Prefix has been changed to `{new}`",
            )
            await ctx.reply(embed=embed)

    @change_prefix.error
    async def change_prefix_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.reply(
                "You need the Manage Server permission to change the prefix.",
                delete_after=10,
            )

    @command(name="poll", brief="Lets the user create a poll.")
    @cooldown(1, 4, BucketType.user)
    async def start_poll(self, ctx, *, question: str):
        """Starts a poll with the question/name the user wants!"""
        embed = Embed(
            title="Poll Started", description=question, colour=ctx.author.colour
        )
        embed.set_footer(
            text=f"{ctx.author} started this poll.", icon_url=ctx.author.avatar_url
        )
        message = await ctx.reply(embed=embed)

        emojis = ["✅", "❌"]

        for emoji in emojis:
            await message.add_reaction(emoji)

    @command(
        name="giveaway",
        aliases=["startgiveaway"],
        brief="Creates a giveaway, that will choose a winner!",
    )
    @cooldown(1, 5, BucketType.user)
    @has_permissions(administrator=True)
    async def start_giveaway(self, ctx, *, prize: str):
        """Lets a Server Admin start a giveaway\n`Server Administrator` permission required."""
        embed = Embed(
            title=f"{prize} giveaway!",
            description=f"{ctx.author.display_name} is giving away {prize}!\nReact with 🎁!",
        )
        embed.set_footer(
            text=f"{ctx.author} started this giveaway.", icon_url=ctx.author.avatar_url
        )

        message = await ctx.reply(embed=embed)

        await message.add_reaction("🎁")

    @command(
        name="stopgiveaway",
        aliases=["endgiveaway"],
        brief="Stops the giveaway, this chooses the winner!",
    )
    @cooldown(1, 5, BucketType.user)
    @has_permissions(administrator=True)
    async def stop_giveaway(self, ctx, *, message_id: Message):
        """Lets a Server Admin stop a giveaway, this chooses the winner at random!\n`Server Administrator` permission required."""

        channel = self.bot.get_channel(message_id.channel.id)
        message = await channel.fetch_message(message_id.id)

        users = set()

        for reaction in message.reactions:
            async for user in reaction.users():
                if not user.bot:
                    users.add(user)

        entries = list()

        for user in users:
            if not user.bot:
                entries.append(user.id)
            else:
                print("lol")

        winner = random.choice(entries)

        print(entries)

        await channel.send(f"<@{winner}> won the giveaway!")
        await channel.send(
            f"{ctx.author.mention}, the giveaway has been ended.", delete_after=30
        )

        user = self.bot.get_user(winner)

        await user.send(
            f"You won the giveaway from <#{channel.id}> in {channel.guild.name}!"
        )

    @command(
        name="timebomb",
        aliases=["tbmsg", "tb", "timebombmessage"],
        brief="Send a message with a timelimit on it.",
    )
    @cooldown(1, 4, BucketType.user)
    async def time_bomb_command(self, ctx, time: int, *, message: str):
        """Makes a message with a timelimit on it, the time is in seconds."""
        if time < 1000:
            await ctx.message.delete()

            embed = Embed(
                title="Time Message", description=message, colour=ctx.author.colour
            )
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(
                text=f"{ctx.author} | This message only lasts {str(time)} seconds.",
                icon_url=ctx.author.avatar_url,
            )

            await ctx.send(embed=embed, delete_after=time)

        else:
            await ctx.reply(
                f"Please try again with a lower time, {time} is too big.",
                delete_after=15,
            )

    @command(name="vote", aliases=["upvote"], brief="Vote for Doob on Top.gg!")
    @cooldown(1, 4, BucketType.user)
    async def topgg_upvote_command(self, ctx):
        await ctx.reply("Vote for Doob at: https://top.gg/bot/680606346952966177/vote")

    @command(name="phone", aliases=["iphone"], brief="phone")
    @cooldown(1, 4, BucketType.user)
    async def phone_command(self, ctx):
        """phone\n`Patreon Only`"""
        homeGuild = self.bot.get_guild(config["homeGuild_id"])  # Support Server ID.
        patreonRole = get(
            homeGuild.roles, id=config["patreonRole_id"]
        )  # Patreon role ID.

        member = []

        for pledger in homeGuild.members:
            if pledger == ctx.author:
                member = pledger

        if ctx.author in homeGuild.members:
            if patreonRole in member.roles:
                await ctx.reply(
                    "https://cdn.discordapp.com/attachments/721514198000992350/794840218514751499/IYUimA7gyac7sxrB3uKu9Mb1ZZOJVtgAAAA.png"
                )

            else:
                await ctx.reply(
                    "You are not a Patron to Doob, subscribe to any of the tiers at <https://patreon.com/doobdev> to gain access to this command."
                )

        else:
            await ctx.reply(
                "You are not a Patron to Doob, subscribe to any of the tiers at <https://patreon.com/doobdev> to gain access to this command."
            )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")

    @command(name="remind", aliases=["remindme"], brief="Set a reminder")
    async def remind(self, ctx, time, *, text):
        """Remind to do something on a date.\nThe format is: `Y/M/D`."""
        date = datetime(*map(int, time.split("/")))
        timers.Timer(
            self.bot, "reminder", date, args=(ctx.channel.id, ctx.author.id, text)
        ).start()

        await ctx.reply("Reminder set!")

    @Cog.listener()
    async def on_reminder(self, author_id, text):
        author = self.bot.get_user(author_id)

        await author.send(f"<@{author.id}>, remember to: {text}")

    @command(
        name="ownerprefix",
        aliases=["opo"],
        brief="Changes the prefix. | Bot Owner Override.",
    )
    async def override_change_prefix(self, ctx, new: str):
        """Changes the prefix for the server.\nOnly the bot owner can use the override command."""

        prefix = db.records("SELECT Prefix FROM guilds WHERE GuildID = ?", ctx.guild.id)

        if ctx.author.id == owner_id:
            db.execute(
                "UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, ctx.guild.id
            )
            embed = Embed(
                title="Prefix Changed",
                description=f"Prefix has been changed to `{new}`",
            )

            await ctx.reply(embed=embed)

        else:
            await ctx.reply(
                f"This is the owner override command, only the owner of the bot can use this. If you are a server manager, use `{prefix[0][0]}prefix` command."
            )


def setup(bot):
    bot.add_cog(Misc(bot))
