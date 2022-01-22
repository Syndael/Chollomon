import io, os, logging, constants, configParserUtils, spreedUtils, imgDownloader, telegramUtils
logging.basicConfig(filename=os.path.join(os.path.abspath(os.path.dirname(__file__)), constants.LOG_FILE), filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)
from os.path import exists

def enviarMensajeTelegram(telegramChatId, telegramMensaje, fotoImg = None, fotoPrc = None):
    telegramBotToken = configParserUtils.getConfigParserGet('telegramBotToken')

    if(telegramBotToken and telegramChatId):
        telegramService = telebot.TeleBot(telegramBotToken)

        media = []
        if fotoImg and fotoPrc:
            media.append(InputMediaPhoto (open(fotoImg, "rb"), caption = telegramMensaje))
            media.append(InputMediaPhoto (open(fotoPrc, "rb")))
            telegramService.send_media_group(telegramChatId, media)
        else:
            telegramService.send_message(telegramChatId, telegramMensaje)

def buscarCartas(prefijo, cantidad, format, cartasMix):
    cartaIndex = 1
    while cartaIndex <= cantidad:
        numCarta = str(prefijo + constants.SEPARADOR_TEMP + format.format(cartaIndex))
        logging.info(str("Buscando " + numCarta))
        if numCarta in cartasMix:
            alterIndex = 1
            finAlter = False
            while not finAlter:
                numCartaAlter = str(numCarta + constants.PRE_ALTER + str(alterIndex))
                logging.info(str("Buscando " + numCartaAlter))
                if numCartaAlter not in cartasMix:
                    rutaImg = descargarImg(numCartaAlter)
                    if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
                        logging.info(str("No encontrado " + numCartaAlter + " fin de búsqueda de " + numCarta))
                        finAlter = True
                    else:
                        #añadir carta al listado
                        logging.info(str("Añadiendo " + numCartaAlter))
                        telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet('telegramChatCanalCartasId'), str("Nueva carta añadida " + numCartaAlter + " " + formatUrlCartaGlobal(numCartaAlter)), rutaImg)
                        spreedUtils.nuevaFila(numCarta, numCartaAlter, formatUrlCartaGlobal(numCartaAlter))

                alterIndex = alterIndex + 1
        else:
            rutaImg = descargarImg(numCarta)
            if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
                if cartaIndex == 1:
                    logging.info(str("No encontrado " + numCarta + " fin de colecciones"))
                    return True
                else:
                    logging.info(str("No encontrado " + numCarta + " fin de temporada"))
                    return False

        cartaIndex = cartaIndex + 1

def formatUrlCartaGlobal(numCarta):
    return str(constants.URL_TEMPLATE_GLOBAL + numCarta + constants.URLS_IMG_FORMAT)

def descargarImg(numCarta):
    urlImg = formatUrlCartaGlobal(numCarta)
    return imgDownloader.descargarImg("tmpFinder.png", urlImg)

def buscarCartasNuevas():
    cartasMix = {c:None for c in spreedUtils.getNumerosMixCartas()}.keys()
    categorias = [{constants.PREFIJO: constants.PRE_TEMP_BT, constants.TEMPORADA: True, constants.CANTIDAD: 999, constants.FORMAT: '{0:03d}'}, {constants.PREFIJO: constants.PRE_TEMP_P, constants.TEMPORADA: False, constants.CANTIDAD: 999, constants.FORMAT: '{0:03d}'}, {constants.PREFIJO: constants.PRE_TEMP_ST, constants.TEMPORADA: True, constants.CANTIDAD: 99, constants.FORMAT: '{0:02d}'}, {constants.PREFIJO: constants.PRE_TEMP_EX, constants.TEMPORADA: True, constants.CANTIDAD: 999, constants.FORMAT: '{0:03d}'}]
    for categoria in categorias:
        if categoria.get(constants.TEMPORADA):
            ultimaTemporada = False
            temporadaIndex = 1
            while not ultimaTemporada:
                temporada = str(categoria.get(constants.PREFIJO) + str(temporadaIndex))
                ultimaTemporada = buscarCartas(temporada, categoria.get(constants.CANTIDAD), categoria.get(constants.FORMAT), cartasMix)
                temporadaIndex = temporadaIndex + 1
        elif not categoria.get(constants.TEMPORADA):
            buscarCartas(categoria.get(constants.PREFIJO), categoria.get(constants.CANTIDAD), categoria.get(constants.FORMAT), cartasMix)
