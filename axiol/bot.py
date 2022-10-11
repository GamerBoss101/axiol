import os
from dotenv import load_dotenv
import disnake


from disnake.ext import commands
import database as db
import constants as var

load_dotenv()


async def guild_prefix(_bot, message):
    """Return current guild prefix"""
    if not message.guild:
        return var.DEFAULT_PREFIX

    prefix_doc = await db.PREFIXES.find_one({"_id": message.guild.id})
    if prefix_doc is None:
        return var.DEFAULT_PREFIX
    return prefix_doc["prefix"]


intents = disnake.Intents().all()
bot = commands.Bot(command_prefix=guild_prefix, help_command=None, intents=intents)


@bot.event
async def on_ready():

    await bot.change_presence(
        activity=disnake.Activity(
            type=disnake.ActivityType.streaming, name=f"Ping and ask for help 👀"
        )
    )
    print("I woke up 🌥️")


# Loading pogs
for filename in os.listdir("./custom"):
    if filename.endswith(".py"):
        bot.load_extension(f"custom.{filename[:-3]}")

for filename in os.listdir("./ext"):
    if filename.endswith(".py"):
        bot.load_extension(f"ext.{filename[:-3]}")

for filename in os.listdir("./plugins"):
    if filename.endswith(".py"):
        bot.load_extension(f"plugins.{filename[:-3]}")

for filename in os.listdir("./visuals"):
    if filename.endswith(".py"):
        bot.load_extension(f"visuals.{filename[:-3]}")


@bot.event
async def on_guild_join(guild):
    # Inserting plugin configs if it does not exist (incase of re-inviting)
    if not await db.PLUGINS.count_documents({"_id": guild.id}, limit=1):
        await db.PLUGINS.insert_one(
            {
                "_id": guild.id,
                "Leveling": False,
                "Moderation": True,
                "ReactionRoles": True,
                "Welcome": False,
                "Verification": False,
                "Chatbot": True,
                "AutoMod": False,
                # "Karma": False,
                "Fun": True,
                "Giveaway": True,
            }
        )

    if not await db.PERMISSIONS.count_documents({"_id": guild.id}, limit=1):
        await db.PERMISSIONS.insert_one(
            {
                "_id": guild.id,
                "Leveling": {},
                "Moderation": {},
                "ReactionRoles": {},
                "Welcome": {},
                "Verification": {},
                "Chatbot": {},
                "Commands": {},
                "AutoMod": {},
                # "Karma": {},
                "Fun": {},
                "Giveaway": {},
            }
        )

    # Support server Log
    bot_count = len([b for b in guild.members if b.bot])
    embed = (
        disnake.Embed(
            title="I just joined a new server!",
            description=guild.name,
            color=var.C_GREEN,
        )
        .add_field(name="ID", value=guild.id, inline=False)
        .add_field(name="Member count", value=guild.member_count, inline=False)
        .add_field(
            name="Bot to human percentage",
            value=f"{round(bot_count / guild.member_count * 100, 2)}%",
            inline=False,
        )
    )

    await bot.get_channel(848207106821980213).send(embed=embed)


# Support server Log
@bot.event
async def on_guild_remove(guild):

    bot_count = len([b for b in guild.members if b.bot])
    embed = (
        disnake.Embed(
            title="I just got removed from a server",
            description=guild.name,
            color=var.C_RED,
        )
        .add_field(name="ID", value=guild.id, inline=False)
        .add_field(name="Member count", value=guild.member_count, inline=False)
        .add_field(
            name="Bot to human percentage",
            value=f"{round(bot_count / guild.member_count * 100, 2)}%",
            inline=False,
        )
    )

    await bot.get_channel(848207106821980213).send(embed=embed)


bot.run(var.TOKEN)
