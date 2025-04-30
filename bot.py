import discord
from discord.ext import commands
import json
import os
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)  # Changed prefix to '!' instead of '/'

BALANCES_FILE = "balances.json"

# Ensure balances file exists
if not os.path.exists(BALANCES_FILE):
    with open(BALANCES_FILE, "w") as f:
        json.dump({}, f)

def load_balances():
    with open(BALANCES_FILE, "r") as f:
        return json.load(f)

def save_balances(balances):
    with open(BALANCES_FILE, "w") as f:
        json.dump(balances, f, indent=4)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.command(name="pay-amount")
async def pay_amount(ctx, user: discord.Member, amount: int):
    sender_id = str(ctx.author.id)
    receiver_id = str(user.id)

    if ctx.channel.name != "my-payments":
        await ctx.send("❌ You can only use this command in #my-payments channel.")
        return

    balances = load_balances()

    sender_balance = balances.get(sender_id, 1000)
    if sender_balance < amount:
        await ctx.send("❌ You don't have enough coins.")
        return

    # Transfer amount
    balances[sender_id] = sender_balance - amount
    balances[receiver_id] = balances.get(receiver_id, 1000) + amount
    save_balances(balances)

    await ctx.send(f"✅ {ctx.author.mention} paid {amount} coins to {user.mention}.")

    # Send DM to sender
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await ctx.author.send(
            f"📤 Dear {ctx.author.mention}, {amount} coins were debited from your account to {user.mention} on {now}."
        )
    except:
        pass

@bot.command(name="balance")
async def balance(ctx):
    user_id = str(ctx.author.id)
    balances = load_balances()
    balance = balances.get(user_id, 1000)
    await ctx.send(f"💰 {ctx.author.mention}, you have {balance} coins.")

@bot.event
async def on_message(message):
    if message.guild is None and message.author != bot.user:
        if message.content.startswith("439246792364-"):
            try:
                amount = int(message.content.split("-")[1])
                user_id = str(message.author.id)
                balances = load_balances()
                balances[user_id] = balances.get(user_id, 1000) + amount
                save_balances(balances)

                await message.author.send(f"✅ {amount} coins added to your account. Current balance: {balances[user_id]} coins.")
            except:
                await message.author.send("❌ Invalid amount format. Use like: 439246792364-500")
    await bot.process_commands(message)
