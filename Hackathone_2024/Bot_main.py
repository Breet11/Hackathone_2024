
import asyncio
import logging
import sys
import re
import datetime

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.utils.markdown import hbold
from aiogram.filters.command import Command
from aiogram import F

import request

TOKEN = '7031013964:AAEGyUmbxX5A3mxY4FmWNfZn48EDbndkWPA' #https://t.me/Hackathone_2024_bot

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

commands = {'/start': 'To start the bot', '/help': 'To check existing commands', '/rate_news': ' To rate website. Write url of english news website'}

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:

    """
    This handler receives messages with `/start` command
    """

    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")

    command_info = "\n".join([f"{command}: {description}" for command, description in commands.items()])
    answer = "Here are the list of existing commands: "
    await message.answer(f"{hbold(answer)} \n{command_info}")

    kb = [
        [
            types.KeyboardButton(text="/start"),
            types.KeyboardButton(text="/help"),
            types.KeyboardButton(text="/rate_news"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Choose command"
    )
    await message.answer("Please choose command", reply_markup=keyboard)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    command_info = "\n".join([f"{command}: {description}" for command, description in commands.items()])
    answer = "Here are the list of existing commands: "
    await message.answer(f"{hbold(answer)} \n{command_info}")

@dp.message(Command("rate_news"))
async def cmd_rate_news(message: Message, command: CommandObject):

    if command.args is None:
        await message.reply("You didn't write url after command")
        return

    await message.answer("Please wait a moment while the chatbot processes your request")

    metadata_result = request.extract(request.METADATA_EXTRACTOR,[
        {
            "content": f"{command.args}",
            "language": "EMPTY"
        }
    ])
    for item in metadata_result:
        title = item['Title']
        author = item['Author']
        date = item['Published date']

    if title is not None:
        eval_title = 1
        title_message = "✅ True"
    else:
        eval_title = 0
        title_message = "❌ False"
    if author is not None:
        eval_author = 0.75
        author_message = "✅ True"
    else:
        eval_author = 0
        author_message = "❌ False"
    if date is not None:
        eval_date = 0.75
        date_message = "✅ True"
    else:
        eval_date = 0
        date_message = "❌ False"

    clickbait_result = request.extract(request.CLICKBAIT_EXTRACTOR,[
        {
            "content": f"{title}",
            "language": "EMPTY"
        }
    ])
    clickbait_message = clickbait_result[0]['categories'][0]['label']
    eval_clickbait = 0
    if clickbait_message == "not clickbait":
        clickbait_message = "✅ " + clickbait_message
        eval_clickbait = 1
    if clickbait_message == "clickbait":
        clickbait_message = "❌ " + clickbait_message

    #await message.answer(clickbait_result[0]['categories'][0]['label'])

    text_result = request.extract(request.CONTENT_EXTRACTOR,[
        {
            "content": f"{command.args}",
            "language": "EMPTY"
        }
    ])
    for item in text_result:
        text = item['text']

    #a way to count quotes (lazy one)
    num_quotes = (text.count('“') + text.count('”'))/2

    if num_quotes >= 7:
        eval_quotes = 0.5
        quotes_message = "✅ True"
    else:
        eval_quotes = 0
        quotes_message = "❌ False"

    entity_result = request.extract(request.ENTITY_EXTRACTOR, [
        {
            "content": f"{text}",
            "language": "xxx"
        }
    ])
    type_count = {}
    first_entry = entity_result[0]
    entities = first_entry.get('entities', [])

    for entity in entities:
        entity_type = entity.get('type')
        if entity_type in type_count:
            type_count[entity_type] += 1
        else:
            type_count[entity_type] = 1

    count = type_count.values()
    total_count = sum(count)
    print(f"Total Count: {total_count}")

    if total_count >= 60:
        eval_entities = 1
        entities_message = "✅ True"
    else:
        eval_entities = 0
        entities_message = "❌ False"

    evaluation = eval_entities + eval_title + eval_date + eval_author + eval_quotes + eval_clickbait

    await message.answer(f"Has title: {title_message}\n Is clickbait: {clickbait_message}\n Has date: {date_message}\n Has author: {author_message}\n More than 60 entities: {entities_message}\n\nFinal score: {evaluation}/5")



@dp.message(F.text)
async def echo_handler(message: types.Message) -> None:

    # Send a copy of the received message
    await message.answer("This is wrong command, please use /help to check list of commands")



async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())