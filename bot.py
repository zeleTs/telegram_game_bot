# === Import required libraries ===
import telebot              # For Telegram bot functions
import os                   # To access environment variables (like BOT_TOKEN)
import random               # For rolling dice and coin flip

# === Load bot token securely from environment variable ===
TOKEN = os.environ.get("BOT_TOKEN", "7224316622:AAEhVGroHMqp-7B1cFdYwQFLHXWFm4tC_M8") # "YOUR_BOT_TOKEN_HERE" is fallback for local testing
bot = telebot.TeleBot(TOKEN)  # Create a bot instance

# === /start command ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "🎮 Welcome to Ashenafi Game Bot!\nUse /coinflip, /dice, or /ludo to begin.")

# === /coinflip command ===
@bot.message_handler(commands=['coinflip'])
def handle_coinflip(message):
    result = random.choice(['🪙 Heads', '🪙 Tails'])  # Randomly choose heads or tails
    bot.reply_to(message, f"You flipped: {result}")

# === /dice command ===
@bot.message_handler(commands=['dice'])
def handle_dice(message):
    result = random.randint(1, 6)  # Random number from 1 to 6
    bot.reply_to(message, f"🎲 You rolled: {result}")

# --------------------------------------
# === LUDO GAME FUNCTIONALITY STARTS HERE ===
# --------------------------------------

# Dictionary to store active games per chat
games = {}  # key = chat_id, value = Game object

# Define the Game class to manage player turns, rolls, and positions
class Game:
    def __init__(self):
        self.players = []         # List of players as tuples: (user_id, username)
        self.positions = {}       # Tracks position of each player: user_id → position
        self.turn = 0             # Index of current player in self.players
        self.started = False      # Indicates if the game has started
        self.finished = False     # True if someone won

    def add_player(self, user_id, username):
        if self.started:
            return False, "🚫 Game already started."
        if user_id in [p[0] for p in self.players]:
            return False, "🧑 You're already in the game!"
        self.players.append((user_id, username))
        self.positions[user_id] = 0  # Start position
        return True, f"✅ {username} joined the game."

    def start_game(self):
        if len(self.players) < 2:
            return False, "❗ At least 2 players are needed to start."
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

        # Check if player won
        if self.positions[user_id] >= 30:
            self.finished = True
            return status + f"\n🏆 {self.players[self.turn][1]} wins the game!"
        
        # Move to next player
        self.turn = (self.turn + 1) % len(self.players)
        next_player = self.players[self.turn][1]
        return status + f"\n➡️ Now it's {next_player}'s turn."

# === /ludo command ===
@bot.message_handler(commands=['ludo'])
def create_game(message):
    chat_id = message.chat.id
    if chat_id in games and not games[chat_id].finished:
        bot.reply_to(message, "⚠️ A game is already running. Finish it first.")
    else:
        games[chat_id] = Game()  # Create new game for this chat
        bot.reply_to(message, "🎮 New Ludo game created!\nPlayers, type /join to participate.")

# === /join command ===
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

# === /startgame command ===
@bot.message_handler(commands=['startgame'])
def start_game(message):
    chat_id = message.chat.id
    if chat_id not in games:
        bot.reply_to(message, "❌ No game to start.")
        return

    success, msg = games[chat_id].start_game()
    bot.reply_to(message, msg)

# === /roll command ===
@bot.message_handler(commands=['roll'])
def roll_dice(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in games:
        bot.reply_to(message, "❌ No game in progress. Start one with /ludo.")
        return

    msg = games[chat_id].roll_dice(user_id)
    bot.reply_to(message, msg)

# === Catch-all handler for unknown messages ===
@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.reply_to(message, "❓ Unknown command. Try /start, /coinflip, /dice, /ludo, /join, /startgame, or /roll.")

# === Start the bot ===
print("Bot is running...")
bot.infinity_polling()
