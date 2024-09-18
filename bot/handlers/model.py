from bot.config import *
from telebot import types

@bot.callback_query_handler(func=lambda call: call.data.startswith('manufacturer_'), state=CalculatorStates.choose_manufacturer)
async def choose_model(call):
    if call.data == 'back':
        selected_manufacturer = context_manager.current_asic[call.message.chat.id]['manufacturer']
    else:
        selected_manufacturer = call.data.split('_')[1]

    context_manager.fill_current_asic(call.message.chat.id, manufacturer=selected_manufacturer)

    models = {asic.model for asic in asic_data if asic.manufacturer == selected_manufacturer and asic.coin == context_manager.current_asic[call.message.chat.id]['coin']}

    current_context_data = context_manager.current_asic.get(call.message.chat.id, {})
    message_text = (f'🟢 Алгоритм: {current_context_data.get("algorithm")}\n'
                    f'🟢 Монета: {current_context_data.get("coin")}\n'
                    f'🟢 Производитель: {selected_manufacturer}\n'
                    '...Выберите модель')

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=model, callback_data=f'model_{model}') for model in models]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='back'))
    await bot.edit_message_text(message_text, call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_model)
    current_state = await bot.get_state(user_id=call.from_user.id)
    print(current_state)