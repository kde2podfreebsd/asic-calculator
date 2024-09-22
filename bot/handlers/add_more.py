from bot.config import *
from telebot import types


@bot.callback_query_handler(func=lambda call: call.data == 'add_more', state=CalculatorStates.confirm_additional_device)
async def add_more_device(call):
    await bot.delete_message(call.message.chat.id, msg_ids[call.message.chat.id])
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_algorithm)
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    unique_algorithms = {asic.algorithm for asic in asic_data if isinstance(asic.algorithm, str)}
    buttons = [types.InlineKeyboardButton(text=algorithm, callback_data=f'algorithm_{algorithm}') for algorithm in unique_algorithms]

    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    
    markup.add(types.InlineKeyboardButton(text='Отмена', callback_data='back_to_submit'))
    
    msg = await bot.send_message(call.message.chat.id, 'Выберите алгоритм', reply_markup=markup)
    msg_ids[call.message.chat.id] = msg.id