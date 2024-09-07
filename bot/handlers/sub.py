from bot.config import *
from telebot import types

async def send_main_menu(chat_id):
    markup = get_main_menu_markup()
    msg = await bot.send_message(
        chat_id,
        'ℹ️ Вы можете рассчитать доходность устройства или выбрать и заказать устройства из нашего каталога!',
        reply_markup=markup
    )
    msg_ids[chat_id] = msg.id
    await bot.set_state(chat_id, CalculatorStates.choose_algorithm)

def get_main_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('📈 Калькулятор доходности'),
        types.KeyboardButton('🛒 Наши устройства')
    )
    return markup

async def is_user_subscribed(user_id):
    try:
        sub_status = await bot.get_chat_member(CHANNEL_ID, user_id)
        return False if sub_status.status == 'left' else True
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False

def get_subscription_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(text='Подписаться!', url="https://t.me/hahehihuha"))
    markup.add(types.InlineKeyboardButton(text='Проверить подписку', callback_data="check_sub"))
    return markup

async def send_subscription_message(chat_id):
    markup = get_subscription_markup()
    msg = await bot.send_message(
        chat_id,
        "Пожалуйста, подпишитесь на наш канал, чтобы использовать бота. [Подписаться](https://t.me/hahehihuha)",
        parse_mode='Markdown',
        reply_markup=markup
    )
    msg_ids[chat_id] = msg.id

@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
async def check_sub(call):
    user_id = call.message.chat.id
    if await is_user_subscribed(user_id):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await send_main_menu(call.message.chat.id)
    else:
        markup = get_subscription_markup()
        await bot.edit_message_text(
            "Вы не подписались:(\nПожалуйста, подпишитесь на наш канал, чтобы использовать бота. [Подписаться](https://t.me/hahehihuha)",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='Markdown'
        )
        await bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )