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
		logging.debug(str("Actualizando el precio actual " + str(actual) + " en la col " + str(columnaActual) + " fil " + str(indiceFila)))
		hoja.update_cell(indiceFila, columnaActual, actual)
	if minimo:
		columnaMinima = indices.get(constants.MINIMO)
		columnaFminima = indices.get(constants.FMINIMO)
		logging.debug(str("Actualizando el precio minimo " + str(minimo) + " en la col " + str(columnaMinima) + " fil " + str(indiceFila)))
		hoja.update_cell(indiceFila, columnaMinima, minimo)
		hoja.update_cell(indiceFila, columnaFminima, datetime.now().strftime("%d/%m/%Y %H:%M"))
	if alarma:
		columnaAlarma = indices.get(constants.ALARMA)
		logging.debug(str("Actualizando el precio alarma " + str(alarma) + " en la col " + str(columnaAlarma) + " fil " + str(indiceFila)))
		hoja.update_cell(indiceFila, columnaAlarma, alarma)


def getListaImagenes():
	hoja = getHoja(constants.SHEET_NAME_ALBUM)
	imagenes = []
	cartas = hoja.get_all_records()
	indiceFila = 2
	for carta in cartas:
		numeroCarta = carta.get(constants.CODIGO)
		urlImg = carta.get(constants.URL_IMAGEN)
		if numeroCarta and len(numeroCarta) > 0 and urlImg and len(urlImg) > 0:
			imagenes.append({constants.CODIGO: numeroCarta, constants.URL_IMAGEN: urlImg})
		indiceFila = indiceFila + 1
	return imagenes


def getNumerosCartas():
	hoja = getHoja(constants.SHEET_NAME_ALBUM)
	numeros = []
	cartas = hoja.get_all_records()
	indiceFila = 2
	for carta in cartas:
		numeroCarta = carta.get(constants.CODIGO)
		if numeroCarta and len(numeroCarta) > 0:
			numeros.append(numeroCarta)
		indiceFila = indiceFila + 1
	return numeros


def getNumerosMixCartas():
	hoja = getHoja(constants.SHEET_NAME_ALBUM)
	numeros = []
	cartas = hoja.get_all_records()
	indiceFila = 2
	for carta in cartas:
		numeroCarta = carta.get(constants.CODIGO)
		if numeroCarta and len(numeroCarta) > 0:
			numeros.append(numeroCarta)
		indiceFila = indiceFila + 1
	return numeros


def getCartasSinFormulas():
	hoja = getHoja(constants.SHEET_NAME_ALBUM)
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


def getCartasSinImagen():
	hoja = getHoja(constants.SHEET_NAME_DATOS)
	numeros = []
	cartas = hoja.get_all_records()
	indiceFila = 2
	for carta in cartas:
		codCarta = carta.get(constants.CODIGO)
		urlImagen = carta.get(constants.URL_IMAGEN)
		if codCarta and len(codCarta) > 0 and (urlImagen is None or urlImagen == ''):
			numeros.append({constants.CODIGO: carta.get(constants.CODIGO), constants.FILA: indiceFila})
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
		coleccion = numeroCarta.split("-")[0]
		if len(coleccionesBusquedasConf.strip()) == 0 or coleccion in coleccionesBusquedas:
			if forzarBusqueda:
				buscar = "TRUE"
			if buscar and buscar == "TRUE" and numeroCarta and len(numeroCarta) > 0:
				urlPrecio = carta.get(constants.URL_PRECIO)
				if urlPrecio and len(urlPrecio) > 0:
					seguimientos.append({constants.FILA: indiceFila, constants.URL_PRECIO: urlPrecio, constants.CODIGO: carta.get(constants.CODIGO), constants.ALARMA: carta.get(constants.ALARMA), constants.ACTUAL: carta.get(constants.ACTUAL), constants.MINIMO: carta.get(constants.MINIMO), constants.NOMBRE: carta.get(constants.NOMBRE)})
		indiceFila = indiceFila + 1
	logging.info(str("Se buscarán " + str(len(seguimientos)) + " de las " + str((indiceFila - 1)) + " filas leidas en total"))
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
		constants.URL_PRECIO: 0
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
	return txt.replace("&lt;", "<").replace("&gt;", ">").replace("&#91;", "[")


def rellenarImagen(indice, urlImagen):
	datos = getHoja(constants.SHEET_NAME_DATOS)
	indices = getIndices(datos)
	datos.update_cell(indice, indices.get(constants.URL_IMAGEN), urlImagen)

	tiempoMinimoBusquedaSpreadsheetStr = configParserUtils.getConfigParserGet(constants.TIEMPO_MINIMO_BUSQUEDA_SPREADSHEET)
	tiempoMinimoBusquedaSpreadsheet = 30
	if len(tiempoMinimoBusquedaSpreadsheetStr) != 0:
		tiempoMinimoBusquedaSpreadsheet = int(tiempoMinimoBusquedaSpreadsheetStr)
	time.sleep(tiempoMinimoBusquedaSpreadsheet)


def rellenarFormula(indice):
	album = getHoja(constants.SHEET_NAME_ALBUM)
	datos = getHoja(constants.SHEET_NAME_DATOS)
	preciosMarket = getHoja(constants.SHEET_NAME_PRECIOS_MARKET)
	preciosTrader = getHoja(constants.SHEET_NAME_PRECIOS_TRADER)
	imgs = getHoja(constants.SHEET_NAME_IMGS)

	tiempoMinimoBusquedaSpreadsheetStr = configParserUtils.getConfigParserGet(constants.TIEMPO_MINIMO_BUSQUEDA_SPREADSHEET)
	tiempoMinimoBusquedaSpreadsheet = 30
	if len(tiempoMinimoBusquedaSpreadsheetStr) != 0:
		tiempoMinimoBusquedaSpreadsheet = int(tiempoMinimoBusquedaSpreadsheetStr)

	time.sleep(tiempoMinimoBusquedaSpreadsheet)

	album.update(str('B' + str(indice)), constants.FRM_AL_B.format(indice), raw=False)
	album.update(str('H' + str(indice)), constants.FRM_AL_H.format(indice, indice), raw=False)
	album.update(str('I' + str(indice)), constants.FRM_AL_I.format(indice), raw=False)
	album.update(str('K' + str(indice)), constants.FRM_AL_K.format(indice), raw=False)
	album.update(str('L' + str(indice)), constants.FRM_AL_L.format(indice), raw=False)
	album.update(str('M' + str(indice)), constants.FRM_AL_M.format(indice), raw=False)
	album.update(str('N' + str(indice)), constants.FRM_AL_N.format(indice), raw=False)
	album.update(str('O' + str(indice)), constants.FRM_AL_O.format(indice), raw=False)
	album.update(str('P' + str(indice)), constants.FRM_AL_P.format(indice), raw=False)
	album.update(str('V' + str(indice)), constants.FRM_AL_V.format(indice, indice), raw=False)
	album.update(str('Y' + str(indice)), constants.FRM_AL_Y.format(indice, indice, indice), raw=False)
	album.update(str('Z' + str(indice)), constants.FRM_AL_Z.format(indice), raw=False)
	album.update(str('AA' + str(indice)), constants.FRM_AL_AA.format(indice), raw=False)
	album.update(str('AB' + str(indice)), constants.FRM_AL_AB.format(indice), raw=False)
	album.update(str('AC' + str(indice)), constants.FRM_AL_AC.format(indice), raw=False)
	album.update(str('AD' + str(indice)), constants.FRM_AL_AD.format(indice), raw=False)
	album.update(str('AE' + str(indice)), constants.FRM_AL_AE.format(indice, indice, indice, indice, indice, indice, indice, indice), raw=False)

	datos.update(str('B' + str(indice)), constants.FRM_DA_B.format(indice), raw=False)
	datos.update(str('C' + str(indice)), constants.FRM_DA_C.format(indice, indice, indice, indice, indice, indice), raw=False)

	time.sleep(tiempoMinimoBusquedaSpreadsheet)

	preciosMarket.update(str('B' + str(indice)), constants.FRM_PMTI_B.format(indice), raw=False)
	preciosMarket.update(str('C' + str(indice)), constants.FRM_PMT_C.format(indice, indice, indice, indice, indice), raw=False)
	preciosMarket.update(str('D' + str(indice)), constants.FRM_PMT_D.format(indice), raw=False)
	preciosMarket.update(str('E' + str(indice)), constants.FRM_PMT_E.format(indice), raw=False)
	preciosMarket.update(str('J' + str(indice)), constants.FRM_PM_J.format(indice), raw=False)
	preciosMarket.update(str('K' + str(indice)), constants.FRM_PMT_K.format(indice), raw=False)

	preciosTrader.update(str('B' + str(indice)), constants.FRM_PMTI_B.format(indice), raw=False)
	preciosTrader.update(str('C' + str(indice)), constants.FRM_PMT_C.format(indice, indice, indice, indice, indice), raw=False)
	preciosTrader.update(str('D' + str(indice)), constants.FRM_PMT_D.format(indice), raw=False)
	preciosTrader.update(str('E' + str(indice)), constants.FRM_PMT_E.format(indice), raw=False)
	preciosTrader.update(str('J' + str(indice)), constants.FRM_PT_J.format(indice), raw=False)
	preciosTrader.update(str('K' + str(indice)), constants.FRM_PMT_K.format(indice), raw=False)

	imgs.update(str('B' + str(indice)), constants.FRM_IM_B.format(indice), raw=False)
	imgs.update(str('C' + str(indice)), constants.FRM_PMTI_B.format(indice), raw=False)
	imgs.update(str('D' + str(indice)), constants.FRM_IM_D.format(indice), raw=False)
	imgs.update(str('E' + str(indice)), constants.FRM_IM_E.format(indice), raw=False)
	imgs.update(str('F' + str(indice)), constants.FRM_IM_F.format(indice), raw=False)
	imgs.update(str('G' + str(indice)), constants.FRM_IM_G.format(indice), raw=False)
	imgs.update(str('H' + str(indice)), constants.FRM_IM_H.format(indice), raw=False)
	imgs.update(str('I' + str(indice)), constants.FRM_IM_I.format(indice), raw=False)
	imgs.update(str('J' + str(indice)), constants.FRM_IM_J.format(indice), raw=False)
	imgs.update(str('K' + str(indice)), constants.FRM_IM_K.format(indice), raw=False)
	imgs.update(str('M' + str(indice)), constants.FRM_IM_M.format(indice), raw=False)

	time.sleep(tiempoMinimoBusquedaSpreadsheet)


def getHoja(sheet):
	scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'client_secret.json'), scope)
	client = gspread.authorize(creds)
	logging.debug(str("Buscando " + sheet + " en " + configParserUtils.getConfigParserGet(constants.WORKBOOK_NAME)))
	return client.open(configParserUtils.getConfigParserGet(constants.WORKBOOK_NAME)).worksheet(sheet)


def getHojaPrecios():
	if configParserUtils.getConfigParserGet(constants.MODO_ESCANEO) == "0":
		hoja = getHoja(constants.SHEET_NAME_PRECIOS_TRADER)
	elif configParserUtils.getConfigParserGet(constants.MODO_ESCANEO) == "1":
		hoja = getHoja(constants.SHEET_NAME_PRECIOS_MARKET)
	else:
		logging.error("No se ha definido modo de escaneo")
		raise Exception("No se ha definido modo de escaneo")
	return hoja
