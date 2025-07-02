import telebot
import random

# Paste your token from BotFather here
TOKEN = '7224316622:AAEhVGroHMqp-7B1cFdYwQFLHXWFm4tC_M8'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Welcome! Type /coinflip to flip a coin, or /dice to roll a die!")

@bot.message_handler(commands=['coinflip'])
def coinflip(message):
    result = random.choice(['Heads', 'Tails'])
    bot.reply_to(message, f"🪙 You flipped: {result}")

@bot.message_handler(commands=['dice'])
def dice(message):
    result = random.randint(1, 6)
    bot.reply_to(message, f"🎲 You rolled: {result}")

print("Bot is running...")
bot.polling()