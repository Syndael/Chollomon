import logging
import os
import time

import configParserUtils
import constants
import filler
import imgDownloader
import spreedUtils
import telegramUtils

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO, handlers=[logging.FileHandler(os.path.join(os.path.abspath(os.path.dirname(__file__)), configParserUtils.getConfigParserGet(constants.LOG_FILE)), mode='w', encoding='UTF-8'), logging.StreamHandler()])
from datetime import datetime

listaCNNum = []


def buscarCartas(prefijo, cantidad, formateo, cartasMix):
	cartaIndex = 1
	excepciones = ['EX2-002']
	while cartaIndex <= cantidad:
		try:
			numCarta = str(prefijo + constants.SEPARADOR_TEMP + formateo.format(cartaIndex))
			logging.info("Buscando {}".format(numCarta))
			formateoConst = constants.FORMATEO_1
			if numCarta in cartasMix:
				descargarAlters(cartasMix, numCarta)
			else:
				rutaImg = descargarImg(numCarta, formateoConst)
				if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
					formateoConst = constants.FORMATEO_2
					rutaImg = descargarImg(numCarta, formateoConst)
				if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
					formateoConst = constants.FORMATEO_3
					rutaImg = descargarImg(numCarta, formateoConst)
				if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
					if cartaIndex == 1:
						logging.info("No encontrado {} fin de colecciones".format(numCarta))
						return True
					elif numCarta not in excepciones:
						logging.info("No encontrado {} fin de temporada".format(numCarta))
						return False
				else:
					addCarta(numCarta, formateoConst)
					descargarAlters(cartasMix, numCarta)
		except Exception as ex:
			logging.error("Error buscando la carta {}".format(str(prefijo + constants.SEPARADOR_TEMP + formateo.format(cartaIndex))), ex)
		cartaIndex = cartaIndex + 1


def descargarAlters(cartasMix, numCarta):
	descargarAlter(cartasMix, numCarta, 1)
	descargarAlter(cartasMix, numCarta, 2)


def descargarAlter(cartasMix, numCarta, modo):
	alterIndex = 1
	finAlter = False
	while not finAlter:
		if modo == 1:
			numCartaAlter = str(numCarta + constants.PRE_ALTER + str(alterIndex))
		else:
			if alterIndex == 1:
				numCartaAlter = str(numCarta + constants.PRE_ALTER_20220811)
			else:
				numCartaAlter = str(numCarta + constants.PRE_ALTER_20220811 + str(alterIndex))

		logging.info(str("Buscando alter " + numCartaAlter))
		formateoConst = constants.FORMATEO_1
		if numCartaAlter not in cartasMix:
			rutaImg = descargarImg(numCartaAlter, formateoConst)
			if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
				formateoConst = constants.FORMATEO_2
				rutaImg = descargarImg(numCartaAlter, formateoConst)
			if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
				formateoConst = constants.FORMATEO_3
				rutaImg = descargarImg(numCartaAlter, formateoConst)
			if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
				logging.info(str("No encontrado " + numCartaAlter + " fin de búsqueda de " + numCarta))
				finAlter = True
			else:
				addCarta(numCartaAlter, formateoConst)

		alterIndex = alterIndex + 1


def addCarta(numCarta, formateo):
	logging.info('Añadiendo {}'.format(numCarta))
	if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "1":
		spreedUtils.nuevaFila(numCarta, numCarta)
	else:
		spreedUtils.nuevaFila(numCarta, None)
	urlImg = formatUrlCarta(formateo.format(numCarta))
	imgDownloader.descargarImg(constants.FORMATEO_IMG.format(numCarta), urlImg)
	listaCNNum.append({constants.CODIGO: numCarta, constants.URL_IMAGEN: urlImg})


def formatUrlCarta(numCarta):
	if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "0":
		return str(constants.URL_TEMPLATE_GLOBAL + numCarta + constants.URLS_IMG_FORMAT)
	elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "1":
		return str(constants.URL_TEMPLATE_JP + numCarta + constants.URLS_IMG_FORMAT)
	elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "2":
		coleccion = numCarta.split("-")[0].replace('e_', '')
		return str(constants.URL_TEMPLATE_GLOBAL_20220811 + coleccion + "/" + numCarta + constants.URLS_IMG_FORMAT)
	else:
		logging.error("No se ha definido modo de busqueda")
		raise Exception("No se ha definido modo de busqueda")


def descargarImg(numCarta, formateo):
	urlImg = formatUrlCarta(formateo.format(numCarta))
	return imgDownloader.descargarImg("tmpFinder.png", urlImg)


def buscarCartasNuevas():
	if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "1":
		cartasMix = {c: None for c in spreedUtils.getNumerosCartas(constants.CODIGOJP)}.keys()
	else:
		cartasMix = {c: None for c in spreedUtils.getNumerosCartas(constants.CODIGO)}.keys()

	categorias = [
		{constants.PREFIJO: constants.PRE_TEMP_BT, constants.TEMPORADA: True, constants.CANTIDAD: 999, constants.FORMAT: '{0:03d}'},
		{constants.PREFIJO: constants.PRE_TEMP_P, constants.TEMPORADA: False, constants.CANTIDAD: 999, constants.FORMAT: '{0:03d}'},
		{constants.PREFIJO: constants.PRE_TEMP_ST, constants.TEMPORADA: True, constants.CANTIDAD: 99, constants.FORMAT: '{0:02d}'},
		{constants.PREFIJO: constants.PRE_TEMP_EX, constants.TEMPORADA: True, constants.CANTIDAD: 999, constants.FORMAT: '{0:03d}'}
	]
	for categoria in categorias:
		if categoria.get(constants.TEMPORADA):
			ultimaTemporada = False
			temporadaIndex = 1
			while not ultimaTemporada:
				temporada = str(categoria.get(constants.PREFIJO) + str(temporadaIndex))
				ultimaTemporada = buscarCartas(temporada, categoria.get(constants.CANTIDAD), categoria.get(constants.FORMAT), cartasMix)
				if temporada != 'ST11':
					ultimaTemporada = False
				temporadaIndex = temporadaIndex + 1
				enviarTelegram()
		elif not categoria.get(constants.TEMPORADA):
			buscarCartas(categoria.get(constants.PREFIJO), categoria.get(constants.CANTIDAD), categoria.get(constants.FORMAT), cartasMix)
			enviarTelegram()


def enviarTelegram():
	if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "0":
		textoExtra = "(Global)"
	elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "1":
		textoExtra = "(Japón)"
	elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "2":
		textoExtra = "(Global B+)"
	else:
		logging.error("No se ha definido modo de busqueda")
		raise Exception("No se ha definido modo de busqueda")

	tiempoMinimoBusquedaTelegramStr = configParserUtils.getConfigParserGet(constants.TIEMPO_MINIMO_BUSQUEDA_TELEGRAM)
	tiempoMinimoBusquedaTelegram = 3
	if len(tiempoMinimoBusquedaTelegramStr) != 0:
		tiempoMinimoBusquedaTelegram = int(tiempoMinimoBusquedaTelegramStr)

	for carta in listaCNNum:
		try:
			numCarta = carta.get(constants.CODIGO)
			nombreImg = str(constants.FORMATEO_IMG.format(numCarta))
			rutaImg = os.path.join(os.path.abspath(os.path.dirname(__file__)), "img", nombreImg)
			telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_CHAT_CANAL_CARTAS_ID), str("Nueva carta añadida " + numCarta + " " + textoExtra + " " + carta.get(constants.URL_IMAGEN)), rutaImg)
			time.sleep(tiempoMinimoBusquedaTelegram)
		except Exception as exc:
			logging.error("Error notificando la carta {}".format(carta.get(constants.CODIGO)), exc)
	listaCNNum.clear()


if __name__ == '__main__':
	try:
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), "Buscando cartas nuevas a las %s" % datetime.now().strftime("%H:%M"))
		buscarCartasNuevas()
		filler.rellenarCartas()
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), "Fin búsqueda de cartas nuevas a las %s" % datetime.now().strftime("%H:%M"))
	except Exception as e:
		msgError = "Error buscando cartas"
		if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "0":
			msgError = str(msgError + "(Global)")
		elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "1":
			msgError = str(msgError + "(Japón)")
		elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == "2":
			msgError = str(msgError + "(Global B+)")
		else:
			logging.error("No se ha definido modo de búsqueda")
		logging.error(msgError, e)
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), msgError)
