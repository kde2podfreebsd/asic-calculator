import os
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup

load_dotenv()

CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

bot = AsyncTeleBot(
    os.getenv("TELEGRAM_BOT_TOKEN"),
    state_storage=StateMemoryStorage(),
    disable_notification=False,
    colorful_logs=False
)

DEVICES_PER_PAGE = 1

from gsheets import GoogleSheetsAPI
from context import ContextManager

context_manager = ContextManager()

g = GoogleSheetsAPI()
asic_data = g.serialize()

msg_ids = dict()
electricity_prices = {}

class CalculatorStates(StatesGroup):
    choose_algorithm = State()
    choose_blockchain = State()
    choose_manufacturer = State()
    choose_model = State()
    choose_ths = State()
    choose_count = State()
    confirm_additional_device = State()
    choose_price = State()
    finalize_selection = State()
    finish = State()