from bot.config import *
from telebot import types

@bot.callback_query_handler(func=lambda call: True, state=CalculatorStates.choose_blockchain)
async def choose_manufacturer(call):
    if call.data == 'back':
        selected_coin = context_manager.current_asic[call.message.chat.id]['coin']
    else:
        selected_coin = call.data

    context_manager.fill_current_asic(call.message.chat.id, coin=selected_coin)

    manufacturers = {asic.manufacturer for asic in asic_data if asic.coin == selected_coin}

    message_text = (f'🟢 Алгоритм: {context_manager.current_asic.get(call.message.chat.id, {}).get("algorithm")}\n'
                    f'🟢 Монета: {selected_coin}\n'
                    '...Выберите производителя')

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=manufacturer, callback_data=f'manufacturer_{manufacturer}') for manufacturer in manufacturers]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='back'))
    await bot.edit_message_text(message_text, call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_manufacturer)
