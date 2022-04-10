import logging
import os

import configParserUtils
import constants
import imgDownloader
import spreedUtils
import telegramUtils

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO, handlers=[logging.FileHandler(os.path.join(os.path.abspath(os.path.dirname(__file__)), configParserUtils.getConfigParserGet(constants.LOG_FILE)), mode='w', encoding='UTF-8'), logging.StreamHandler()])
from datetime import datetime


def buscarCartas(prefijo, cantidad, formateo, cartasMix):
	cartaIndex = 1
	while cartaIndex <= cantidad:
		numCarta = str(prefijo + constants.SEPARADOR_TEMP + formateo.format(cartaIndex))
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
						addCarta(numCarta, numCartaAlter, rutaImg)

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
			else:
				addCarta(numCarta, numCarta, rutaImg)

		cartaIndex = cartaIndex + 1


def addCarta(numCarta, numCartaAlter, rutaImg):
	if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "0":
		textoExtra = "(Global)"
	elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "1":
		textoExtra = "(Japón)"
	else:
		logging.error("No se ha definido modo de busqueda")
		raise Exception("No se ha definido modo de busqueda")

	logging.info(str("Añadiendo " + numCartaAlter + textoExtra))
	telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_CHAT_CANAL_CARTAS_ID), str("Nueva carta añadida " + numCartaAlter + " " + textoExtra + " " + formatUrlCarta(numCartaAlter)), rutaImg)

	if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "0":
		spreedUtils.nuevaFila(numCarta, numCartaAlter, formatUrlCarta(numCartaAlter), 0)
	elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "1":
		spreedUtils.nuevaFila(numCarta, numCartaAlter, formatUrlCarta(numCartaAlter), 1)


def formatUrlCarta(numCarta):
	if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "0":
		return str(constants.URL_TEMPLATE_GLOBAL + numCarta + constants.URLS_IMG_FORMAT)
	elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "1":
		return str(constants.URL_TEMPLATE_JP + numCarta + constants.URLS_IMG_FORMAT)
	else:
		logging.error("No se ha definido modo de busqueda")
		raise Exception("No se ha definido modo de busqueda")


def descargarImg(numCarta):
	urlImg = formatUrlCarta(numCarta)
	return imgDownloader.descargarImg("tmpFinder.png", urlImg)


def buscarCartasNuevas():
	cartasMix = {c: None for c in spreedUtils.getNumerosMixCartas()}.keys()
	categorias = [{constants.PREFIJO: constants.PRE_TEMP_BT, constants.TEMPORADA: True, constants.CANTIDAD: 999, constants.FORMAT: '{0:03d}'}, {constants.PREFIJO: constants.PRE_TEMP_P, constants.TEMPORADA: False, constants.CANTIDAD: 999, constants.FORMAT: '{0:03d}'}, {constants.PREFIJO: constants.PRE_TEMP_ST, constants.TEMPORADA: True, constants.CANTIDAD: 99, constants.FORMAT: '{0:02d}'},
		{constants.PREFIJO: constants.PRE_TEMP_EX, constants.TEMPORADA: True, constants.CANTIDAD: 999, constants.FORMAT: '{0:03d}'}]
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


if __name__ == '__main__':
	try:
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), "Buscando cartas nuevas a las %s" % datetime.now().strftime("%H:%M"))
		buscarCartasNuevas()
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), "Fin búsqueda de cartas nuevas a las %s" % datetime.now().strftime("%H:%M"))
	except Exception as e:
		msgError = "Error buscando cartas"
		if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "0":
			msgError = str(msgError + "(Global)")
		elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "1":
			msgError = str(msgError + "(Japón)")
		else:
			logging.error("No se ha definido modo de búsqueda")
		logging.error(msgError)
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), msgError)
