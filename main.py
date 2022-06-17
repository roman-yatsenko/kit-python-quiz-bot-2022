from aiogram import (
    Bot,
    Dispatcher,
    executor,
    types,
)
from aiogram.utils import deep_linking

import config
from quiz import Quiz

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

quiz_db = {} # quiz info
quiz_owners = {} # quiz owners info

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message) -> None:
    """Start command handler"""
    if message.chat.type == types.ChatType.PRIVATE:
        poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        poll_keyboard.add(types.KeyboardButton(
            text='Создать тест',
            request_poll=types.KeyboardButtonPollType(type=types.PollType.QUIZ)
        ))
        poll_keyboard.add(types.KeyboardButton(text='Отмена'))
        await message.answer('Нажмите на кнопку и создайте тест!',
                            reply_markup=poll_keyboard)
    else:
        words = message.text.split()
        if len(words) == 1:
            bot_info = await bot.get_me()
            keyboard = types.InlineKeyboardMarkup()
            move_to_pm_button = types.InlineKeyboardButton(
                text="Перейти к боту",
                url=f't.me/{bot_info.username})?start=anything'
            )
            keyboard.add(move_to_pm_button)
            await message.reply('Не выбран тест. Создайте тест в чате с ботом',
                reply_markup=keyboard)
        else:
            quiz_owner = quiz_owners(words[1])
            if not quiz_owner:
                await message.reply('Неправильный тест. Попробуйте создать другой')
                return
            for quiz in quiz_db[quiz_owner]:
                if quiz.quiz_id == words[1]:
                    msg = await bot.send_poll(
                        chat_id=message.chat_id,
                        question=quiz.question,
                        is_anonymous=False,
                        options=quiz.options,
                        type='quiz',
                        correct_option_id=quiz.correct_option_id
                    )
                    quiz_owners[msg.poll.id] = quiz_owner
                    del quiz_owners[words[1]]
                    quiz.quiz_id = msg.poll.id
                    quiz.chat_id = msg.chat.id
                    quiz.message_id = msg.message_id

@dp.message_handler(lambda message: message.text == 'Отмена')
async def action_cancel(message: types.Message) -> None:
    """Cancel action handler"""
    await message.answer('Действие отменено. Введите /start, чтоы начать заново',
        reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(content_types=['poll'])
async def msg_with_poll(message: types.Message) -> None:
    """Message with poll(quiz) handler"""
    user_id = str(message.from_user.id)
    # if user is unknown
    if not quiz_db.get(user_id):
        quiz_db[user_id] = []
    
    # quiz type check
    if message.poll.type != 'quiz':
        await message.reply('Извините, я принимаю только тесты!')
        return
    
    # quiz saving
    quiz_db[user_id].append(Quiz(
        quiz_id=message.poll.id,
        question=message.poll.question,
        options=[option.text for option in message.poll.options],
        correct_option_id=message.poll.correct_option_id,
        owner_id=user_id
    ))
    quiz_owners[message.poll.id] = user_id

    await message.reply(
        f'Тест сохранен. Общее количество тестов: {len(quiz_db[user_id])}'
    )

@dp.inline_handler()
async def inline_query(query: types.InlineQuery) -> None:
    """Inline query handler"""
    results = []
    user_quizes = quiz_db.get(query.from_user.id)
    if user_quizes:
        for quiz in user_quizes:
            keyboard = types.InlineKeyboardMarkup()
            start_quiz_button = types.InlineKeyboardButton(
                text='Отправить в группу',
                url=await deep_linking.get_startgroup_link(quiz.quiz_id)
            )
            keyboard.add(start_quiz_button)
            results.append(types.InlineQueryResultArticle(
                id=quiz.quiz_id,
                title=quiz.question,
                input_message_content=types.InputTextMessageContent(
                    message_text='Отправьте кнопку ниже для отправки теста в группу'
                ),
                reply_markup=keyboard
            ))
    await query.answer(switch_pm_text='Создать тест', switch_pm_parameter='-',
        results=results, cache_time=120, is_personal=True)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
