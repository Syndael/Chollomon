import logging
import os

import gspread

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


def getListaSeguimientos(forzarBusqueda):
	hoja = getHojaPrecios()
	indicesSeguimientos = []
	seguimientos = []
	indicesSeguimientos.append(getIndices(hoja))
	cartas = hoja.get_all_records()
	indiceFila = 2
	for carta in cartas:
		numeroCarta = carta.get(constants.CODIGO)
		buscar = carta.get(constants.BUSCAR)
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
	indicesCampos = {constants.URL_PRECIO: 0, constants.CODIGO: 0, constants.ALARMA: 0, constants.COMPRA: 0, constants.ACTUAL: 0, constants.MINIMO: 0, constants.FMINIMO: 0, constants.NUMERO: 0, constants.BUSCAR: 0, constants.URL_IMAGEN: 0, constants.NOMBRE: 0, constants.URL_JAPO: 0}
	for tituloIndex in range(len(titulos)):
		titulo = titulos[tituloIndex]
		if titulo == constants.URL_PRECIO:
			indicesCampos[constants.URL_PRECIO] = tituloIndex + 1
		elif titulo == constants.CODIGO:
			indicesCampos[constants.CODIGO] = tituloIndex + 1
		elif titulo == constants.ALARMA:
			indicesCampos[constants.ALARMA] = tituloIndex + 1
		elif titulo == constants.COMPRA:
			indicesCampos[constants.COMPRA] = tituloIndex + 1
		elif titulo == constants.ACTUAL:
			indicesCampos[constants.ACTUAL] = tituloIndex + 1
		elif titulo == constants.MINIMO:
			indicesCampos[constants.MINIMO] = tituloIndex + 1
		elif titulo == constants.FMINIMO:
			indicesCampos[constants.FMINIMO] = tituloIndex + 1
		elif titulo == constants.NUMERO:
			indicesCampos[constants.NUMERO] = tituloIndex + 1
		elif titulo == constants.BUSCAR:
			indicesCampos[constants.BUSCAR] = tituloIndex + 1
		elif titulo == constants.URL_IMAGEN:
			indicesCampos[constants.URL_IMAGEN] = tituloIndex + 1
		elif titulo == constants.URL_JAPO:
			indicesCampos[constants.URL_JAPO] = tituloIndex + 1
		elif titulo == constants.NOMBRE:
			indicesCampos[constants.NOMBRE] = tituloIndex + 1

	return indicesCampos


def nuevaFila(nCarta, nMixCarta, urlImg, modo):
	album = getHoja(constants.SHEET_NAME_ALBUM)
	row = album.append_row([nCarta])
	indiceFilaActualizada = int(str(row.get('updates').get('updatedRange')).replace('Album!A', ''))
	indices = getIndices(album)
	album.update_cell(indiceFilaActualizada, indices.get(constants.NUMERO), nCarta)
	album.update_cell(indiceFilaActualizada, indices.get(constants.CODIGO), nMixCarta)
	if modo == 0:
		album.update_cell(indiceFilaActualizada, indices.get(constants.URL_IMAGEN), urlImg)
	elif modo == 1:
		album.update_cell(indiceFilaActualizada, indices.get(constants.URL_JAPO), urlImg)
	preciosTrader = getHoja(constants.SHEET_NAME_PRECIOS_TRADER)
	preciosTrader.append_row([nMixCarta])
	preciosMarket = getHoja(constants.SHEET_NAME_PRECIOS_MARKET)
	preciosMarket.append_row([nMixCarta])
	preciosAux = getHoja(constants.SHEET_NAME_PRECIOS_AUX)
	preciosAux.append_row([nMixCarta])


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
