import logging
import os
import time

import gspread
import requests

import configParserUtils
import constants

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO, handlers=[logging.FileHandler(os.path.join(os.path.abspath(os.path.dirname(__file__)), configParserUtils.getConfigParserGet(constants.LOG_FILE)), mode='w', encoding='UTF-8'), logging.StreamHandler()])
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials


def actualizarPrecios(actual, minimo, alarma, indiceFila, indices):
	hoja = getHojaPrecios()
	if actual:
		columnaActual = indices.get(constants.ACTUAL)
		logging.debug(str('Actualizando el precio actual ' + str(actual) + ' en la col ' + str(columnaActual) + ' fil ' + str(indiceFila)))
		hoja.update_cell(indiceFila, columnaActual, actual)
	if minimo:
		columnaMinima = indices.get(constants.MINIMO)
		columnaFminima = indices.get(constants.FMINIMO)
		logging.debug(str('Actualizando el precio minimo ' + str(minimo) + ' en la col ' + str(columnaMinima) + ' fil ' + str(indiceFila)))
		hoja.update_cell(indiceFila, columnaMinima, minimo)
		hoja.update_cell(indiceFila, columnaFminima, datetime.now().strftime('%d/%m/%Y %H:%M'))
	if alarma:
		columnaAlarma = indices.get(constants.ALARMA)
		logging.debug(str('Actualizando el precio alarma ' + str(alarma) + ' en la col ' + str(columnaAlarma) + ' fil ' + str(indiceFila)))
		hoja.update_cell(indiceFila, columnaAlarma, alarma)


def getListaImagenes():
	hoja = getHoja(constants.SHEET_NAME_DATOS)
	imagenes = []
	cartas = hoja.get_all_records()
	indiceFila = 2
	for carta in cartas:
		numeroCarta = carta.get(constants.CODIGO)
		urlImg = carta.get(constants.URL_IMAGEN)
		if numeroCarta and len(numeroCarta) > 0 and urlImg and len(urlImg) > 0 and urlImg != '-':
			imagenes.append({constants.CODIGO: numeroCarta, constants.URL_IMAGEN: urlImg})
		indiceFila = indiceFila + 1
	return imagenes


def getNumerosCartas(columna):
	hoja = getHoja(constants.SHEET_NAME_DATOS)
	numeros = []
	cartas = hoja.get_all_records()
	indiceFila = 2

	if columna:
		indiceColumna = columna
	else:
		indiceColumna = constants.CODIGO

	for carta in cartas:
		numeroCarta = carta.get(indiceColumna)
		if numeroCarta and len(numeroCarta) > 0:
			numeros.append(numeroCarta)
		indiceFila = indiceFila + 1
	return numeros


def getCartasSinFormulas():
	hoja = getHoja(constants.SHEET_NAME_DATOS)
	numeros = []
	cartas = hoja.get_all_records()
	indiceFila = 2
	for carta in cartas:
		codCarta = carta.get(constants.CODIGO)
		numeroCarta = carta.get(constants.NUMERO)
		if codCarta and len(codCarta) > 0 and (numeroCarta is None or numeroCarta == ''):
			numeros.append({constants.CODIGO: carta.get(constants.CODIGO), constants.FILA: indiceFila})
		indiceFila = indiceFila + 1
	return numeros


def getCartasSinDatos():
	hoja = getHoja(constants.SHEET_NAME_DATOS)
	numeros = []
	cartas = hoja.get_all_records()
	indiceFila = 2
	for carta in cartas:
		codCarta = carta.get(constants.CODIGO)
		nombreCarta = carta.get(constants.NOMBRE)
		numeroCarta = carta.get(constants.NUMERO)
		if codCarta and len(codCarta) > 0 and (nombreCarta is None or nombreCarta == '') and numeroCarta and len(numeroCarta) > 0:
			numeros.append({constants.CODIGO: carta.get(constants.CODIGO), constants.NUMERO: carta.get(constants.NUMERO), constants.FILA: indiceFila})
		indiceFila = indiceFila + 1
	return numeros


def getCartasSinCodigoEuJp(codigoBusqueda):
	hoja = getHoja(constants.SHEET_NAME_DATOS)
	numeros = []
	cartas = hoja.get_all_records()
	indiceFila = 2
	for carta in cartas:
		codCarta = carta.get(constants.CODIGO)
		numCarta = carta.get(constants.NUMERO)
		codCartaAux = carta.get(codigoBusqueda)
		if codCarta and len(codCarta) > 0 and (codCartaAux is None or codCartaAux == ''):
			numeros.append({constants.CODIGO: carta.get(constants.CODIGO), codigoBusqueda: carta.get(codigoBusqueda), constants.FILA: indiceFila, constants.NUMERO: numCarta})
		indiceFila = indiceFila + 1
	return numeros


def getCartasSinCodigoEu():
	return getCartasSinCodigoEuJp(constants.CODIGOEU);


def getCartasSinCodigoJp():
	return getCartasSinCodigoEuJp(constants.CODIGOJP);


def getCartasSinImagen():
	hoja = getHoja(constants.SHEET_NAME_DATOS)
	numeros = []
	cartas = hoja.get_all_records()
	indiceFila = 2
	for carta in cartas:
		codCarta = carta.get(constants.CODIGO)
		if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '2':
			codCarta = carta.get(constants.CODIGOEU)
		codCartaJp = carta.get(constants.CODIGOJP)
		numCarta = carta.get(constants.NUMERO)
		if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '1':
			columnaImg = constants.URL_JAPO
		else:
			columnaImg = constants.URL_IMAGEN
		urlImagen = carta.get(columnaImg)
		if codCarta and len(codCarta) > 0 and (urlImagen is None or urlImagen == ''):
			numeros.append({constants.CODIGO: codCarta, constants.FILA: indiceFila, constants.CODIGOJP: codCartaJp, constants.NUMERO: numCarta})
		indiceFila = indiceFila + 1
	return numeros


def getListaSeguimientos(forzarBusqueda):
	hoja = getHojaPrecios()
	indicesSeguimientos = []
	seguimientos = []
	indicesSeguimientos.append(getIndices(hoja))
	cartas = hoja.get_all_records()
	indiceFila = 2
	coleccionesBusquedasConf = configParserUtils.getConfigParserGet(constants.COLECCIONES_BUSQUEDAS)
	coleccionesBusquedas = []
	for col in coleccionesBusquedasConf.split(constants.SEPARADOR_CONFIG):
		coleccionesBusquedas.append(col.strip())
	for carta in cartas:
		numeroCarta = carta.get(constants.CODIGO)
		buscar = carta.get(constants.BUSCAR)
		coleccion = numeroCarta.split('-')[0]
		if len(coleccionesBusquedasConf.strip()) == 0 or coleccion in coleccionesBusquedas:
			if forzarBusqueda:
				buscar = 'TRUE'
			if buscar and buscar == 'TRUE' and numeroCarta and len(numeroCarta) > 0:
				urlPrecio = carta.get(constants.URL_PRECIO)
				if urlPrecio and len(urlPrecio) > 0:
					seguimientos.append({constants.FILA: indiceFila, constants.URL_PRECIO: urlPrecio, constants.CODIGO: carta.get(constants.CODIGO), constants.ALARMA: carta.get(constants.ALARMA), constants.ACTUAL: carta.get(constants.ACTUAL), constants.MINIMO: carta.get(constants.MINIMO), constants.NOMBRE: carta.get(constants.NOMBRE)})
		indiceFila = indiceFila + 1
	logging.info(str('Se buscarán ' + str(len(seguimientos)) + ' de las ' + str((indiceFila - 1)) + ' filas leidas en total'))
	indicesSeguimientos.append(seguimientos)
	logging.debug(indicesSeguimientos)
	return indicesSeguimientos


def getIndices(hoja):
	titulos = hoja.row_values(1)
	indicesCampos = {
		constants.ACTUAL: 0,
		constants.ALARMA: 0,
		constants.BUSCAR: 0,
		constants.CODIGO: 0,
		constants.COLOR: 0,
		constants.COMPRA: 0,
		constants.DP: 0,
		constants.EVOL: 0,
		constants.FMINIMO: 0,
		constants.MAIN_EFF: 0,
		constants.MINIMO: 0,
		constants.NOMBRE: 0,
		constants.NUMERO: 0,
		constants.PLAY: 0,
		constants.SOUR_EFF: 0,
		constants.TIPO: 0,
		constants.URL_IMAGEN: 0,
		constants.URL_JAPO: 0,
		constants.URL_PRECIO: 0,
		constants.CODIGOJP: 0,
		constants.CODIGOEU: 0
	}

	for tituloIndex in range(len(titulos)):
		titulo = titulos[tituloIndex]
		if titulo == constants.ACTUAL:
			indicesCampos[constants.ACTUAL] = tituloIndex + 1
		elif titulo == constants.ALARMA:
			indicesCampos[constants.ALARMA] = tituloIndex + 1
		elif titulo == constants.BUSCAR:
			indicesCampos[constants.BUSCAR] = tituloIndex + 1
		elif titulo == constants.CODIGO:
			indicesCampos[constants.CODIGO] = tituloIndex + 1
		elif titulo == constants.COLOR:
			indicesCampos[constants.COLOR] = tituloIndex + 1
		elif titulo == constants.COMPRA:
			indicesCampos[constants.COMPRA] = tituloIndex + 1
		elif titulo == constants.DP:
			indicesCampos[constants.DP] = tituloIndex + 1
		elif titulo == constants.EVOL:
			indicesCampos[constants.EVOL] = tituloIndex + 1
		elif titulo == constants.FMINIMO:
			indicesCampos[constants.FMINIMO] = tituloIndex + 1
		elif titulo == constants.MAIN_EFF:
			indicesCampos[constants.MAIN_EFF] = tituloIndex + 1
		elif titulo == constants.MINIMO:
			indicesCampos[constants.MINIMO] = tituloIndex + 1
		elif titulo == constants.NOMBRE:
			indicesCampos[constants.NOMBRE] = tituloIndex + 1
		elif titulo == constants.NUMERO:
			indicesCampos[constants.NUMERO] = tituloIndex + 1
		elif titulo == constants.PLAY:
			indicesCampos[constants.PLAY] = tituloIndex + 1
		elif titulo == constants.SOUR_EFF:
			indicesCampos[constants.SOUR_EFF] = tituloIndex + 1
		elif titulo == constants.TIPO:
			indicesCampos[constants.TIPO] = tituloIndex + 1
		elif titulo == constants.URL_IMAGEN:
			indicesCampos[constants.URL_IMAGEN] = tituloIndex + 1
		elif titulo == constants.URL_JAPO:
			indicesCampos[constants.URL_JAPO] = tituloIndex + 1
		elif titulo == constants.URL_PRECIO:
			indicesCampos[constants.URL_PRECIO] = tituloIndex + 1
		elif titulo == constants.CODIGOJP:
			indicesCampos[constants.CODIGOJP] = tituloIndex + 1
		elif titulo == constants.CODIGOEU:
			indicesCampos[constants.CODIGOEU] = tituloIndex + 1

	return indicesCampos


def nuevaFila(nMixCarta):
	album = getHoja(constants.SHEET_NAME_ALBUM)
	album.append_row([nMixCarta])
	preciosTrader = getHoja(constants.SHEET_NAME_PRECIOS_TRADER)
	preciosTrader.append_row([nMixCarta])
	preciosMarket = getHoja(constants.SHEET_NAME_PRECIOS_MARKET)
	preciosMarket.append_row([nMixCarta])
	preciosAux = getHoja(constants.SHEET_NAME_PRECIOS_AUX)
	preciosAux.append_row([nMixCarta])
	imgs = getHoja(constants.SHEET_NAME_IMGS)
	imgs.append_row([nMixCarta])
	datos = getHoja(constants.SHEET_NAME_DATOS)
	datos.append_row([nMixCarta])


def rellenarCodigoJp(indice, codCarta):
	rellenarCodigoEuJp(indice, constants.CODIGOJP, codCarta)


def rellenarCodigoEu(indice, codCarta):
	rellenarCodigoEuJp(indice, constants.CODIGOEU, codCarta)


def rellenarCodigoEuJp(indice, campo, codCarta):
	datos = getHoja(constants.SHEET_NAME_DATOS)
	indices = getIndices(datos)
	logging.info('Buscando y rellenando el {} con {}'.format(campo, codCarta))
	datos.update_cell(indice, indices.get(campo), codCarta)

	tiempoMinimoBusquedaSpreadsheetStr = configParserUtils.getConfigParserGet(constants.TIEMPO_MINIMO_BUSQUEDA_SPREADSHEET)
	tiempoMinimoBusquedaSpreadsheet = 30
	if len(tiempoMinimoBusquedaSpreadsheetStr) != 0:
		tiempoMinimoBusquedaSpreadsheet = int(tiempoMinimoBusquedaSpreadsheetStr)
	time.sleep(tiempoMinimoBusquedaSpreadsheet)


def rellenarDatos(indice, nCarta):
	datos = getHoja(constants.SHEET_NAME_DATOS)
	indices = getIndices(datos)
	urlApi = constants.URL_API_DATOS.format(nCarta)
	logging.info('Buscando y copiando datos de {} {}'.format(nCarta, urlApi))
	datosRecuperados = requests.get(urlApi)

	if datosRecuperados.ok:
		datosRecuperadosJson = datosRecuperados.json()
		if len(datosRecuperadosJson) == 1:
			dato = datosRecuperadosJson[0]
			nombreApi = dato['name']
			if nombreApi:
				datos.update_cell(indice, indices.get(constants.NOMBRE), nombreApi)
			colorApi = dato['color']
			if colorApi:
				if colorApi == 'Yellow':
					datos.update_cell(indice, indices.get(constants.COLOR), 'Amarillo')
				if colorApi == 'Blue':
					datos.update_cell(indice, indices.get(constants.COLOR), 'Azul')
				if colorApi == 'White':
					datos.update_cell(indice, indices.get(constants.COLOR), 'Blanco')
				if colorApi == 'Purple':
					datos.update_cell(indice, indices.get(constants.COLOR), 'Morado')
				if colorApi == 'Black':
					datos.update_cell(indice, indices.get(constants.COLOR), 'Negro')
				if colorApi == 'Red':
					datos.update_cell(indice, indices.get(constants.COLOR), 'Rojo')
				if colorApi == 'Green':
					datos.update_cell(indice, indices.get(constants.COLOR), 'Verde')

			dpApi = dato['dp']
			if dpApi:
				datos.update_cell(indice, indices.get(constants.DP), dpApi)
			playApi = dato['play_cost']
			if playApi:
				datos.update_cell(indice, indices.get(constants.PLAY), playApi)
			typeApi = dato['type']
			evolApi = dato['evolution_cost']
			if evolApi:
				datos.update_cell(indice, indices.get(constants.EVOL), evolApi)
			elif typeApi == 'Digimon':
				datos.update_cell(indice, indices.get(constants.EVOL), '0')
			levelApi = dato['level']
			if typeApi:
				if typeApi == 'Digimon':
					datos.update_cell(indice, indices.get(constants.TIPO), 'Lvl {}'.format(levelApi))
				elif typeApi == 'Digi-Egg':
					datos.update_cell(indice, indices.get(constants.TIPO), 'Lvl 2')
				else:
					datos.update_cell(indice, indices.get(constants.TIPO), typeApi)
			maineffect = dato['maineffect']
			if maineffect:
				datos.update_cell(indice, indices.get(constants.MAIN_EFF), limpiarSimbolos(maineffect))
			soureeffect = dato['soureeffect']
			if soureeffect:
				datos.update_cell(indice, indices.get(constants.SOUR_EFF), limpiarSimbolos(soureeffect))

		tiempoMinimoBusquedaSpreadsheetStr = configParserUtils.getConfigParserGet(constants.TIEMPO_MINIMO_BUSQUEDA_SPREADSHEET)
		tiempoMinimoBusquedaSpreadsheet = 30
		if len(tiempoMinimoBusquedaSpreadsheetStr) != 0:
			tiempoMinimoBusquedaSpreadsheet = int(tiempoMinimoBusquedaSpreadsheetStr)
		time.sleep(tiempoMinimoBusquedaSpreadsheet)

	time.sleep(5)


def limpiarSimbolos(txt):
	return txt.replace('&lt;', '<').replace('&gt;', '>').replace('&#91;', '[')


def rellenarImagen(indice, urlImagen):
	datos = getHoja(constants.SHEET_NAME_DATOS)
	indices = getIndices(datos)
	if configParserUtils.getConfigParserGet(constants.MODO_BUSCADOR) == '1':
		columnaImg = constants.URL_JAPO
	else:
		columnaImg = constants.URL_IMAGEN
	datos.update_cell(indice, indices.get(columnaImg), urlImagen)

	tiempoMinimoBusquedaSpreadsheetStr = configParserUtils.getConfigParserGet(constants.TIEMPO_MINIMO_BUSQUEDA_SPREADSHEET)
	tiempoMinimoBusquedaSpreadsheet = 30
	if len(tiempoMinimoBusquedaSpreadsheetStr) != 0:
		tiempoMinimoBusquedaSpreadsheet = int(tiempoMinimoBusquedaSpreadsheetStr)
	time.sleep(tiempoMinimoBusquedaSpreadsheet)


def rellenarFormula(indice):
	datos = getHoja(constants.SHEET_NAME_DATOS)

	tiempoMinimoBusquedaSpreadsheetStr = configParserUtils.getConfigParserGet(constants.TIEMPO_MINIMO_BUSQUEDA_SPREADSHEET)
	tiempoMinimoBusquedaSpreadsheet = 30
	if len(tiempoMinimoBusquedaSpreadsheetStr) != 0:
		tiempoMinimoBusquedaSpreadsheet = int(tiempoMinimoBusquedaSpreadsheetStr)

	time.sleep(tiempoMinimoBusquedaSpreadsheet)

	datos.update(str('D' + str(indice)), constants.FRM_DA_D.format(indice, indice), raw=False)
	datos.update(str('E' + str(indice)), constants.FRM_DA_E.format(indice, indice, indice), raw=False)
	datos.update(str('P' + str(indice)), constants.FRM_DA_P.format(indice), raw=False)
	datos.update(str('Q' + str(indice)), constants.FRM_DA_Q.format(indice), raw=False)

	time.sleep(tiempoMinimoBusquedaSpreadsheet)


def getHoja(sheet):
	scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'client_secret.json'), scope)
	client = gspread.authorize(creds)
	logging.info(str('Buscando ' + sheet + ' en ' + configParserUtils.getConfigParserGet(constants.WORKBOOK_NAME)))
	return client.open(configParserUtils.getConfigParserGet(constants.WORKBOOK_NAME)).worksheet(sheet)


def getHojaPrecios():
	if configParserUtils.getConfigParserGet(constants.MODO_ESCANEO) == '0':
		hoja = getHoja(constants.SHEET_NAME_PRECIOS_TRADER)
	elif configParserUtils.getConfigParserGet(constants.MODO_ESCANEO) == '1':
		hoja = getHoja(constants.SHEET_NAME_PRECIOS_MARKET)
	else:
		logging.error('No se ha definido modo de escaneo')
		raise Exception('No se ha definido modo de escaneo')
	return hoja
