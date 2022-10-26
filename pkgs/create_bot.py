from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from .db import BotDb


ADMIN = 00000000
token = '000000:AAAAAAAAAAaaaaaaaaaa'

storage = MemoryStorage()
bot = Bot(token=token, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)
DB = BotDb('pkgs/cryptorank.db')
