import asyncio
import logging
import os
import time

import configParserUtils
import constants
import finder
import imgDownloader
import spreedUtils
import telegramUtils

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO, handlers=[logging.FileHandler(os.path.join(os.path.abspath(os.path.dirname(__file__)), configParserUtils.getConfigParserGet(constants.LOG_FILE)), mode='w', encoding='UTF-8'), logging.StreamHandler()])
from pyppeteer import launch
from pyppeteer.errors import ElementHandleError
from datetime import datetime
from os.path import exists

listaErroresBestDeal = []
listaSinPrecio = []


async def busqueda(seguimiento, indices, webBusqueda):
	chromium = configParserUtils.getConfigParserGet(constants.CHROMIUM)
	entornoDocker = configParserUtils.getConfigParserGet(constants.ENTORNO_DOCKER)
	browser = None
	page = None
	precioEncontrado = 0
	url = None

	try:
		if chromium and len(chromium) > 0:
			if entornoDocker and entornoDocker == 'True':
				browser = await launch(logLevel=logging.WARN, executablePath=chromium, args=['--disable-dev-shm-usage', '--disable-gpu', '--single-process', '--no-zygote', '--no-sandbox'])
			else:
				browser = await launch(logLevel=logging.WARN, executablePath=chromium)
		else:
			if entornoDocker and entornoDocker == 'True':
				browser = await launch(logLevel=logging.WARN, args=['--disable-dev-shm-usage', '--disable-gpu', '--single-process', '--no-zygote', '--no-sandbox'])
			else:
				browser = await launch(logLevel=logging.WARN)

		page = await browser.newPage()
		if page:
			url = seguimiento.get(constants.URL_PRECIO)
			codigo = seguimiento.get(constants.CODIGO)
			await page.setViewport(dict(width=1200, height=2000))
			await page.goto(url, timeout=20000)
			try:
				if configParserUtils.getConfigParserGet(constants.MODO_ESCANEO) == '0':
					precio = await page.Jeval('.best-deal', 'node => node.innerText')
					await page.J('.min products-table__price products-table__separator--left')
				elif configParserUtils.getConfigParserGet(constants.MODO_ESCANEO) == '1':
					sinPrecio = False
					try:
						sinPrecio = await page.Jeval('div.table-body > div.text-center > p.noResults', 'node => node.innerText')
					except ElementHandleError as e:
						logging.debug('Error o precio encontrado', e)
					if sinPrecio:
						precio = '-'
					else:
						precio = await page.Jeval('div.col-offer > div.price-container.d-none.d-md-flex.justify-content-end > div > div > span', 'node => node.innerText')
				else:
					logging.error('No se ha definido modo de escaneo')
					raise Exception('No se ha definido modo de escaneo')

				alarma = seguimiento.get(constants.ALARMA)
				nombre = seguimiento.get(constants.NOMBRE)
				if precio != '-':
					nombrePrecioParam = None
					nombreImgParam = None
					if configParserUtils.getConfigParserGet(constants.MODO_ESCANEO) == '0':
						precio = getFloatUS(precio)
						nombreImgParam = dict(x=39, y=290, width=250, height=350)
						nombrePrecioParam = dict(x=305, y=1010, width=600, height=405)
					elif configParserUtils.getConfigParserGet(constants.MODO_ESCANEO) == '1':
						precio = getFloatES(precio)
						nombreImgParam = dict(x=64, y=515, width=240, height=334)
						nombrePrecioParam = dict(x=105, y=886, width=1050, height=405)
					if alarma and getFloatES(alarma) >= precio:
						telegramMensaje = str('He encontrado un ' + nombre + '(' + codigo + ') en ' + webBusqueda + ' a ' + getFloatToEuro(precio) + '\n' + url)
						logging.info(str('La carta ' + nombre + '(' + codigo + ') con alarma por ' + alarma + ' está por ' + getFloatToEuro(precio)))
						nombreImgFoto = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'img', str('img_' + codigo + '.png'))
						eliminarImgCarta = False
						if not exists(nombreImgFoto):
							await page.screenshot({'path': nombreImgFoto, 'clip': nombreImgParam})
							eliminarImgCarta = True
						nombrePrecioFoto = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'img', str('prc_' + codigo + '.png'))
						await page.screenshot({'path': nombrePrecioFoto, 'clip': nombrePrecioParam})
						telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_CHAT_CANAL_CHOLLOS_ID), telegramMensaje, nombreImgFoto, nombrePrecioFoto)
						os.remove(nombrePrecioFoto)
						if eliminarImgCarta:
							os.remove(nombreImgFoto)
					else:
						logging.info(str('La carta ' + codigo + ' está por ' + getFloatToEuro(precio)))
					precioEncontrado = precio
				else:
					logging.info(str('La carta ' + codigo + ' no está a la venta'))
					listaSinPrecio.append(str(codigo + ' (Sin precio) ' + url))
			except ElementHandleError as e:
				listaErroresBestDeal.append(str(codigo + ' (ElementHandleError) ' + url))
				logging.error('Error leyendo el precio (ElementHandleError) %s' % url)
				logging.debug(e)
			except Exception as e:
				logging.error('Error leyendo el precio %s' % url, exc_info=e)
	except Exception as e:
		logging.error('Error accediendo a la web buscando el precio %s' % url, exc_info=e)
	finally:
		if page:
			await page.close()
		if browser:
			await browser.close()
		if precioEncontrado > 0:
			logging.debug(str('Actualizando el precio ' + str(precioEncontrado)))
			actual = None
			minimo = None
			alarma = None
			actualizar = False
			if seguimiento.get(constants.ACTUAL) == '' or precioEncontrado != getFloatES(seguimiento.get(constants.ACTUAL)):
				actual = precioEncontrado
				actualizar = True
			if seguimiento.get(constants.MINIMO) == '' or precioEncontrado < getFloatES(seguimiento.get(constants.MINIMO)):
				minimo = precioEncontrado
				actualizar = True
			if seguimiento.get(constants.ALARMA) != '' and precioEncontrado <= getFloatES(seguimiento.get(constants.ALARMA)):
				alarma = precioEncontrado - 0.01
				actualizar = True
				mensaje = str('Se actualiza la alarma ' + seguimiento.get(constants.ALARMA) + ' de ' + seguimiento.get(constants.NOMBRE) + '(' + seguimiento.get(constants.CODIGO) + ') a ' + getFloatToEuro(alarma))
				telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_CHAT_CANAL_CHOLLOS_ID), mensaje)
			if actualizar:
				spreedUtils.actualizarPrecios(actual, minimo, alarma, seguimiento.get(constants.FILA), indices)


def getFloatES(num):
	numFl = float(num.replace('.', '').replace(',', '.').replace('€', '').replace(' ', ''))
	return round(numFl, 2)


def getFloatUS(num):
	numFl = float(num.replace(',', '').replace('€', '').replace(' ', ''))
	return round(numFl, 2)


def getFloatToEuro(num):
	return str(str(round(num, 2)).replace(',', '_').replace('.', ',').replace('_', '.').replace(' ', '') + '€')


def main():
	telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'El bot ha iniciado su ejecución a las %s' % datetime.now().strftime('%H:%M'))
	bucleInfinito = True
	bucleInfinitoParam = configParserUtils.getConfigParserGet(constants.BUCLE_INFINITO)
	coleccionesBusquedas = configParserUtils.getConfigParserGet(constants.COLECCIONES_BUSQUEDAS)
	tiempoMinimoBusquedaStr = configParserUtils.getConfigParserGet(constants.TIEMPO_MINIMO_BUSQUEDA)
	tiempoMinimoBusqueda = 8
	if len(tiempoMinimoBusquedaStr) != 0:
		tiempoMinimoBusqueda = int(tiempoMinimoBusquedaStr)

	while bucleInfinito:
		if bucleInfinitoParam == 'False':
			bucleInfinito = False

		buscarCartasNuevas = configParserUtils.getConfigParserGet(constants.BUSCAR_CARTAS_NUEVAS)
		if buscarCartasNuevas and buscarCartasNuevas == 'True':
			logging.info('------------------------------------------------------------')
			logging.info('Inicio busqueda de cartas nuevas')
			logging.info('------------------------------------------------------------')

			telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Buscando cartas nuevas')
			finder.buscarCartasNuevas()

			logging.info('------------------------------------------------------------')
			logging.info('Fin busqueda de cartas nuevas')

		descargarImagenes = configParserUtils.getConfigParserGet(constants.DESCARGAR_IMAGENES)
		if descargarImagenes and descargarImagenes == 'True':
			logging.info('------------------------------------------------------------')
			logging.info('Inicio descarga imagenes')
			logging.info('------------------------------------------------------------')

			telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Buscando imagenes')
			imgDownloader.descargarImgs()

			logging.info('------------------------------------------------------------')
			logging.info('Fin descarga imagenes')

		logging.info('------------------------------------------------------------')
		logging.info('Inicio listado')
		if len(coleccionesBusquedas) != 0:
			logging.info(coleccionesBusquedas)
		logging.info('------------------------------------------------------------')

		vueltas = 0
		cantidadBusquedas = int(configParserUtils.getConfigParserGet(constants.CANTIDAD_BUSQUEDAS))
		while vueltas < cantidadBusquedas:
			listaErroresBestDeal.clear()
			listaSinPrecio.clear()
			if len(coleccionesBusquedas) != 0:
				telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Obteniendo/Refrescando seguimientos.... ' + coleccionesBusquedas)
			else:
				telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Obteniendo/Refrescando seguimientos....')

			forzarPrimeraBusqueda = False
			forzarPrimeraBusquedaConf = configParserUtils.getConfigParserGet(constants.FORZAR_PRIMERA_BUSQUEDA)
			if vueltas == 0:
				if forzarPrimeraBusquedaConf and forzarPrimeraBusquedaConf == 'True':
					forzarPrimeraBusqueda = True

			indicesSeguimientos = spreedUtils.getListaSeguimientos(forzarPrimeraBusqueda)
			if configParserUtils.getConfigParserGet(constants.MODO_ESCANEO) == '0':
				webBusqueda = constants.WEB_TRADER
			elif configParserUtils.getConfigParserGet(constants.MODO_ESCANEO) == '1':
				webBusqueda = constants.WEB_MARKET
			else:
				logging.error('No se ha definido modo de escaneo')
				raise Exception('No se ha definido modo de escaneo')

			mensajeEscaneo = str('Escaneando listado(' + str(len(indicesSeguimientos[1])))
			if len(coleccionesBusquedas) != 0:
				mensajeEscaneo = mensajeEscaneo + str(' cartas de ' + coleccionesBusquedas)
			mensajeEscaneo = mensajeEscaneo + str(') en ' + webBusqueda + ' a las ' + datetime.now().strftime('%H:%M'))
			telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), mensajeEscaneo)
			logging.info(mensajeEscaneo)
			for seg in indicesSeguimientos[1]:
				try:
					antesEnvio = datetime.now()
					if len(seg) > 2 and seg.get(constants.ALARMA):
						logging.info(str('Buscando la carta ' + seg.get(constants.NOMBRE) + '(' + seg.get(constants.CODIGO) + ') en ' + webBusqueda + ' con alarma por ' + str(seg.get(constants.ALARMA)).replace(' ', '')))
					else:
						logging.info(str('Buscando la carta ' + seg.get(constants.NOMBRE) + '(' + seg.get(constants.CODIGO) + ') en ' + webBusqueda))
					asyncio.get_event_loop().run_until_complete(asyncio.wait_for(busqueda(seg, indicesSeguimientos[0], webBusqueda), timeout=30.0))
					despuessEnvio = datetime.now()
					tiempoEnvio = despuessEnvio - antesEnvio
					if tiempoEnvio.total_seconds() < tiempoMinimoBusqueda:
						time.sleep(tiempoMinimoBusqueda - tiempoEnvio.total_seconds())
				except Exception as e:
					logging.error('Error al buscar precio en %s' % seg.get(constants.URL_PRECIO), exc_info=e)

			textoErroresBestDeal = 'No se ha encontrado mejor oferta en las cartas: '
			if len(listaErroresBestDeal) > 0:
				for errorBestDeal in listaErroresBestDeal:
					textoErroresBestDeal = str(textoErroresBestDeal + '\n\t' + errorBestDeal)
				logging.info(textoErroresBestDeal)
				rutaFicheroErroresBestDeal = os.path.join(os.path.abspath(os.path.dirname(__file__)), str('ErroresBestDeal.txt'))
				ficheroErroresBestDeal = open(rutaFicheroErroresBestDeal, 'w')
				ficheroErroresBestDeal.write(textoErroresBestDeal)
				ficheroErroresBestDeal.close()
				telegramUtils.enviarFicheroTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), rutaFicheroErroresBestDeal)
				os.remove(rutaFicheroErroresBestDeal)

			enviarSinPrecio = configParserUtils.getConfigParserGet(constants.ENVIAR_SIN_PRECIO)
			if enviarSinPrecio and enviarSinPrecio == 'True':
				textoSinPrecio = 'No se ha encontrado precio en las cartas: '
				if len(listaSinPrecio) > 0:
					for sinPrecio in listaSinPrecio:
						textoSinPrecio = str(textoSinPrecio + '\n\t' + sinPrecio)
					logging.info(textoSinPrecio)
					rutaFicheroSinPrecio = os.path.join(os.path.abspath(os.path.dirname(__file__)), str('SinPrecio.txt'))
					ficheroSinPrecio = open(rutaFicheroSinPrecio, 'w')
					ficheroSinPrecio.write(textoSinPrecio)
					ficheroSinPrecio.close()
					telegramUtils.enviarFicheroTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), rutaFicheroSinPrecio)
					os.remove(rutaFicheroSinPrecio)

			msgFinScan = 'Fin de escaneado'
			if len(coleccionesBusquedas) != 0:
				msgFinScan = msgFinScan + str('(' + coleccionesBusquedas + ')')
			msgFinScan = msgFinScan + str(' en ' + webBusqueda + ' a las %s' % datetime.now().strftime('%H:%M'))
			telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), msgFinScan)
			vueltas = vueltas + 1

	telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'El bot ha terminado su ejecución a las %s' % datetime.now().strftime('%H:%M'))
	logging.info('------------------------------------------------------------')
	logging.info('Fin listado')
	if len(coleccionesBusquedas) != 0:
		logging.info(coleccionesBusquedas)
	logging.info('------------------------------------------------------------')


if __name__ == '__main__':
	main()
