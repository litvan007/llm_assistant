from telebot.async_telebot import AsyncTeleBot
from telebot import types
import asyncio

import logging

from model_wrapper import ModelWrapper

"""
get_text_messages - обработка любого текстового сообщения, в том числе того, что отправился при нажатии кнопки.

Методы, реализующие одноименные команды телеграм-боту:
start
help
generate
checkmodel
model
"""
logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger.info('Started')

TOKEN = "My token"

model_wrapper = ModelWrapper() # внутри класса описание
bot = AsyncTeleBot(TOKEN)

@bot.message_handler(commands=['help'])
async def help(message):
    help_message = """Доступны следующие команды:
/start старт бота
/model выбор модели
/checkmodel посмотреть, как модель сейчас загружена
/generate сгенерировать текст по контексту (можно использовать без введения команды)
"""
    await bot.send_message(message.from_user.id, help_message)


@bot.message_handler(commands=['start'])
async def start(message):
    await bot.send_message(message.from_user.id, "Привет! Для знакомства с доступными командами введите /help")

@bot.message_handler(commands=['model'])
async def model(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("StatLM")
    btn2 = types.KeyboardButton("GPT")
    btn3 = types.KeyboardButton("Llama")
    markup.add(btn1, btn2, btn3)
    await bot.send_message(message.from_user.id, "Выберите модель для генерации", reply_markup=markup)


@bot.message_handler(commands=['checkmodel'])
async def checkmodel(message):
    await bot.send_message(message.from_user.id, f"Текущая модель: {str(model_wrapper.current_model_name)}")


@bot.message_handler(commands=['generate'])
async def generate(message):
    await bot.send_message(message.from_user.id,
                     "Введите текст (вопрос, на который нужно ответить, либо текст, который нужно продолжить)")


@bot.message_handler(content_types=['text'])
async def get_text_messages(message):
    logger.info(f'<{message.text}>')
    if message.text in ['StatLM', 'GPT', 'Llama']:
        logger.info(f'@{message.text}@')
        status, result = await model_wrapper.load(message.text, test_inference=True)
        if status:
            await bot.send_message(message.from_user.id, "Подгружено")
            logger.info(f"Inited model: {(model_wrapper.current_model_name)}")
        else:
            await bot.send_message(message.from_user.id, f"Проблемы с загрузкой модели, ниже описаны ошибки.\n{result}")
            logger.info(f"Problems to init model: {str(model_wrapper.current_model_name)}")
    else:
        status, result = await model_wrapper.generate(message.text)
        if status:
            await bot.send_message(message.from_user.id, result)
            logger.info(f"With model: {str(model_wrapper.current_model_name)} gained text: {result}")
        else:
            await bot.send_message(message.from_user.id, f"Проблемы с генерацией, ниже описаны ошибки.\n{result}")



asyncio.run(bot.polling(non_stop=True, request_timeout=90))
