import logging
import os

import configParserUtils
import constants
import finder
import scan
import spreedUtils
import telegramUtils

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO, handlers=[logging.FileHandler(os.path.join(os.path.abspath(os.path.dirname(__file__)), configParserUtils.getConfigParserGet(constants.LOG_FILE)), mode='w', encoding='UTF-8'), logging.StreamHandler()])
from datetime import datetime


def rellenarCartas():
	if configParserUtils.getConfigParserGet(constants.COPIAR_FORMULA) == '1':
		for carta in spreedUtils.getCartasSinFormulas():
			logging.info('COPIAR_FORMULA {0}'.format(carta.get(constants.CODIGO)))
			spreedUtils.rellenarFormula(carta.get(constants.FILA))

	if configParserUtils.getConfigParserGet(constants.COPIAR_DATOS_GENERALES) == '1':
		for carta in spreedUtils.getCartasSinDatos():
			logging.info('COPIAR_DATOS_GENERALES de {0}'.format(carta.get(constants.CODIGO)))
			spreedUtils.rellenarDatos(carta.get(constants.FILA), carta.get(constants.NUMERO))

	if configParserUtils.getConfigParserGet(constants.COPIAR_CODIGO_IMAGEN) == '1':
		if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '2' or configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '0':
			for carta in spreedUtils.getCartasSinCodigoEu():
				logging.info('COPIAR_CODIGOS_EU de {0}'.format(carta.get(constants.CODIGO)))
				cod = finder.buscarCodigoImagen(carta.get(constants.CODIGO))
				if cod:
					spreedUtils.rellenarCodigoEu(carta.get(constants.FILA), cod)

		if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '1':
			for carta in spreedUtils.getCartasSinCodigoJp():
				logging.info('COPIAR_CODIGOS_JP de {0}'.format(carta.get(constants.CODIGO)))
				cod = finder.buscarCodigoImagen(carta.get(constants.CODIGO))
				if cod:
					spreedUtils.rellenarCodigoJp(carta.get(constants.FILA), cod)

	if configParserUtils.getConfigParserGet(constants.COPIAR_IMAGEN) == '1':
		for carta in spreedUtils.getCartasSinImagen():
			if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '1':
				codCarta = carta.get(constants.CODIGOJP)
			else:
				codCarta = carta.get(constants.CODIGO)
			if codCarta:
				logging.info('COPIAR_IMAGEN de {0}'.format(codCarta))
				cod = finder.buscarCodigoImagen(codCarta.replace(constants.TAG_SELLADO, ''))
				if cod:
					spreedUtils.rellenarImagen(carta.get(constants.FILA), finder.formatUrlCarta(cod))

	if configParserUtils.getConfigParserGet(constants.COPIAR_IMAGEN_CM) == '1':
		for carta in spreedUtils.getCartasCm(configParserUtils.getConfigParserGet(constants.COPIAR_IMAGEN_CM_FORZADO) == '1'):
			codCarta = carta.get(constants.CODIGO)
			if codCarta:
				logging.info('COPIAR_IMAGEN_CM de {0}'.format(codCarta))
				scan.rellenarImagenCm(codCarta, carta.get(constants.URL_PRECIO), carta.get(constants.FILA))


if __name__ == '__main__':
	try:
		frm = configParserUtils.getConfigParserGet(constants.COPIAR_FORMULA)
		datos = configParserUtils.getConfigParserGet(constants.COPIAR_DATOS_GENERALES)
		codImg = configParserUtils.getConfigParserGet(constants.COPIAR_CODIGO_IMAGEN)
		img = configParserUtils.getConfigParserGet(constants.COPIAR_IMAGEN)
		imgCm = configParserUtils.getConfigParserGet(constants.COPIAR_IMAGEN_CM)
		imgCmForzado = configParserUtils.getConfigParserGet(constants.COPIAR_IMAGEN_CM_FORZADO)
		buscador = configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR)
		if buscador == '0':
			buscador = 'EU Old'
		elif buscador == '1':
			buscador = 'JP'
		elif buscador == '2':
			buscador = 'EU'
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Rellenando datos a las {}, Formulas {}, Datos {}, Codigo img {}, Imagen {}, Imagen CM(forzado {}) {}, Buscador {}'.format(datetime.now().strftime('%H:%M'), frm, datos, codImg, img, imgCmForzado, imgCm, buscador))
		rellenarCartas()
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Fin relleno datos a las %s' % datetime.now().strftime('%H:%M'))
	except Exception as e:
		msgError = 'Error rellenado datos'
		logging.error(msgError, e)
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), msgError)
