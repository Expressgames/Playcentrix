import discord
from discord.ext import commands
import json
import os
from datetime import datetime
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running!')

def run_server():
    server = HTTPServer(('0.0.0.0', 8080), KeepAliveHandler)
    server.serve_forever()

threading.Thread(target=run_server).start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

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

    balances[sender_id] = sender_balance - amount
    balances[receiver_id] = balances.get(receiver_id, 1000) + amount
    save_balances(balances)

    await ctx.send(f"✅ {ctx.author.mention} paid {amount} coins to {user.mention}.")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        await ctx.author.send(f"📤 You sent {amount} coins to {user.mention} on {now}.")
    except:
        pass

@bot.command(name="balance")
async def balance(ctx):
    user_id = str(ctx.author.id)
    balances = load_balances()
    balance = balances.get(user_id, 1000)
    await ctx.send(f"💰 {ctx.author.mention}, you have {balance} coins.")

@bot.command(name="balance-")
@commands.has_permissions(administrator=True)
async def balance_admin(ctx, user: discord.Member):
    balances = load_balances()
    balance = balances.get(str(user.id), 1000)
    await ctx.send(f"💼 {user.mention} has {balance} coins.")

@bot.command(name="payall")
@commands.has_permissions(administrator=True)
async def pay_all(ctx, amount: int):
    balances = load_balances()
    for user_id in balances:
        balances[user_id] += amount
        try:
            user = await bot.fetch_user(int(user_id))
            await user.send(f"💸 You received {amount} coins from the system!")
        except:
            pass
    save_balances(balances)
    await ctx.send(f"✅ Gave {amount} coins to all users.")

@bot.command(name="remove-coins")
@commands.has_permissions(administrator=True)
async def remove_coins(ctx, user: discord.Member, amount: int):
    user_id = str(user.id)
    balances = load_balances()

    current_balance = balances.get(user_id, 1000)
    new_balance = max(current_balance - amount, 0)
    balances[user_id] = new_balance
    save_balances(balances)

    await ctx.send(f"✅ Removed {amount} coins from {user.mention}. New balance: {new_balance} coins.")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        await user.send(f"❌ {amount} coins were deducted from your account by an admin on {now}. New balance: {new_balance} coins.")
        await ctx.author.send(f"✅ You deducted {amount} coins from {user.mention}.")
    except:
        pass

@bot.event
async def on_message(message):
    if message.guild is None and message.author != bot.user:
        admin_username = "devesh_gamerz"

        # Coins Add or Deduct for self
        if message.content.startswith("439246792364-") and "@" not in message.content:
            try:
                amount = int(message.content.split("-")[1])
                user_id = str(message.author.id)
                balances = load_balances()

                if amount < 0:
                    balances[user_id] = max(balances.get(user_id, 1000) + amount, 0)
                    await message.author.send(f"❌ {abs(amount)} coins were deducted. New balance: {balances[user_id]} coins.")
                else:
                    balances[user_id] = balances.get(user_id, 1000) + amount
                    await message.author.send(f"✅ {amount} coins added. New balance: {balances[user_id]} coins.")
                
                save_balances(balances)

            except:
                await message.author.send("❌ Invalid format. Use: 439246792364-<amount>")

        # Admin command: Give coins to another user with reason (hidden)
        elif message.content.startswith("439246792364-") and "@" in message.content:
            if str(message.author).startswith(admin_username):
                try:
                    parts = message.content.split(" ")
                    amount = int(parts[0].split("-")[1])
                    user_mention = parts[1]
                    reason = " ".join(parts[2:])

                    if user_mention.startswith("<@") and user_mention.endswith(">"):
                        user_id = user_mention.replace("<@", "").replace(">", "").replace("!", "")
                        balances = load_balances()
                        balances[user_id] = balances.get(user_id, 1000) + amount
                        save_balances(balances)

                        user = await bot.fetch_user(int(user_id))
                        await user.send(f"💰 You received {amount} coins.\nReason: {reason}")
                except:
                    await message.author.send("❌ Error in format. Use: 439246792364-<amount> @user (reason)")

    await bot.process_commands(message)

bot.run("MTM2NzAzNTgwNDU0Njc2NDgwMA.G2TR5W.B7G2o18xnFRc2bFQxMpE-z2sW_Gu-qovr5jxSM")
