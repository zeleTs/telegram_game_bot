# === Import required libraries ===
import telebot              # For Telegram bot functions
import os                   # To access environment variables (like BOT_TOKEN)
import random               # For rolling dice and coin flip
import time
from telebot.types import ReplyKeyboardMarkup

# === Load bot token securely from environment variable ===
TOKEN = os.environ.get("BOT_TOKEN", "your_default_token")
bot = telebot.TeleBot(TOKEN)  # Create a bot instance

# === /start command ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "🎮 Welcome to Ashenafi Game Bot!\nUse /coinflip, /dice, or /ludo to begin.")

# === /coinflip command ===
@bot.message_handler(commands=['coinflip'])
def handle_coinflip(message):
    result = random.choice(['🪙 Heads', '🪙 Tails'])
    bot.reply_to(message, f"You flipped: {result}")

# === /dice command ===
@bot.message_handler(commands=['dice'])
def handle_dice(message):
    result = random.randint(1, 6)
    bot.reply_to(message, f"🎲 You rolled: {result}")

# === Token selection keyboard ===
def token_choice_keyboard():
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Token A', 'Token B')
    return markup

# === LUDO GAME FUNCTIONALITY ===
games = {}  # key = chat_id, value = Game object

class Game:
    def __init__(self):
        self.players = []
        self.positions = {}
        self.turn = 0
        self.started = False
        self.sixes_in_a_row = {}
        self.skip_turn = set()
        self.tokens = {}           # user_id → {'A': pos, 'B': pos}
        self.pending_move = {}     # user_id → dice roll
        self.finished = False

    def add_player(self, user_id, username):
        if self.started:
            return False, "🚫 Game already started."
        if user_id in [p[0] for p in self.players]:
            return False, "🧑 You're already in the game!"
        self.tokens[user_id] = {'A': 0, 'B': 0}
        self.players.append((user_id, username))
        self.positions[user_id] = 0
        self.sixes_in_a_row[user_id] = 0
        return True, f"✅ {username} joined the game."

    def start_game(self):
        if len(self.players) < 2:
            return False, "❗ At least 2 players are needed to start."
        self.started = True
        return True, f"🎲 Game started with {len(self.players)} players!\nIt's {self.players[0][1]}'s turn. Type /roll"

    def roll_dice(self, user_id):
        if self.finished:
            return "🏁 Game is already over.", None
        if self.players[self.turn][0] != user_id:
            return "⏳ Not your turn.", None
        if user_id in self.skip_turn:
            self.skip_turn.remove(user_id)
            self.sixes_in_a_row[user_id] = 0
            self.turn = (self.turn + 1) % len(self.players)
            next_player = self.players[self.turn][1]
            return f"⛔ You must skip this turn.\n➡️ Now it's {next_player}'s turn.", None

        roll = random.randint(1, 6)
        name = self.players[self.turn][1]
        self.pending_move[user_id] = roll
        return f"🎲 {name} rolled a {roll}.\nWhich token do you want to move?", token_choice_keyboard()

    def move_token(self, user_id, token, roll):
        name = [p[1] for p in self.players if p[0] == user_id][0]
        self.tokens[user_id][token] += roll
        status = f"🚀 {name} moved Token {token} by {roll} to position {self.tokens[user_id][token]}."

        for other_id in self.tokens:
            if other_id == user_id:
                continue
            for tkn, pos in self.tokens[other_id].items():
                if pos == self.tokens[user_id][token]:
                    other_name = [p[1] for p in self.players if p[0] == other_id][0]
                    self.tokens[other_id][tkn] = 0
                    status += f"\n💥 Landed on {other_name}'s Token {tkn}. Sent it back to 0!"

        if all(pos >= 30 for pos in self.tokens[user_id].values()):
            self.finished = True
            return status + f"\n🏆 {name} has finished both tokens and wins the game!"

        self.turn = (self.turn + 1) % len(self.players)
        next_name = self.players[self.turn][1]
        return status + f"\n➡️ Now it's {next_name}'s turn."

# === Telegram command handlers ===

@bot.message_handler(commands=['ludo'])
def create_game(message):
    chat_id = message.chat.id
    if chat_id in games and not games[chat_id].finished:
        bot.reply_to(message, "⚠️ A game is already running. Finish it first.")
    else:
        games[chat_id] = Game()
        bot.reply_to(message, "🎮 New Ludo game created!\nPlayers, type /join to participate.")

@bot.message_handler(func=lambda msg: msg.text in ['Token A', 'Token B'])
def choose_token(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if chat_id not in games:
        bot.reply_to(message, "❌ No active game.")
        return
    game = games[chat_id]
    if user_id not in game.pending_move:
        bot.reply_to(message, "❌ You have no pending move.")
        return

    token = 'A' if message.text == 'Token A' else 'B'
    roll = game.pending_move.pop(user_id)
    result = game.move_token(user_id, token, roll)
    bot.send_message(chat_id, result)

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

@bot.message_handler(commands=['startgame'])
def start_game(message):
    chat_id = message.chat.id
    if chat_id not in games:
        bot.reply_to(message, "❌ No game to start.")
        return

    success, msg = games[chat_id].start_game()
    bot.reply_to(message, msg)

@bot.message_handler(commands=['roll'])
def roll_dice_cmd(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in games:
        bot.reply_to(message, "❌ No game in progress. Start one with /ludo.")
        return

    text, markup = games[chat_id].roll_dice(user_id)
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.reply_to(message, "❓ Unknown command. Try /start, /coinflip, /dice, /ludo, /join, /startgame, or /roll.")

# === Start the bot ===
print("Bot is running...")
while True:
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"⚠️ Bot crashed: {e}")
        print("🔄 Restarting in 5 seconds...")
        time.sleep(5)
