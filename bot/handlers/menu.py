from bot.config import *
from bot.handlers.sub import *


@bot.message_handler(commands=['start', 'menu'])
async def start(message) -> None:
    user_id = message.chat.id

    if await is_user_subscribed(user_id):
        await send_main_menu(message.chat.id)
    else:
        await send_subscription_message(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
async def back_to_main_menu(call):
    await bot.delete_state(call.from_user.id)
    user_id = call.message.chat.id
    await bot.delete_message(chat_id=user_id, message_id=msg_ids[user_id])
    if await is_user_subscribed(user_id):
        await send_main_menu(call.message.chat.id)
    else:
        await send_subscription_message(call.message.chat.id)