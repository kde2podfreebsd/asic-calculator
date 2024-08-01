from telebot import types
from bot.config import bot
from telebot.asyncio_handler_backends import State, StatesGroup
from bitinfo import crypto_full_names

# TODO - добавить чекер подписки

class CalculatorStates(StatesGroup):
    choose_blockchain = State()
    choose_count = State()

msg_ids = dict()
user_data = dict()

@bot.message_handler(commands=['start', 'menu'])
async def start(message) -> None:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('📈 Калькулятор доходности'),
        types.KeyboardButton('🛒 Наши устройства')
    )

    msg = await bot.send_message(message.chat.id, 'ℹ️ Вы можете расчитать доходность устройства или выбрать и заказать устройства из нашего каталога!', reply_markup=markup)
    msg_ids[message.chat.id] = msg.id
    await bot.set_state(message.chat.id, CalculatorStates.choose_blockchain)

@bot.message_handler(state=CalculatorStates.choose_blockchain)
async def choose_blockchain(message):
    await bot.delete_message(message.chat.id, msg_ids[message.chat.id])
    blockchains = list(crypto_full_names.values())
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=blockchain, callback_data=blockchain) for blockchain in blockchains]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    msg = await bot.send_message(message.chat.id, 'ℹ️ Выберите блокчейн', reply_markup=markup)
    msg_ids[message.chat.id] = msg.id

@bot.callback_query_handler(func=lambda call: call.data in list(crypto_full_names.values()))
async def choose_blockchain(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(text='M30s 90 TH/S - 640 USD', callback_data='asic_'))
    await bot.edit_message_text('ℹ️ Выберите устройство', call.message.chat.id, msg_ids[call.message.chat.id])
    await bot.edit_message_reply_markup(call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('asic_'))
async def choose_count(call):
    user_data[call.from_user.id] = {'number': ''}
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=str(i), callback_data=f'num_{i}') for i in range(1, 10)]
    buttons.append(types.InlineKeyboardButton(text='Стереть', callback_data='clear'))
    buttons.append(types.InlineKeyboardButton(text='0', callback_data='num_0'))
    buttons.append(types.InlineKeyboardButton(text='Выбрать', callback_data='submit'))
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    await bot.edit_message_text('ℹ️ Выберите количество', call.message.chat.id, msg_ids[call.message.chat.id])
    await bot.edit_message_reply_markup(call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_count)

@bot.callback_query_handler(func=lambda call: call.data.startswith('num_'))
async def handle_number(call):
    user_id = call.from_user.id
    current_number = user_data.get(user_id, {}).get('number', '')
    number = call.data.split('_')[1]
    
    if len(current_number) < 6:
        current_number += number
    user_data[user_id]['number'] = current_number

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=str(i), callback_data=f'num_{i}') for i in range(1, 10)]
    buttons.append(types.InlineKeyboardButton(text='Стереть', callback_data='clear'))
    buttons.append(types.InlineKeyboardButton(text='0', callback_data='num_0'))
    buttons.append(types.InlineKeyboardButton(text='Выбрать', callback_data='submit'))
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    
    number_display = f'Кол-во: {current_number}'
    await bot.edit_message_text(number_display, call.message.chat.id, msg_ids[call.message.chat.id])
    await bot.edit_message_reply_markup(call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'clear')
async def handle_clear(call):
    user_id = call.from_user.id
    user_data[user_id]['number'] = ''
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=str(i), callback_data=f'num_{i}') for i in range(1, 10)]
    buttons.append(types.InlineKeyboardButton(text='0', callback_data='num_0'))
    buttons.append(types.InlineKeyboardButton(text='Стереть', callback_data='clear'))
    buttons.append(types.InlineKeyboardButton(text='Выбрать', callback_data='submit'))
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    
    await bot.edit_message_text('Кол-во: ', call.message.chat.id, msg_ids[call.message.chat.id])
    await bot.edit_message_reply_markup(call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'submit')
async def handle_submit(call):
    # Переход к следующему состоянию
    await bot.edit_message_text(f'Вы выбрали количество: {user_data[call.from_user.id]["number"]}', call.message.chat.id, msg_ids[call.message.chat.id])

    




