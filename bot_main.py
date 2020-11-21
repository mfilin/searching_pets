import logging

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

import admin
import db
from config import bot, dp
from states import Form


@dp.message_handler(commands="start", state="*")
async def cmd_start(message: types.Message):
	choose = types.InlineKeyboardButton("🐶Найти питомца", callback_data="choose")
	about_us = types.InlineKeyboardButton("О нас", callback_data="about_us")
	how_to = types.InlineKeyboardButton("Передача питомца", callback_data="how_to")
	inst = types.InlineKeyboardButton(
		"Наш инстаграм", url="https://www.instagram.com/empasi_net"
	)
	vk = types.InlineKeyboardButton("Группа ВК", url="https://vk.com/empasi_net")
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.row(choose)
	keyboard.add(about_us, how_to, inst, vk)

	await bot.send_message(
		message.from_user.id,
		"🐾Привет! Это бот проекта Эмпаси.\n\n\
Этот проект помогает людям найти нового питомца из приюта. Мы собираем информацию из приютов Волгограда, \
а также от наших друзей-волонтеров. Через этот бот вы сможете подобрать себе нового питомца, а также узнать больше о проекте.",
		reply_markup=keyboard,
	)


@dp.callback_query_handler(text="about_us", state="*")  # if cb.data == 'yes'
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
	await bot.answer_callback_query(query.id)
	await bot.send_message(query.from_user.id, "Тут может быть информация о нас")


@dp.callback_query_handler(text="how_to", state="*")  # if cb.data == 'yes'
async def how_to(query: types.CallbackQuery):
	await bot.answer_callback_query(query.id)

	await bot.answer_callback_query(query.id)
	await bot.send_message(
		query.from_user.id, "Тут может быть информация о том как можно получить питомца"
	)


@dp.callback_query_handler(text="choose", state="*")
async def stat_choosing(query: types.CallbackQuery):
	await bot.answer_callback_query(query.id)

	cat = types.InlineKeyboardButton("🐶Собака", callback_data="Собака")
	dog = types.InlineKeyboardButton("🐈Кошка", callback_data="Кошка")
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.add(cat, dog)
	await Form.CHOOSING.set()
	await bot.send_message(
		query.from_user.id,
		"1/6\nДавай начнем подбор. \n\n\
Для начала скажите какого вы хотите питомца:",
		reply_markup=keyboard,
	)


@dp.callback_query_handler(text="Кошка", state=Form.CHOOSING)
@dp.callback_query_handler(text="Собака", state=Form.CHOOSING)
async def gender(query: types.CallbackQuery, state: FSMContext):
	await bot.answer_callback_query(query.id)

	await state.update_data(cat_or_dog=query.data)
	male = types.InlineKeyboardButton("Мужской", callback_data="Мужской")
	female = types.InlineKeyboardButton("Женский", callback_data="Женский")
	both = types.InlineKeyboardButton("Неважно", callback_data="Любой пол")
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.add(male, female, both)

	await bot.edit_message_text(
		"2/6\nОтлично! Теперь выберите пол питомца:",
		message_id=query.message.message_id,
		chat_id=query.message.chat.id,
	)

	await bot.edit_message_reply_markup(
		reply_markup=keyboard,
		message_id=query.message.message_id,
		chat_id=query.message.chat.id,
	)


age_list = [
	"2-4 Месяца",
	"4-6 Месяцев",
	"6-12 Месяцев",
	"1-3 Года",
	"3-7 Лет",
	"Старше 7 лет",
]


@dp.callback_query_handler(text="Мужской", state=Form.CHOOSING)
@dp.callback_query_handler(text="Женский", state=Form.CHOOSING)
@dp.callback_query_handler(text="Любой пол", state=Form.CHOOSING)
async def age(query: types.CallbackQuery, state: FSMContext):
	await bot.answer_callback_query(query.id)
	await state.update_data(gender=[query.data])
	buttons = []

	for i in age_list:
		buttons.append((i, i))

	keyboard = types.InlineKeyboardMarkup(row_width=2)

	keyboard.add(
		*(
			types.InlineKeyboardButton(text, callback_data=data)
			for text, data in buttons
		)
	)
	keyboard.add(types.InlineKeyboardButton("Любой возраст", callback_data="Любой возраст"))
	keyboard.add(types.InlineKeyboardButton("Продолжить", callback_data="Продолжить1"))

	await bot.edit_message_text(
		'3/6\nОтлично! Теперь выберите возраст питомца. \n\n\
Здесь можно выбрать несколько кнопок. Нажмите на кнопку "Продолжить", когда будете готовы.\
Чтобы отменить выбор, нажмите на кнопку еще раз.',
		message_id=query.message.message_id,
		chat_id=query.message.chat.id,
	)

	await bot.edit_message_reply_markup(
		reply_markup=keyboard,
		message_id=query.message.message_id,
		chat_id=query.message.chat.id,
	)

@dp.callback_query_handler(text="Любой возраст", state=Form.CHOOSING)
@dp.callback_query_handler(text="Продолжить1", state=Form.CHOOSING)
async def fur_type(query: types.CallbackQuery, state: FSMContext):
	await bot.answer_callback_query(query.id)

	got_keyboard = []
	age_output = []

	for i in query.message.reply_markup.inline_keyboard:
		for j in i:
			got_keyboard.append(j.text)

	for i in got_keyboard:
		if i[0] == "✅":
			age_output.append(i[1:])

	if query.data == 'Любой возраст':
		age_output = list(age_list)

	await state.update_data(age=age_output)

	b1 = types.InlineKeyboardButton("Короткая", callback_data="Короткая")
	b2 = types.InlineKeyboardButton(
		"Длинная/пушистая", callback_data="Длинная/пушистая"
	)
	b3 = types.InlineKeyboardButton("Любая", callback_data="Любой тип шерсти")
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.add(b1, b2, b3)

	await bot.edit_message_text(
		"4/6\nТип шерсти:",
		message_id=query.message.message_id,
		chat_id=query.message.chat.id,
	)
	await bot.edit_message_reply_markup(
		reply_markup=keyboard,
		message_id=query.message.message_id,
		chat_id=query.message.chat.id,
	)


color_list = (
	"Черный",
	"Белый",
	"Черно-белый",
	"Рыжий",
	"Коричневый",
	"Двухцветнный",
	"Палевый (светлый)",
	"Тигровый",
	"Черепаховый",
)


@dp.callback_query_handler(text="Короткая", state=Form.CHOOSING)
@dp.callback_query_handler(text="Длинная/пушистая", state=Form.CHOOSING)
@dp.callback_query_handler(text="Любой тип шерсти", state=Form.CHOOSING)
async def choose_color(query: types.CallbackQuery, state: FSMContext):
	await bot.answer_callback_query(query.id)

	await state.update_data(fur=[query.data])

	buttons = []
	for i in color_list:
		buttons.append((i, i))

	async with state.proxy() as data:
		animal_type = data["cat_or_dog"]
	if animal_type == "Собака":
		buttons.pop(-1)
		buttons.pop(-1)
	elif animal_type == "Кошка":
		buttons.pop(6)

	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.add(
		*(
			types.InlineKeyboardButton(text, callback_data=data)
			for text, data in buttons
		)
	)
	keyboard.add(types.InlineKeyboardButton("Любой цвет", callback_data="Любой цвет"))
	keyboard.add(types.InlineKeyboardButton("Продолжить", callback_data="Продолжить2"))
	await bot.edit_message_text(
		"5/6\nВыберите цвет:",
		message_id=query.message.message_id,
		chat_id=query.message.chat.id,
	)
	await bot.edit_message_reply_markup(
		reply_markup=keyboard,
		message_id=query.message.message_id,
		chat_id=query.message.chat.id,
	)


@dp.callback_query_handler(lambda c: c.data in cat_characters, state=Form.CHOOSING)
@dp.callback_query_handler(lambda c: c.data in dog_characters, state=Form.CHOOSING)
@dp.callback_query_handler(lambda c: c.data in color_list, state=Form.CHOOSING)
@dp.callback_query_handler(lambda c: c.data in age_list, state=Form.CHOOSING)
async def update_tick(query: types.CallbackQuery, state: FSMContext):
	await bot.answer_callback_query(query.id)
	got_keyboard = []
	for i in query.message.reply_markup.inline_keyboard:
		for j in i:
			got_keyboard.append(j.text)

	cdata_list = []
	for i in query.message.reply_markup.inline_keyboard:
		for j in i:
			cdata_list.append(j.callback_data)

	clicked = cdata_list.index(query.data)

	if got_keyboard[clicked][0] != "✅":
		got_keyboard[clicked] = "✅" + got_keyboard[clicked]
	else:
		got_keyboard[clicked] = got_keyboard[clicked][1:]

	for i in range(len(got_keyboard)):
		got_keyboard[i] = (got_keyboard[i], cdata_list[i])

	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.add(
		*(
			types.InlineKeyboardButton(text, callback_data=data)
			for text, data in got_keyboard[:-2]
		)
	)
	keyboard.row(
		types.InlineKeyboardButton(
			got_keyboard[-2][0], callback_data=got_keyboard[-2][1]
		)
	)
	
	keyboard.row(
		types.InlineKeyboardButton(
			got_keyboard[-1][0], callback_data=got_keyboard[-1][1]
		)
	)
	await bot.edit_message_reply_markup(
		reply_markup=keyboard,
		message_id=query.message.message_id,
		chat_id=query.message.chat.id,
	)

@dp.callback_query_handler(text="Любой цвет", state=Form.CHOOSING)
@dp.callback_query_handler(text="Продолжить2", state=Form.CHOOSING)
async def check_character(query: types.CallbackQuery, state: FSMContext):
	await bot.answer_callback_query(query.id)

	got_keyboard = []
	color_output = []

	for i in query.message.reply_markup.inline_keyboard:
		for j in i:
			got_keyboard.append(j.text)

	for i in got_keyboard:
		if i[0] == "✅":
			color_output.append(i[1:])

	if query.data == 'Любой цвет':
		color_output = list(color_list)

	await state.update_data(color=color_output)

	async with state.proxy() as data:
		pressed_age = data["age"]

	if (
		(age_list[2] in pressed_age)
		or (age_list[3] in pressed_age)
		or (age_list[4] in pressed_age)
		or (age_list[5] in pressed_age)
	):
		await character(query, state)
	else:
		await final(query, state)


dog_characters = ("Холерик", 
	"Меланхолик", 
	"Cангвиник", 
	"Флегматик"
)
cat_characters = (
	"Независимый",
	"Средне-независимый",
	"Дружелюбный",
	"Дружелюбный-активный",
	"Дружелюбный-спокойный",
)

async def character(query: types.CallbackQuery, state: FSMContext):

	buttons = []
	async with state.proxy() as data:
		animal_type = data["cat_or_dog"]
	if animal_type == "Собака":
		for i in dog_characters:
			buttons.append((i, i))
	elif animal_type == "Кошка":
		for i in cat_characters:
			buttons.append((i, i))

	keyboard = types.InlineKeyboardMarkup(row_width=2)

	keyboard.add(
		*(
			types.InlineKeyboardButton(text, callback_data=data)
			for text, data in buttons
		)
	)
	keyboard.add(types.InlineKeyboardButton("Любой характер", callback_data="Любой характер"))
	keyboard.add(types.InlineKeyboardButton("Завершить", callback_data="Завершить"))

	await bot.edit_message_text(
		"6/6\nТип Характера:",
		message_id=query.message.message_id,
		chat_id=query.message.chat.id,
	)
	await bot.edit_message_reply_markup(
		reply_markup=keyboard,
		message_id=query.message.message_id,
		chat_id=query.message.chat.id,
	)

@dp.callback_query_handler(text="Любой характер", state=Form.CHOOSING)
@dp.callback_query_handler(text="Завершить", state=Form.CHOOSING)
async def final(query: types.CallbackQuery, state: FSMContext):

	got_keyboard = []
	character_output = []

	for i in query.message.reply_markup.inline_keyboard:
		for j in i:
			got_keyboard.append(j.text)

	for i in got_keyboard:
		if i[0] == "✅":
			character_output.append(i[1:])

	if query.data == 'Любой характер':
		character_output = list(cat_characters) + list(dog_characters)

	async with state.proxy() as data:
		animal_type = data["cat_or_dog"]
		gender = data["gender"]
		age = data["age"]
		fur = data["fur"]
		color = data["color"]

	blank = ", "

	await bot.send_message(
		query.from_user.id,
		f"""Конец!
🌿Вы выбрали следующие параметры поиска:

{animal_type}
Пол: <b>{blank.join(gender)}</b>
Возраст: <b>{blank.join(age)}</b>
Шерсть: <b>{blank.join(fur)}</b>
Цвет: <b>{blank.join(color)}</b>
Тип характера: <b>{blank.join(character_output)}</b>

Вот что мы нашли в нашей базе:

		""",
		parse_mode=ParseMode.HTML,
	)

	if gender[0] == 'Любой пол':
		gender = ['Мужской', 'Женский']
	if fur[0] == 'Любой тип шерсти':
		fur = ['Длинная/пушистая', 'Короткая']

	found = db.find_animal(animal_type, gender, age, fur, color, character_output)
	for animal in found:
		await bot.send_photo(query.from_user.id, animal[1])
		await bot.send_message(query.from_user.id, animal[0])


if __name__ == "__main__":
	executor.start_polling(dp, skip_updates=True)
