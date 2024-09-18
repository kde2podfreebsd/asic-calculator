from bot.config import *
from bot.handlers.algorithm import choose_algorithm
from bot.handlers.blockchain import choose_blockchain
from bot.handlers.manufacturer import choose_manufacturer
from bot.handlers.model import choose_model
from bot.handlers.ths import choose_ths
from bot.handlers.count import choose_count
from bot.handlers.menu import *

@bot.callback_query_handler(func=lambda call: call.data == 'back')
async def back_inline_handler(call):
    current_state = await bot.get_state(user_id=call.from_user.id)
    # print(current_state)
    await bot.delete_state(call.from_user.id)

    if current_state == CalculatorStates.choose_algorithm.name:
        await send_main_menu(call.message.chat.id)

    if current_state == CalculatorStates.choose_blockchain.name:
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_algorithm)
        await choose_algorithm(call)

    if current_state == CalculatorStates.choose_manufacturer.name:
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_blockchain)
        await choose_blockchain(call)

    if current_state == CalculatorStates.choose_model.name:
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_manufacturer)
        await choose_manufacturer(call)

    if current_state == CalculatorStates.choose_ths.name:
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_model)
        await choose_model(call)

    if current_state == CalculatorStates.choose_count.name:
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_ths)
        await choose_ths(call)

    if current_state == CalculatorStates.confirm_additional_device.name:
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_count)
        await choose_count(call)
