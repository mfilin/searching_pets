
#@dp.callback_query_handler(lambda c: c.data in age_dict.keys(), state =Form.CHOOSING)
async def age(query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(query.id)
    
    got_keyboard = []

    for i in query.message.reply_markup.inline_keyboard:
        for j in i:
            got_keyboard.append(j.text)

    clicked = int(query.data[3])

    if got_keyboard[clicked][0] != '✅':
        got_keyboard[clicked] = '✅' + got_keyboard[clicked] 
    else:
        got_keyboard[clicked] = got_keyboard[clicked][1:] 

    b1 = types.InlineKeyboardButton(got_keyboard[0], callback_data='age0')
    b2 = types.InlineKeyboardButton(got_keyboard[1], callback_data='age1')
    b3 = types.InlineKeyboardButton(got_keyboard[2], callback_data='age2')
    b4 = types.InlineKeyboardButton(got_keyboard[3], callback_data='age3')
    b5 = types.InlineKeyboardButton(got_keyboard[4], callback_data='age4')
    b6 = types.InlineKeyboardButton(got_keyboard[5], callback_data='age5')
    cont = types.InlineKeyboardButton('Продолжить', callback_data='Продолжить1')
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(b1,b2,b3,b4,b5,b6,cont)
    await bot.edit_message_reply_markup(reply_markup = keyboard, message_id = query.message.message_id, chat_id =  query.message.chat.id)
