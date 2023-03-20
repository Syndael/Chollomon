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


def buscarCodigoImagen(codigoCod):
	logging.info('Buscando imagen de la carta {0}'.format(codigoCod))
	formateoConst = constants.FORMATEO_1
	rutaImg = descargarImg(codigoCod, formateoConst)
	alterIndex = 0
	if '_P1' in codigoCod:
		alterIndex = 1

	codigoCodRes = formateoConst.format(codigoCod)

	if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '2':
		if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
			formateoConst = constants.FORMATEO_2
			if alterIndex == 1:
				rutaImg = descargarImg(codigoCod.replace('_P1', 'P'), formateoConst)
				codigoCodRes = formateoConst.format(codigoCod.replace('_P1', 'P'))
			else:
				rutaImg = descargarImg(codigoCod, formateoConst)
				codigoCodRes = formateoConst.format(codigoCod)
		if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
			formateoConst = constants.FORMATEO_3
			rutaImg = descargarImg(codigoCod, formateoConst)
			codigoCodRes = formateoConst.format(codigoCod)
		if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
			formateoConst = constants.FORMATEO_4
			if alterIndex == 1:
				formateoConst = constants.FORMATEO_4_P1
				rutaImg = descargarImg(codigoCod.replace('_P1', ''), formateoConst)
				codigoCodRes = formateoConst.format(codigoCod.replace('_P1', ''))
			else:
				rutaImg = descargarImg(codigoCod.replace('_P', 'p'), formateoConst)
				codigoCodRes = formateoConst.format(codigoCod.replace('_P', 'p'))
		if os.path.getsize(rutaImg) < constants.TAMANHO_MIN_IMG:
			formateoConst = constants.FORMATEO_5
			if alterIndex == 1:
				formateoConst = constants.FORMATEO_5_P1
				rutaImg = descargarImg(codigoCod.replace('_P1', ''), formateoConst)
				codigoCodRes = formateoConst.format(codigoCod.replace('_P1', ''))
			else:
				rutaImg = descargarImg(codigoCod.replace('_P', 'P'), formateoConst)
				codigoCodRes = formateoConst.format(codigoCod.replace('_P', 'P'))

	if os.path.getsize(rutaImg) > constants.TAMANHO_MIN_IMG:
		try:
			return codigoCodRes
		except Exception as e2:
			msgError2 = 'Error rellenado la imagen {0}'.format(codigoCodRes)
			logging.error(msgError2, e2)
			telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), msgError2)
	return None


def buscarCartas(prefijo, cantidad, formateo, cartasMix):
	cartaIndex = 1
	excepciones = ['EX2-002']

	coleccionesBusquedas = configParserUtils.getConfigParserGet(constants.COLECCIONES_BUSQUEDAS)
	while cartaIndex <= cantidad and (coleccionesBusquedas == '' or coleccionesBusquedas == prefijo):
		try:
			numCarta = str(prefijo + constants.SEPARADOR_TEMP + formateo.format(cartaIndex))
			if numCarta not in cartasMix:
				logging.info('Buscando {}'.format(numCarta))
				numCartaEncontrado = buscarCodigoImagen(numCarta)
				if numCartaEncontrado:
					addCarta(numCarta, numCartaEncontrado)
					descargarAlter(cartasMix, numCarta)
				else:
					if cartaIndex == 1:
						logging.info('No encontrado {} fin de colecciones'.format(numCarta))
						return True
					elif numCarta not in excepciones:
						logging.info('No encontrado {} fin de temporada'.format(numCarta))
						return False
			else:
				logging.info('Buscando alter {}'.format(numCarta))
				descargarAlter(cartasMix, numCarta)
		except Exception as ex:
			logging.error('Error buscando la carta {}'.format(str(prefijo + constants.SEPARADOR_TEMP + formateo.format(cartaIndex))), ex)
		cartaIndex = cartaIndex + 1
	return coleccionesBusquedas == '' or coleccionesBusquedas == prefijo or (prefijo != constants.PRE_TEMP_P and getIntColeccion(coleccionesBusquedas) < getIntColeccion(prefijo))


def getIntColeccion(colec):
	return int(colec.replace(constants.PRE_TEMP_BT, '').replace(constants.PRE_TEMP_P, '').replace(constants.PRE_TEMP_ST, '').replace(constants.PRE_TEMP_EX, ''))


def descargarAlter(cartasMix, numCarta):
	alterIndex = 1
	finAlter = False
	while not finAlter:
		numCartaAlter = str(numCarta + constants.PRE_ALTER + str(alterIndex))
		if numCartaAlter not in cartasMix:
			numCartaAlterEncontrado = buscarCodigoImagen(numCartaAlter)
			if numCartaAlterEncontrado:
				addCarta(numCartaAlter, numCartaAlterEncontrado)
			else:
				logging.info(str('No encontrado ' + numCartaAlter + ' fin de búsqueda de ' + numCarta))
				finAlter = True

		alterIndex = alterIndex + 1


def addCarta(numCarta, numCartaEncontrada):
	logging.info('Añadiendo {}'.format(numCarta))
	spreedUtils.nuevaFila(numCarta)

	urlImg = formatUrlCarta(numCartaEncontrada)
	imgDownloader.descargarImg(constants.FORMATEO_IMG.format(numCarta), urlImg)
	listaCNNum.append({constants.CODIGO: numCarta, constants.URL_IMAGEN: urlImg})


def formatUrlCarta(numCarta):
	if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '0':
		return str(constants.URL_TEMPLATE_GLOBAL + numCarta + constants.URLS_IMG_FORMAT)
	elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '1':
		return str(constants.URL_TEMPLATE_JP + numCarta + constants.URLS_IMG_FORMAT)
	elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '2':
		coleccion = numCarta.split('-')[0].replace('e_', '')
		return str(constants.URL_TEMPLATE_GLOBAL_20220811 + coleccion + '/' + numCarta + constants.URLS_IMG_FORMAT)
	else:
		logging.error('No se ha definido modo de busqueda')
		raise Exception('No se ha definido modo de busqueda')


def descargarImg(numCarta, formateo):
	urlImg = formatUrlCarta(formateo.format(numCarta))
	return imgDownloader.descargarImg('tmpFinder.png', urlImg)


def buscarCartasNuevas():
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
				if temporada == 'ST11':
					ultimaTemporada = False
				temporadaIndex = temporadaIndex + 1
				enviarTelegram()
		elif not categoria.get(constants.TEMPORADA):
			buscarCartas(categoria.get(constants.PREFIJO), categoria.get(constants.CANTIDAD), categoria.get(constants.FORMAT), cartasMix)
			enviarTelegram()


def enviarTelegram():
	if configParserUtils.getConfigParserGet(constants.FINDER_TELE) == '0':
		if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '0':
			textoExtra = '(Global)'
		elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '1':
			textoExtra = '(Japón)'
		elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '2':
			textoExtra = '(Global B+)'
		else:
			logging.error('No se ha definido modo de busqueda')
			raise Exception('No se ha definido modo de busqueda')

		enviarMensaje(textoExtra, listaCNNum)

	listaCNNum.clear()


def notificarCartas():
	if configParserUtils.getConfigParserGet(constants.FINDER_TELE) == '1':
		spreedUtils.marcarNotificada(0, enviarMensaje('(Global)', spreedUtils.getCartasNotificadasEuOld()))
		spreedUtils.marcarNotificada(1, enviarMensaje('(Japón)', spreedUtils.getCartasNotificadasJp()))
		spreedUtils.marcarNotificada(0, enviarMensaje('(Global B+)', spreedUtils.getCartasNotificadasEu()))
		spreedUtils.marcarNotificada(0, enviarMensaje('(Manual)', spreedUtils.getCartasNotificadasOtros()))


def enviarMensaje(textoExtra, listaCartas):
	tiempoMinimoBusquedaTelegramStr = configParserUtils.getConfigParserGet(constants.TIEMPO_MINIMO_BUSQUEDA_TELEGRAM)
	tiempoMinimoBusquedaTelegram = 3
	if len(tiempoMinimoBusquedaTelegramStr) != 0:
		tiempoMinimoBusquedaTelegram = int(tiempoMinimoBusquedaTelegramStr)

	cartasNotificadas = []
	for carta in listaCartas:
		try:
			numCarta = carta.get(constants.CODIGO)
			nombreImg = str(constants.FORMATEO_IMG.format(numCarta))
			rutaImg = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'img', nombreImg)
			imgDownloader.descargarImg(nombreImg, carta.get(constants.URL_IMAGEN), rutaImg)
			telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_CHAT_CANAL_CARTAS_ID), str('Nueva carta añadida ' + numCarta + ' ' + textoExtra + ' ' + carta.get(constants.URL_IMAGEN)), rutaImg)
			time.sleep(tiempoMinimoBusquedaTelegram)
			cartasNotificadas.append(carta)
		except Exception as exc:
			logging.error('Error notificando la carta {}'.format(carta.get(constants.CODIGO)), exc)

	return cartasNotificadas


if __name__ == '__main__':
	try:
		buscador = configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR)
		notificador = configParserUtils.getConfigParserGet(constants.FINDER_TELE)

		if buscador == '0':
			buscador = 'EU Old'
		elif buscador == '1':
			buscador = 'JP'
		elif buscador == '2':
			buscador = 'EU'

		if notificador == '0':
			notificador = 'Original'
		elif notificador == '1':
			notificador = 'SI'
		elif notificador == '2':
			notificador = 'NO'

		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Buscando cartas nuevas a las {}, Buscador {}, Notificar {}'.format(datetime.now().strftime('%H:%M'), buscador, notificador))
		if configParserUtils.getConfigParserGet(constants.FINDER_TELE) != '1':
			buscarCartasNuevas()
		filler.rellenarCartas()
		if configParserUtils.getConfigParserGet(constants.FINDER_TELE) == '1':
			notificarCartas()
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Fin búsqueda de cartas nuevas a las %s' % datetime.now().strftime('%H:%M'))
	except Exception as e:
		msgError = 'Error buscando cartas'
		if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '0':
			msgError = str(msgError + '(Global)')
		elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '1':
			msgError = str(msgError + '(Japón)')
		elif configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '2':
			msgError = str(msgError + '(Global B+)')
		else:
			logging.error('No se ha definido modo de búsqueda')
		logging.error(msgError, e)
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), msgError)
