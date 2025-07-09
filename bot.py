import telebot
import random
import os

# Replace this with your real token
TOKEN = os.environ.get("BOT_TOKEN", "7224316622:AAEhVGroHMqp-7B1cFdYwQFLHXWFm4tC_M8")

bot = telebot.TeleBot(TOKEN)


# Game state
games = {}  # chat_id: Game object

# Simple Game class to manage each game session
class Game:
    def __init__(self):
        self.players = []         # List of (user_id, username)
        self.positions = {}       # user_id: position
        self.turn = 0             # Index of current player in self.players
        self.started = False
        self.finished = False

    def add_player(self, user_id, username):
        if self.started:
            return False, "🚫 Game already started."
        if user_id in [p[0] for p in self.players]:
            return False, "🧑 You're already in the game!"
        self.players.append((user_id, username))
        self.positions[user_id] = 0
        return True, f"✅ {username} joined the game."

    def start_game(self):
        if len(self.players) < 2:
            return False, "❗ At least 2 players needed to start."
        self.started = True
        return True, f"🎲 Game started with {len(self.players)} players!\nIt's {self.players[0][1]}'s turn. Type /roll"

    def roll_dice(self, user_id):
        if self.finished:
            return "🏁 Game is already over."
        if self.players[self.turn][0] != user_id:
            return "⏳ Not your turn."

        roll = random.randint(1, 6)
        self.positions[user_id] += roll
        status = f"🎲 You rolled a {roll}! You're now at position {self.positions[user_id]}."

        # Check win
        if self.positions[user_id] >= 30:
            self.finished = True
            return status + f"\n🏆 {self.players[self.turn][1]} wins the game!"
        
        # Next turn
        self.turn = (self.turn + 1) % len(self.players)
        next_player = self.players[self.turn][1]
        return status + f"\n➡️ Now it's {next_player}'s turn."

# Start new game
@bot.message_handler(commands=['ludo'])
def create_game(message):
    chat_id = message.chat.id
    if chat_id in games and not games[chat_id].finished:
        bot.reply_to(message, "⚠️ A game is already running.")
    else:
        games[chat_id] = Game()
        bot.reply_to(message, "🎮 New Ludo game created!\nPlayers, type /join to participate.")

# Join a game
@bot.message_handler(commands=['join'])
def join_game(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.first_name

    if chat_id not in games:
        bot.reply_to(message, "❌ No active game. Start one with /ludo.")
        return

    success, msg = games[chat_id].add_player(user_id, username)
    bot.reply_to(message, msg)

# Start the game
@bot.message_handler(commands=['startgame'])
def start_game(message):
    chat_id = message.chat.id
    if chat_id not in games:
        bot.reply_to(message, "❌ No active game to start.")
        return

    success, msg = games[chat_id].start_game()
    bot.reply_to(message, msg)

# Roll the dice
@bot.message_handler(commands=['roll'])
def roll_dice(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in games:
        bot.reply_to(message, "❌ No game found. Start one with /ludo.")
        return

    msg = games[chat_id].roll_dice(user_id)
    bot.reply_to(message, msg)

# Fallback handler
@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.reply_to(message, "❓ Unknown command. Use /ludo, /join, /startgame, or /roll.")

# Start polling
print("Ludo bot is running...")
bot.infinity_polling()
