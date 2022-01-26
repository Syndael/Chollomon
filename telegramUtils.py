import telebot, configParserUtils
from telebot.types import InputMediaPhoto

def enviarMensajeTelegram(telegramChatId, telegramMensaje, fotoImg = None, fotoPrc = None):
    telegramBotToken = configParserUtils.getConfigParserGet(constants.TELEGRAM_BOT_TOKEN)

    if(telegramBotToken and telegramChatId):
        telegramService = telebot.TeleBot(telegramBotToken)

        media = []
        if fotoImg and fotoPrc:
            media.append(InputMediaPhoto (open(fotoImg, "rb"), caption = telegramMensaje))
            media.append(InputMediaPhoto (open(fotoPrc, "rb")))
            telegramService.send_media_group(telegramChatId, media)
        elif fotoImg:
            media.append(InputMediaPhoto (open(fotoImg, "rb"), caption = telegramMensaje))
            telegramService.send_media_group(telegramChatId, media)
        else:
            telegramService.send_message(telegramChatId, telegramMensaje)
