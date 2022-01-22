import io, os, logging, configparser, gspread, constants, configParserUtils
logging.basicConfig(filename=os.path.join(os.path.abspath(os.path.dirname(__file__)), constants.LOG_FILE), filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

def actualizarPrecios(actual, minimo, alarma, buscar, indiceFila, indices):
    hoja = getHoja(constants.SHEET_NAME_PRECIOS)
    if actual:
        columnaActual = indices.get(constants.ACTUAL)
        logging.debug(str("Actualizando el precio actual " + str(actual) + " en la col " + str(columnaActual) + " fil " + str(indiceFila)))
        hoja.update_cell(indiceFila, columnaActual, actual)
    if minimo:
        columnaMinima = indices.get(constants.MINIMO)
        columnaFminima = indices.get(constants.FMINIMO)
        logging.debug(str("Actualizando el precio minimo " + str(minimo) + " en la col " + str(columnaMinima) + " fil " + str(indiceFila)))
        hoja.update_cell(indiceFila, columnaMinima, minimo)
        hoja.update_cell(indiceFila, columnaFminima, datetime.now().strftime("%d/%m/%Y T %H:%M"))
    if alarma:
        columnaAlarma = indices.get(constants.ALARMA)
        logging.debug(str("Actualizando el precio alarma " + str(alarma) + " en la col " + str(columnaAlarma) + " fil " + str(indiceFila)))
        hoja.update_cell(indiceFila, columnaAlarma, alarma)
    if not buscar:
        columnaBuscar = indices.get(constants.BUSCAR)
        logging.debug("Actualizando buscar a False")
        hoja.update_cell(indiceFila, columnaBuscar, buscar)

def getListaImagenes():
    hoja = getHoja(constants.SHEET_NAME_ALBUM)
    imagenes = []

    cartas = hoja.get_all_records()
    indiceFila = 2
    for carta in cartas:
        numeroCarta = carta.get(constants.NUMERO_MIX)
        urlImg = carta.get(constants.URL_IMAGEN)
        if numeroCarta and len(numeroCarta) > 0 and urlImg and len(urlImg) > 0:
            imagenes.append({constants.NUMERO: numeroCarta, constants.URL_IMAGEN: urlImg})

        indiceFila = indiceFila + 1

    return imagenes

def getNumerosCartas():
    hoja = getHoja(constants.SHEET_NAME_ALBUM)
    numeros = []

    cartas = hoja.get_all_records()
    indiceFila = 2
    for carta in cartas:
        numeroCarta = carta.get(constants.NUMERO)
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
        numeroCarta = carta.get(constants.NUMERO_MIX)
        if numeroCarta and len(numeroCarta) > 0:
            numeros.append(numeroCarta)

        indiceFila = indiceFila + 1

    return numeros

def getListaSeguimientos():
    hoja = getHoja(constants.SHEET_NAME_PRECIOS)
    indicesSeguimientos = []
    seguimientos = []

    indicesSeguimientos.append(getIndices(hoja))

    cartas = hoja.get_all_records()
    indiceFila = 2
    for carta in cartas:
        numeroCarta = carta.get(constants.NUMERO_MIX)
        buscar = carta.get(constants.BUSCAR)
        forzarBusqueda = configParserUtils.getConfigParserGet('forzarBusqueda')
        if forzarBusqueda and forzarBusqueda == "True":
            buscar = "TRUE"
        if buscar and buscar == "TRUE" and numeroCarta and len(numeroCarta) > 0:
            urlTrade = carta.get(constants.TRADE)
            if urlTrade and len(urlTrade) > 0:
                seguimientos.append({constants.FILA: indiceFila, constants.TRADE: urlTrade, constants.NUMERO: carta.get(constants.NUMERO_MIX), constants.ALARMA: carta.get(constants.ALARMA), constants.ACTUAL: carta.get(constants.ACTUAL), constants.MINIMO: carta.get(constants.MINIMO)})

        indiceFila = indiceFila + 1

    logging.info(str("Se buscarán " + str(len(seguimientos)) + " de las " + str((indiceFila - 1)) + " filas leidas en total"))
    indicesSeguimientos.append(seguimientos)
    logging.debug(indicesSeguimientos)
    return indicesSeguimientos

def getIndices(hoja):
    titulos = hoja.row_values(1)

    indicesCampos = {constants.TRADE: 0, constants.NUMERO_MIX: 0, constants.ALARMA: 0, constants.COMPRA: 0, constants.ACTUAL: 0, constants.MINIMO: 0, constants.FMINIMO: 0, constants.NUMERO: 0, constants.BUSCAR: 0, constants.URL_IMAGEN: 0, constants.NUMERO_P: 0}
    for tituloIndex in range(len(titulos)):
        titulo = titulos[tituloIndex]
        if titulo == constants.TRADE:
            indicesCampos[constants.TRADE] = tituloIndex + 1
        elif titulo == constants.NUMERO_MIX:
            indicesCampos[constants.NUMERO_MIX] = tituloIndex + 1
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
        elif titulo == constants.NUMERO_P:
            indicesCampos[constants.NUMERO_P] = tituloIndex + 1

    return indicesCampos

def nuevaFila(nCarta, nMixCarta, urlImg):
    album = getHoja(constants.SHEET_NAME_ALBUM)
    row = album.append_row([nCarta])
    indiceFilaActualizada = int(str(row.get('updates').get('updatedRange')).replace('Album!A', ''))
    indices = getIndices(album)
    album.update_cell(indiceFilaActualizada, indices.get(constants.NUMERO_MIX), nMixCarta)
    album.update_cell(indiceFilaActualizada, indices.get(constants.NUMERO_P), nMixCarta)
    album.update_cell(indiceFilaActualizada, indices.get(constants.URL_IMAGEN), urlImg)

    precios = getHoja(constants.SHEET_NAME_PRECIOS)
    precios.append_row([nMixCarta])

def getHoja(sheet):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'client_secret.json'), scope)
    client = gspread.authorize(creds)
    return client.open(constants.WORKBOOK_NAME).worksheet(sheet)