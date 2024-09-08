from bot.config import *
from telebot import types


@bot.callback_query_handler(func=lambda call: call.data.startswith('model_'), state=CalculatorStates.choose_model)
async def choose_ths(call):
    if call.data == 'back':
        selected_model = context_manager.current_asic[call.message.chat.id]['model']
        context_manager.current_asic[call.message.chat.id]['number'] = ''
    else:
        selected_model = call.data.split('_')[1]

    context_manager.fill_current_asic(call.message.chat.id, model=selected_model)

    thss = {asic.ths for asic in asic_data if asic.model == selected_model}

    current_context_data = context_manager.current_asic.get(call.message.chat.id, {})
    message_text = (f'🟢 Алгоритм: <em>{current_context_data.get("algorithm")}</em>\n'
                    f'🟢 Монета: <em>{current_context_data.get("coin")}</em>\n'
                    f'🟢 Производитель: <em>{current_context_data.get("manufacturer")}</em>\n'
                    f'🟢 Модель: <em>{selected_model}</em>\n'
                    '...Выберите TH/s')

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=ths, callback_data=f'ths_{ths}') for ths in thss]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='back'))
    await bot.edit_message_text(message_text, call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup, parse_mode='HTML')
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_ths)