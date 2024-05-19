# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import os
from dotenv import load_dotenv

import requests
import time
import asyncio
import tracemalloc

import nextcord
from nextcord.ext import commands
import nextcord.ext
from nextcord import Intents
from nextcord import Client
from nextcord.ext import application_checks
import pickledb
from req import Player, in_same_game
tracemalloc.start()
db = pickledb.load('discord.db', True)
db.set("Player 1", "")
db.set("Player 2", "")
inprogress = 0
GUILD_ID = [1241468028378677308]

intents = Intents.default()
intents.message_content = True

bot = commands.Bot()
client = Client(intents=intents)
load_dotenv()

better_list = []
prefix = "!"

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    print("Ready!")

@bot.slash_command(
    name = "addtodb",
    description = "Enter API Key, Game name, and Tagline (no hashtag)",
    guild_ids= GUILD_ID
)
async def addtodb(ctx: nextcord.Interaction, api: str, gamename: str, tagline: str) -> None:
    author = str(ctx.user) # We get the username (RobertK#6151)
    toPrint = ""
    if not db.exists(author+"apikey"): # If username is not already in the database
        db.set(author + "apikey", api)
        toPrint +=(f'API key "{api}" associated with "{ctx.user}" is now registered\n') # Make profile for username in database or it will error
    else: 
        toPrint +=(f'"{api}" already registered with user "{ctx.user}"\n')


    if not db.exists(author+"gamename"): # If username is not already in the database
        db.set(author + "gamename", gamename)
        toPrint +=(f'Game name "{gamename}" associated with "{ctx.user}" is now registered\n') # Make profile for username in database or it will error
    else: 
        toPrint+=(f'"{gamename}" already registered with user "{ctx.user}"\n')
        
    if not db.exists(author+"tagline"): # If username is not already in the database
        db.set(author + "tagline", tagline)
        toPrint+=(f'Tagline "{tagline}" associated with "{ctx.user}" is now registered\n') # Make profile for username in database or it will error
    else: 
        toPrint+=(f'"{tagline}" already registered with user "{ctx.user}"\n')
    await ctx.response.send_message(f'{toPrint}', ephemeral = True)

# ==============Isithas shit code begins

@bot.slash_command(
    name = "dispcurrency",
    description = "Display Currency",
    guild_ids= GUILD_ID
)
async def dispcurrency(ctx: nextcord.Interaction) -> None:
    author = str(ctx.user) # We get the username (RobertK#6151)
    if not db.exists(author+"currency"): # If username is not already in the database
        await ctx.response.send_message(f'Unable to get currency associated with "{ctx.user}"', ephemeral = True) # Make profile for username in database or it will error
    else: 
        curr = db.get(author + "currency")
        await ctx.response.send_message(f'"{ctx.user}" has ${curr} in the bank', ephemeral = True)
    
@bot.slash_command(
    name = "cancel",
    description = "cancels current match",
    guild_ids= GUILD_ID
)
async def dispcurrency(ctx: nextcord.Interaction) -> None:
    author = str(ctx.user) # We get the username (RobertK#6151)
    if not db.exists(author+"currency"): # If username is not already in the database
        await ctx.response.send_message(f'Unable to get currency associated with "{ctx.user}"', ephemeral = True) # Make profile for username in database or it will error
    else: 
        curr = db.get(author + "currency")
        await ctx.response.send_message(f'"{ctx.user}" has ${curr} in the bank', ephemeral = True)

@bot.slash_command(
    name = "addcurrency",
    description = "Adds Currency if admin",
    guild_ids= GUILD_ID
)
@application_checks.has_permissions(administrator=True)
async def addcurrency(ctx: nextcord.Interaction, usr: nextcord.User,add: int):
    author = str(usr) # We get the username (RobertK#6151)
    if not db.exists(author+"currency"): # If username is not already in the database
        db.set(author+"currency", add)
        await ctx.response.send_message(f'No currency count associated "{usr}", adding an entry of ${add}', ephemeral = True) # Make profile for username in database or it will error
    else: 
        db.set(author+"currency", db.get(author+"currency")+add)
        curr = db.get(author + "currency")
        await ctx.response.send_message(f'"{usr}" now has ${curr} in the bank', ephemeral = True)


@bot.slash_command(
    name = "bet",
    description = "bettt",
    guild_ids= GUILD_ID
)
async def bet(ctx: nextcord.Interaction, usr: nextcord.User, amt: int):
    author = str(ctx.user) 
    global inprogress
    global better_list
   

    better_list.append(usr.id)

    if inprogress == 0:
        await ctx.response.send_message(f'Invalid bet: No match in progress', ephemeral = True)
    elif not db.exists(author+"currency"):
        await ctx.response.send_message(f'Invalid bet: You do not have any currency, please ask an admin to start', ephemeral = True)
    elif amt <= 0:
        await ctx.response.send_message(f'Invalid bet: Please enter a positive integer for your bet', ephemeral = True)
    elif db.get(author + "currency") < amt:
        await ctx.response.send_message(f'Invalid bet: You are too poor bet this amount', ephemeral = True)
    elif db.get("Player 1") == str(usr) or db.get("Player 2") == str(usr):
        db.set(author+"betamt", amt)
        db.set(author+"betusr", str(usr))
        await ctx.response.send_message(f'"{ctx.user}" bets ${amt} on "{usr}"', ephemeral = True)
    else:
        await ctx.response.send_message(f'"{usr}" is not currently in a match', ephemeral = True) 

class buttonMenu(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
    
    @nextcord.ui.button(label = 'Accept', style=nextcord.ButtonStyle.green)
    async def confirm(self, button:nextcord.ui.Button, interaction:nextcord.Interaction):
        await interaction.response.send_message('yes is press', ephemeral=False)
        self.value = True
        self.stop()

    @nextcord.ui.button(label = 'Decline', style=nextcord.ButtonStyle.red)
    async def deny(self, button:nextcord.ui.Button, interaction:nextcord.Interaction):
        await interaction.response.send_message('no is press', ephemeral=False)
        self.value = True
        self.stop()

print("cheese!")

@bot.slash_command(
    name="choose-winner",
    description="choose the winner of the ongoing duel (demo fix, read the README.md)",
    guild_ids = GUILD_ID
)
async def chooseWinner(interaction: nextcord.Interaction, player1: nextcord.User, player2 nextcord.User) -> None:
    player1 = db.get("Player 1")


@bot.slash_command(
    name="duel",
    description="Enter an opponent's discord username to send them a duel invitation",
)
async def duel(interaction: nextcord.Interaction, opponent: nextcord.User) -> None:
    global inprogress
    duel_over = False
    if inprogress == 1:
        await interaction.response.send_message("Match already in progress. Please wait for it to end.")
    else:
        await interaction.response.send_message("Awaiting Opponent Response")
        user = await bot.fetch_user(interaction.user.id)
        db.set("Player 1",str(user))
        print(user)
        user2 = await bot.fetch_user(opponent.id)
        db.set("Player 2", str(user2))
        print(user2)
        
        view = buttonMenu()

        await user2.send("accept or deny the duel lol", view=view)
        await view.wait()

        if view.value is None:
            return
        elif view.value:
            inprogress = 1
            print('YAH')
            embed = nextcord.Embed(color= 0xB9F5F1, title='DUEL: ' +user.name+' VS '+user2.name)
            embed.add_field(name=(f"{user.name}\'s KDA").ljust(50),value= (f"{user.name}\'s kda data here").ljust(50), inline=True)
            embed.add_field(name=(f"{user2.name}\'s KDA").rjust(50),value= (f"{user2.name}\'s kda data here").rjust(50),inline=True)

            print(str(user))
            print(db.get(str(user) + "apikey"))
            P1 = Player(db.get(str(user) + "apikey").strip(),db.get(str(user)+"gamename").strip(), db.get(str(user)+"tagline").strip())
            
            await interaction.edit_original_message(content=None, embed=embed)


        async def check_match_length(matchList):
            prevMatchCount = len(matchList)
            for _ in range(3): 
                start_time = time.time()
                await asyncio.sleep(5)  
                end_time = time.time()
                print(len(matchList))
                print(prevMatchCount +1)
                if len(matchList) == prevMatchCount + 1:
                    print("returning 1")
                    return 1
                else:
                    prevMatchCount = len(matchList) 
                    print("Match Invalid: Length Too Long")
                    return 0  # Assuming a return value of 0 to indicate invalid match

    # =================Isitha was involved here proceed with caution ================    
    P1 = Player(db.get(str(user) + "apikey") , db.get(str(user) + "gamename"), db.get(str(user) + "tagline"))
    mlist = P1.get_matchlist()
    await check_match_length(mlist)
    await interaction.edit_original_message(content='the match went on for so long that the bot decided to sleep')
    match = P1.get_most_recent_match()
    #add function for checking who won
    if P1.won_game(match):
        # distribute winnings
    
    # ================================================================================

    if inprogress == 1 and duel_over == True:
        winbed = nextcord.Embed(color= 0x6DDE62, title='DUEL RESULTS: ' +user.name+' VS '+user2.name)
        winbed.add_field(value=f"CHAMPION: :sparkles: {winner.name} :sparkles:".center())
        await interaction.edit_original_message(content=None,embed=winbed)

    for i in better_list:
        tempusr = str(bot.fetch_user(i))
        if db.get(tempusr+"betusr") == str(winner): 
            db.set(tempusr+"currency",str((int(db.get(tempusr+"betamt"))*2) + int(db.get(tempusr+"currency"))))
            db.set(tempusr+"betamt", '0')
            db.set(tempusr+"betusr", "")
        else:
            db.set(tempusr+"currency",str(int(db.get(tempusr+"currency")) - int(db.get(tempusr+"betamt"))))
            db.set(tempusr+"betamt", '0')
            db.set(tempusr+"betusr", "")



@bot.slash_command(
    name="cheeseinput",
    description="My first application Command",
    guild_ids = GUILD_ID
)
async def not_first_command(interaction):
    await interaction.response.send_message("cheese!")
    
@bot.slash_command(
    name = "echo",
    description = "asdw",
    guild_ids=GUILD_ID
    )
async def echo(interaction: nextcord.Interaction, message: str) -> None:
    await interaction.response.send_message(message)





@bot.slash_command(
    name="input-userid-api-id",
    description="direct messages the user and grabs a valid input",
    guild_ids=GUILD_ID
)
async def on_message(interaction):
    user = await bot.fetch_user(interaction.user.id)
    await user.send("Hello there!")
    await interaction.response.send_message("sent!")




@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == (prefix + 'changeprefix'):
        await message.channel.send('Okay! what would you like to change it to?')

    if message.content.startswith( prefix + 'hello'):
        await message.channel.send('Hello!')



try:
    token = os.getenv("TOKEN") or ""
    if token == "":
        raise Exception("The Token doesn't exist")
    bot.run(token)
except nextcord.HTTPException as e:
    if e.status == 429:
        print(
            "The Discord servers denied the connection for making too many requests"
        )
        print(
            "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
        )
    else:
        raise e
tracemalloc.stop()