import logging

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram import Bot, Dispatcher, executor, types

from config import bot, dp
from states import Form

from bot_main import age_list, color_list, dog_characters, cat_characters

import time
import bot_main
import db


@dp.message_handler(commands='admin', state ='*')
async def check_admin(message: types.Message):

	if db.check_admin(message.from_user.username) == True:

		add = types.InlineKeyboardButton('Добавить нового питомца', callback_data='add_new_pet')
		see = types.InlineKeyboardButton('Посмотреть весь список питомцев', callback_data='see')
		delete = types.InlineKeyboardButton('Удалить анкету питомца', callback_data='delete')
		keyboard = types.InlineKeyboardMarkup(row_width=2)
		keyboard.row(add)
		keyboard.row(see)
		keyboard.row(delete)

		await bot.send_message(message.from_user.id, "Панель администратора.", reply_markup=keyboard)



@dp.callback_query_handler(text='see', state ='*')
async def see_all(query: types.CallbackQuery,state: FSMContext):
	await bot.answer_callback_query(query.id)
	fetched = db.get_all_animals()

	for animal in fetched: 
		try:
			await bot.send_message(query.from_user.id, f"""

{animal[1]}
Пол: <b>{animal[2]}</b>
Возраст: <b>{animal[3]}</b>
Шерсть: <b>{animal[4]}</b>
Цвет: <b>{animal[5]}</b>
Тип характера: <b>{animal[6]}</b>

Описание:
{animal[0]}

Номер (для удаления): <b>{animal[8]}</b>
				""",parse_mode=ParseMode.HTML)
			await bot.send_photo(query.from_user.id,animal[7]) 
		except:
			pass
	await check_admin(query)



@dp.callback_query_handler(text='delete', state ='*')
async def delete_pet(query: types.CallbackQuery,state: FSMContext):
	await bot.answer_callback_query(query.id)

	await bot.send_message(query.from_user.id, """
Введите номер животного, которого вы хотите убрать из базы.\
Номер можно посмотреть, нажав на кнопку 'посмотреть весь список питомцев'. 

Если вы передумали удалять, напишите 'Отмена'""")


	await Form.DELETING.set()


@dp.message_handler(content_types=['text'], state=Form.DELETING)
async def text(message: types.message, state: FSMContext):

	if message.text.lower() == 'отмена':
		await cancel_message(message,state)
	else:
		try:
			db.delete_animal(int(message.text))
		except ValueError:
			await bot.send_message(message.from_user.id, "Ошибка ;( Попробуйте еще раз\nНадо написать номер анкеты цифрой")
			return
		await bot.send_message(message.from_user.id, "Анкета удалена")
		await state.finish()
		await check_admin(message)





@dp.callback_query_handler(text='add_new_pet', state ='*')
async def add_new(query: types.CallbackQuery,state: FSMContext):
	await bot.answer_callback_query(query.id)
	dog = types.InlineKeyboardButton('🐶Собака', callback_data='Собака')
	cat = types.InlineKeyboardButton('🐈Кошка', callback_data='Кошка')
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.row(cat,dog)
	await bot.send_message(query.from_user.id, "Добавление питомца 1/6\nВведите тип питомца:", reply_markup=keyboard)
	await Form.ADDING.set()


@dp.callback_query_handler(text='Кошка', state=Form.ADDING)
@dp.callback_query_handler(text='Собака', state=Form.ADDING)
async def cat_or_dog(query: types.CallbackQuery,state: FSMContext):
	await bot.answer_callback_query(query.id)
	await state.update_data(cat_or_dog=query.data)
	dog = types.InlineKeyboardButton('Женский', callback_data='Женский')
	cat = types.InlineKeyboardButton('Мужской', callback_data='Мужской')
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.row(cat,dog)
	await bot.edit_message_text("Добавление питомца 2/6\nВведите пол:",message_id = query.message.message_id, chat_id =  query.message.chat.id)
	await bot.edit_message_reply_markup(reply_markup = keyboard, message_id = query.message.message_id, chat_id =  query.message.chat.id)

@dp.callback_query_handler(text='Мужской', state=Form.ADDING)
@dp.callback_query_handler(text='Женский', state=Form.ADDING)
async def select_gender(query: types.CallbackQuery,state: FSMContext):
	await bot.answer_callback_query(query.id)
	await state.update_data(gender=query.data)

	buttons = []

	for i in age_list:
		buttons.append((i,i))

	print(buttons)
	keyboard = types.InlineKeyboardMarkup(row_width=2)

	keyboard.add(*(types.InlineKeyboardButton(text, callback_data=data) for text, data in buttons))
	await bot.edit_message_text("Добавление питомца 3/6\nВведите возраст питомца:",message_id = query.message.message_id, chat_id =  query.message.chat.id)
	await bot.edit_message_reply_markup(reply_markup = keyboard, message_id = query.message.message_id, chat_id =  query.message.chat.id)


@dp.callback_query_handler(lambda c: c.data in age_list, state=Form.ADDING)
async def inline_kb_answer_callback_handler(query: types.CallbackQuery,state: FSMContext):
	await bot.answer_callback_query(query.id)
	await state.update_data(age=query.data)

	b1 = types.InlineKeyboardButton('Короткая', callback_data='Короткая')
	b2 = types.InlineKeyboardButton('Длинная/пушистая', callback_data='Длинная/пушистая')
	keyboard = types.InlineKeyboardMarkup(row_width=3)
	keyboard.add(b1,b2)
	
	await bot.edit_message_text("Добавление питомца 4/6\nВведите тип шерсти:",message_id = query.message.message_id, chat_id =  query.message.chat.id)
	await bot.edit_message_reply_markup(reply_markup = keyboard, message_id = query.message.message_id, chat_id =  query.message.chat.id)


@dp.callback_query_handler(text='Короткая', state=Form.ADDING)
@dp.callback_query_handler(text='Длинная/пушистая', state=Form.ADDING)
async def choose_color(query: types.CallbackQuery, state: FSMContext):
	await bot.answer_callback_query(query.id)
	await state.update_data(fur = query.data)

	print('it was a dog!!')
	buttons = []
	for i in color_list:
		buttons.append((i,i))

	async with state.proxy() as data:
		animal_type = data['cat_or_dog']
	if animal_type == 'Собака':
		buttons.pop(-1)
		buttons.pop(-1)
	elif animal_type == 'Кошка':
		buttons.pop(6)
		

	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.add(*(types.InlineKeyboardButton(text, callback_data=data) for text, data in buttons))
	await bot.edit_message_text('Добавление питомца 5/6\n\nВыберите цвет:',message_id = query.message.message_id, chat_id =  query.message.chat.id)
	await bot.edit_message_reply_markup(reply_markup = keyboard, message_id = query.message.message_id, chat_id =  query.message.chat.id)



@dp.callback_query_handler(lambda c: c.data in color_list, state =Form.ADDING)
async def check_character(query: types.CallbackQuery, state: FSMContext):
	await bot.answer_callback_query(query.id)
	await state.update_data(color=query.data)

	async with state.proxy() as data:
		pressed_age = data['age']
	print('pressed age IS::::' + str(pressed_age))
	
	if (age_list[2] in pressed_age) or \
	(age_list[3] in pressed_age) or \
	(age_list[4] in pressed_age) or \
	(age_list[5] in pressed_age):
		await character(query,state)      
	else:
		await bot.edit_message_text('Питомец слишком мал, поэтому характер на добавляем',message_id = query.message.message_id, chat_id =  query.message.chat.id)
		time.sleep(2)
		await description(query,state)






async def character(query: types.CallbackQuery, state: FSMContext):

	buttons = []
	async with state.proxy() as data:
		animal_type = data['cat_or_dog']
	if animal_type == 'Собака':
		for i in dog_characters:
			buttons.append((i,i))
	elif animal_type == 'Кошка':
		for i in cat_characters:
			buttons.append((i,i))
   
	keyboard = types.InlineKeyboardMarkup(row_width=2)

	keyboard.add(*(types.InlineKeyboardButton(text, callback_data=data) for text, data in buttons))

	await bot.edit_message_text('6/6\nТип Характера:',message_id = query.message.message_id, chat_id =  query.message.chat.id)
	await bot.edit_message_reply_markup(reply_markup = keyboard, message_id = query.message.message_id, chat_id =  query.message.chat.id)




@dp.callback_query_handler(lambda c: c.data in dog_characters, state =Form.ADDING)
@dp.callback_query_handler(lambda c: c.data in cat_characters, state =Form.ADDING)
async def description(query: types.CallbackQuery, state: FSMContext):
	await state.update_data(character=query.data)
	await bot.send_message(query.from_user.id, 'Напишите описание питомца. \n\nПоместите все описание в одно сообщение, и  \
когда все будет готово, отправьте его сюда в чат. Бот добавит ваше следующее сообщение в базу данных как описание.')




@dp.message_handler(content_types=['text'], state=Form.ADDING)
async def add_photo(message: types.message, state: FSMContext):

	await state.update_data(description=message.text)
	await message.reply('Описание добавлено')

	await bot.send_message(message.from_user.id, 'Остался последний шаг! Пришлите в чат одно изображение питомца.\
 Бот добавит ваше последнее фото в чате.')


@dp.message_handler(content_types=['photo'], state=Form.ADDING)
async def photo(message: types.message, state: FSMContext):
	print('photo file id was: ' + str(message.photo[0].file_id))
	await state.update_data(photo_id=message.photo[0].file_id)
	await message.reply('Фото добавлено')
	async with state.proxy() as data:
		animal_type = data['cat_or_dog']
		gender = data['gender']
		age = data['age']
		fur = data['fur']
		color = data['color']
		character = data['character']
		description = data['description']

	await bot.send_message(message.from_user.id, f"""
{animal_type}
Пол: <b>{gender}</b>
Возраст: <b>{age}</b>
Шерсть: <b>{fur}</b>
Цвет: <b>{color}</b>
Тип характера: <b>{character}</b>




Описание:
{description}
""",parse_mode = ParseMode.HTML)

	yes = types.InlineKeyboardButton('Добавить', callback_data='Добавить в базу данных')
	no = types.InlineKeyboardButton('Заново', callback_data='Отмена')
	keyboard = types.InlineKeyboardMarkup(row_width=3)
	keyboard.add(yes,no)
	await bot.send_message(message.from_user.id, 'Добавить питомца в базу или заполнить форму заново?',reply_markup=keyboard)


@dp.callback_query_handler(text='Добавить в базу данных', state=Form.ADDING)
async def add(query: types.CallbackQuery, state: FSMContext):
	await bot.answer_callback_query(query.id)
	async with state.proxy() as data:
		animal_type = data['cat_or_dog']
		gender = data['gender']
		age = data['age']
		fur = data['fur']
		color = data['color']
		character = data['character']
		description = data['description']
		photo_id = data['photo_id']

	db.new_animal(animal_type, gender, age, fur, color, character,description, photo_id)
	await bot.send_message(query.from_user.id, 'Питомец добавлен!')
	await state.finish()
	
	await check_admin(query)

@dp.callback_query_handler(text='Отмена', state=Form.ADDING)
async def cancel(query: types.CallbackQuery, state: FSMContext):
	await bot.answer_callback_query(query.id)
	await bot.send_message(query.from_user.id, 'Отмена ввода')
	await state.finish()
	await check_admin(query)

async def cancel_message(message: types.message, state: FSMContext):
	await bot.send_message(message.from_user.id, 'Отмена ввода')
	await state.finish()
	await check_admin(message)


