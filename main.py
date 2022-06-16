from aiogram import (
    Bot,
    Dispatcher,
    executor,
    types,
)

import config

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

@dp.message_handler()
async def echo(message: types.Message) -> None:
    await message.reply(message.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
