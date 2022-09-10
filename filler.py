import logging
import os

import configParserUtils
import constants
import finder
import spreedUtils
import telegramUtils

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO, handlers=[logging.FileHandler(os.path.join(os.path.abspath(os.path.dirname(__file__)), configParserUtils.getConfigParserGet(constants.LOG_FILE)), mode='w', encoding='UTF-8'), logging.StreamHandler()])
from datetime import datetime


def rellenarImagen(indice, numCarta):
	logging.info("Rellando imagen de la carta {}".format(numCarta))

	formateoConst = constants.FORMATEO_1
	rutaImg = finder.descargarImg(numCarta, formateoConst)
	if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
		formateoConst = constants.FORMATEO_2
		rutaImg = finder.descargarImg(numCarta, formateoConst)
	if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
		formateoConst = constants.FORMATEO_3
		rutaImg = finder.descargarImg(numCarta, formateoConst)
	if os.path.getsize(rutaImg) > constants.TAMANHO_MIN_IMG:
		spreedUtils.rellenarImagen(indice, finder.formatUrlCarta(formateoConst.format(numCarta)))


def rellenarCartas():
	if configParserUtils.getConfigParserGet(constants.COPIAR_FORMULA) == "1":
		for carta in spreedUtils.getCartasSinFormulas():
			logging.info('Copiando formulas de {}'.format(carta.get(constants.CODIGO)))
			spreedUtils.rellenarFormula(carta.get(constants.FILA))

	if configParserUtils.getConfigParserGet(constants.COPIAR_DATOS_GENERALES) == "1":
		for carta in spreedUtils.getCartasSinDatos():
			spreedUtils.rellenarDatos(carta.get(constants.FILA), carta.get(constants.NUMERO))

	if configParserUtils.getConfigParserGet(constants.COPIAR_IMAGEN) == "1":
		for carta in spreedUtils.getCartasSinImagen():
			rellenarImagen(carta.get(constants.FILA), carta.get(constants.CODIGO).replace(constants.TAG_SELLADO, ""))


if __name__ == '__main__':
	try:
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), "Rellenando datos a las %s" % datetime.now().strftime("%H:%M"))
		rellenarCartas()
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), "Fin relleno datos a las %s" % datetime.now().strftime("%H:%M"))
	except Exception as e:
		msgError = "Error rellenado datos"
		logging.error(msgError, e)
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), msgError)
