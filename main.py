import json
import os

import discord
import dotenv
from discord import Option
from discord.ext.pages import Paginator, Page

import parsers

dotenv.load_dotenv()
token = os.getenv("TOKEN")

bot = discord.Bot()

dev_id = 496392770374860811
dev_tag = "@CompuGenius Programs#2368"

server_invite_url = "https://discord.gg/mZ3cBrEcmE"
logo_url = "https://wiki.beardedninjagames.com/logo_vrif.png"

wiki_base_url = "https://wiki.beardedninjagames.com/"


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                        name="amazing games made with VRIF. Type /help ."))


async def get_pages(ctx: discord.AutocompleteContext):
    return [page for page in parsers.wiki_pages if ctx.value.lower() in page.lower()]


@bot.slash_command(name="wiki", description="Get wiki links.")
async def _wiki(ctx, page: Option(str, "Page (Ex. Installation Guide)", autocomplete=get_pages, required=False),
                message_id: Option(str, "ID of Message to Reply To", required=False)):
    with open("wiki_urls.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    categories = data["categories"]

    if page is not None:
        categories = [parsers.Category.from_dict(category) for category in categories]

        url = wiki_base_url

        page_lower = page.lower()
        for category in categories:
            title_lower = category.title.lower()
            if page_lower.startswith(title_lower):
                page_lower = page_lower.removeprefix(title_lower + " / ")
                for p in category.pages:
                    if page_lower == p.title.lower():
                        url += "%s/%s" % (category.url, p.url)
                        break

        if url == wiki_base_url:
            page = "No Wiki Page Found With Name `%s`" % page

        text = "%s recommends you take a look at the following wiki page:" % ctx.author.mention
        embed = create_embed(page, url=url)
        if message_id is not None:
            message = await ctx.fetch_message(int(message_id))
            await message.reply(text, embed=embed)
            await ctx.respond("Replied to message with ID `%s`." % message_id, ephemeral=True)
        else:
            await ctx.respond(text, embed=embed)

    else:
        embeds = []

        for category in categories:
            category = parsers.Category.from_dict(category)

            category_url = wiki_base_url + category.url

            description = ""

            for page in category.pages:
                description += "• [%s](%s)\n" % (page.title, "%s/%s" % (category_url, page.url))

            embed = create_embed(category.title, description=description)
            embeds.append(embed)

        paginator = create_paginator(embeds)
        await paginator.respond(ctx.interaction)


@bot.slash_command(name="help", description="Get help for using the bot.")
async def _help(ctx):
    description = '''
A bot created by <@%s> for the VRIF Discord server (<%s>).

**/wiki** - *Displays the full wiki directory*
**/help** - *Displays this message*
''' % (dev_id, server_invite_url)

    embed = create_embed("VRIF Wiki Help [Click For Wiki Website]", description=description,
                         footer="Bot © CompuGenius Programs. All rights reserved.", image=logo_url, url=wiki_base_url)
    await ctx.respond(embed=embed)


def clean_text(text, remove_spaces=True):
    text = text.lower().replace("'", "").replace("’", "").replace("-", "").replace("ñ", "n").replace(".", "")
    if remove_spaces:
        text = text.replace(" ", "")
    else:
        text = text.replace(" ", "_")

    return text


def create_paginator(embeds):
    pages = []
    for entry in embeds:
        pages.append(Page(embeds=[entry]))
    return Paginator(pages=pages)


def create_embed(title, description=None, color=discord.Color.green(),
                 footer="Any errors with the bot? Please report to %s" % dev_tag,
                 image="", *, url="", author="", author_url=""):
    embed = discord.Embed(title=title, description=description, url=url, color=color)
    embed.set_footer(text=footer)
    embed.set_thumbnail(url=image)
    embed.set_author(name=author, url=author_url)
    return embed


bot.run(token)
