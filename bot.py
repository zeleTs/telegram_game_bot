import telebot
import random
import os

# Replace this with your real token
TOKEN = os.environ.get("BOT_TOKEN", "7224316622:AAEhVGroHMqp-7B1cFdYwQFLHXWFm4tC_M8")

bot = telebot.TeleBot(TOKEN)

# /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "🎮 Welcome to the Ashenafi Game Bot!\nYou can play /coinflip or /dice. More games coming soon!")

# /coinflip command
@bot.message_handler(commands=['coinflip'])
def handle_coinflip(message):
    result = random.choice(['🪙 Heads', '🪙 Tails'])
    bot.reply_to(message, f"You flipped: {result}")

# /dice command
@bot.message_handler(commands=['dice'])
def handle_dice(message):
    result = random.randint(1, 6)
    bot.reply_to(message, f"🎲 You rolled: {result}")

# Catch-all for unknown commands or messages
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    if message.text.startswith('/'):
        bot.reply_to(message, "⚠️ Unknown command.\nTry /start, /coinflip, or /dice.")
    else:
        bot.reply_to(message, "I only respond to specific commands:\n/start, /coinflip, /dice")

# Start the bot
print("Bot is running...")
bot.infinity_polling()
