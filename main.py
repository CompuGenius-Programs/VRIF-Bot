import json
import os

import aiohttp
import discord
import dotenv
from discord import Option
from discord.ext.pages import Paginator, Page

import parsers

dotenv.load_dotenv()
token = os.getenv("TOKEN")
publisher_api_key = os.getenv("PUBLISHER_API_KEY")

bot = discord.Bot()

dev_id = 496392770374860811
dev_tag = "@CompuGeniusPrograms"

server_invite_url = "https://discord.gg/BFauBCj"
logo_url = "https://wiki.beardedninjagames.com/logo_vrif.png"

wiki_base_url = "https://wiki.beardedninjagames.com/"

verified_role_id = 684607822125727748
invoice_verification_url = "https://api.assetstore.unity3d.com/publisher/v1/invoice/verify.json?key=%s&invoice=%s"

vrif_server = 681644705792131083
verification_logs_channel = 1050437008272654487
verification_channel = 1050434477362515998

wiki_pages = []


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                        name="amazing games made with VRIF. Type /help"))

    await populate_pages()

    guild = bot.get_guild(vrif_server)
    verify_channel = discord.utils.get(guild.channels, id=verification_channel)
    await verify_channel.send(view=VerifyInvoiceView())


async def populate_pages():
    with open("wiki_urls.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    vrif = data["vrif"]
    external = data["external"]

    for category in vrif:
        category = parsers.VRIF.from_dict(category)
        for page in category.pages:
            wiki_pages.append("%s / %s" % (category.title, page.title))

    for page in external:
        page = parsers.External.from_dict(page)
        wiki_pages.append("External / %s" % page.title)


async def get_pages(ctx: discord.AutocompleteContext):
    return [page for page in wiki_pages if ctx.value.lower() in page.lower()]


@bot.slash_command(name="wiki", description="Get wiki links.")
async def _wiki(ctx, page: Option(str, "Page (Ex. Installation Guide)", autocomplete=get_pages, required=False),
                message_id: Option(str, "ID of Message to Reply To", required=False)):
    with open("wiki_urls.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    vrif = data["vrif"]
    external = data["external"]

    if page is not None:
        url = wiki_base_url
        page_lower = page.lower()

        if not page.startswith("External"):
            categories = [parsers.VRIF.from_dict(category) for category in vrif]

            for category in categories:
                title_lower = category.title.lower()
                if page_lower.startswith(title_lower):
                    page_lower = page_lower.removeprefix(title_lower + " / ")
                    for p in category.pages:
                        if page_lower == p.title.lower():
                            if p.override != "":
                                url = p.override
                            else:
                                url += "%s/%s" % (category.url, p.url)
                            break

        else:
            categories = [parsers.External.from_dict(category) for category in external]

            for category in categories:
                title_lower = category.title.lower()
                if page_lower.removeprefix("external / ") == title_lower:
                    url = category.url
                    break

        if url == wiki_base_url:
            page = "No Wiki Page Found With Name `%s`" % page
            await ctx.respond(page)
        else:
            text = "%s recommends you take a look at the [`%s`](<%s>) wiki page" % (ctx.author.mention, page, url)

            if message_id is not None:
                message = await ctx.fetch_message(int(message_id))
                await ctx.respond("Dismiss this message.", ephemeral=True)
                await message.reply(text)
            else:
                await ctx.respond(text)

    else:
        embeds = []

        for category in vrif:
            category = parsers.VRIF.from_dict(category)

            category_url = wiki_base_url + category.url

            description = ""

            for page in category.pages:
                description += "• [%s](%s)\n" % (page.title, "%s/%s" % (category_url, page.url))

            embed = create_embed(category.title, description=description)
            embeds.append(embed)

        for category in external:
            category = parsers.External.from_dict(category)

            description = "• [%s](%s)" % (category.title, category.url)

            embed = create_embed("External", description=description)
            embeds.append(embed)

        paginator = create_paginator(embeds)
        await paginator.respond(ctx.interaction)


class VerifyInvoiceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Get Verified", style=discord.ButtonStyle.primary)
    async def button_callback(self, button, interaction):
        await interaction.response.send_modal(VerifyInvoiceModal(title="Verify Invoice Number"))


class VerifyInvoiceModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Invoice Number", min_length=14, max_length=14,
                                           placeholder="IN000000000000"))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get(invoice_verification_url % (publisher_api_key, self.children[0].value)) as resp:
                data = await resp.json()
                if interaction.user.id == dev_id:
                    embed = create_embed("Invoice Information", "```%s```" % json.dumps(data, indent=4))
                    await interaction.followup.send(embed=embed, ephemeral=True)

                logs_channel = discord.utils.get(interaction.guild.channels, id=verification_logs_channel)
                invoices = data["invoices"]
                if len(invoices) >= 1:
                    if any(x["refunded"] == "No" and x["downloaded"] == "Yes" for x in invoices):
                        if interaction.user.id != dev_id:
                            await interaction.user.add_roles(
                                discord.utils.get(interaction.guild.roles, id=verified_role_id),
                                reason="User verified invoice.")
                            await logs_channel.send("Verified <@%s>." % interaction.user.id)

                        embed = create_embed("Invoice Verified", "You are now @verified!")
                        await interaction.followup.send(embed=embed, ephemeral=True)
                    else:
                        embed = create_embed("Invoice Not Verified",
                                             "You are not verified. Please download your asset before verifying.")
                        await interaction.followup.send(embed=embed, ephemeral=True)
                        await logs_channel.send("Did Not Verify <@%s>. Refunded: %s, Downloaded: %s" % (
                            interaction.user.id, invoices[0]["refunded"], invoices[0]["downloaded"]))
                else:
                    embed = create_embed("Invalid Invoice Number", "The invoice number you entered is invalid.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    await logs_channel.send("Invalid Invoice Number for <@%s>: %s" % (interaction.user.id, invoices))


@bot.slash_command(name="help", description="Get help for using the bot.")
async def _help(ctx):
    description = '''
A bot created by <@%s> for the VRIF Discord server (<%s>).

**/wiki** - *Displays the full wiki directory*
**/help** - *Displays this message*
''' % (dev_id, server_invite_url)

    embed = create_embed("VRIF Wiki Help [Click For Wiki Website]", description=description, error="", image=logo_url,
                         url=wiki_base_url)
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
                 error="Any errors with the bot? Please report to %s" % dev_tag,
                 image="", *, url="", author="", author_url=""):
    embed = discord.Embed(title=title, description=description, url=url, color=color)
    embed.set_footer(text=error)
    embed.set_thumbnail(url=image)
    embed.set_author(name=author, url=author_url)
    return embed


bot.run(token)
