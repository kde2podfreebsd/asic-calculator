from bot.config import *
from telebot import types

@bot.message_handler(state=CalculatorStates.choose_algorithm)
async def choose_algorithm(message):
    context_manager.clear(message.chat.id)
    await bot.delete_message(message.chat.id, msg_ids[message.chat.id])
    unique_algorithms = {asic.algorithm for asic in asic_data if isinstance(asic.algorithm, str)}

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=algorithm, callback_data=algorithm) for algorithm in unique_algorithms]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='main_menu'))
    msg = await bot.send_message(message.chat.id, 'Выберите алгоритм', reply_markup=markup)
    msg_ids[message.chat.id] = msg.id