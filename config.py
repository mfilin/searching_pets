from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = 'PUT API TOKEN HERE'


bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)