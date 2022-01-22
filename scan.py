import asyncio, io, os, logging, decimal, constants, configParserUtils, spreedUtils, imgDownloader, telegramUtils, finder
logging.basicConfig(filename=os.path.join(os.path.abspath(os.path.dirname(__file__)), constants.LOG_FILE), filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)
from pyppeteer import launch
from datetime import datetime
from os.path import exists

async def busqueda(seguimiento, indices):
    chromium = configParserUtils.getConfigParserGet('chromium')
    browser = None
    if chromium and len(chromium) > 0:
        browser = await launch(executablePath = chromium)
    else:
        browser = await launch()

    page = await browser.newPage()
    precioEncontrado = 0

    try:
        url = seguimiento.get(constants.TRADE)
        await page.goto(url, timeout = 100000)
        await page.setViewport(dict(width = 1200, height = 2000));
        try:
            precio = await page.Jeval('.best-deal', 'node => node.innerText')
            await page.J('.min products-table__price products-table__separator--left')

            alarma = seguimiento.get(constants.ALARMA)
            codigo = seguimiento.get(constants.NUMERO)
            if alarma and getFloatES(alarma) >= getFloatUS(precio):
                telegramMensaje = str("He encontrado un " + codigo + " a " + precio + "\n" + url)
                logging.info(str("La carta " + codigo + " con alarma por €" + alarma + " está por " + precio))

                nombreImgFoto = os.path.join(os.path.abspath(os.path.dirname(__file__)), "img", str("img_" + codigo + ".png"))
                if not exists(nombreImgFoto):
                    nombreImgParam = dict(x = 39, y = 290, width = 250, height = 350)
                    await page.screenshot({'path': nombreImgFoto, 'clip': nombreImgParam})

                nombrePrecioFoto = os.path.join(os.path.abspath(os.path.dirname(__file__)), "img", str("prc_" + codigo + ".png"))
                nombrePrecioParam = dict(x = 305, y = 1010, width = 600, height = 405)
                await page.screenshot({'path': nombrePrecioFoto, 'clip': nombrePrecioParam})

                telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet('telegramChatCanalChollosId'), telegramMensaje, nombreImgFoto, nombrePrecioFoto)

                os.remove(nombrePrecioFoto)

            precioEncontrado = getFloatUS(precio.replace('€', ''))
        except Exception as e:
            logging.error("Error leyendo el precio %s" % url, exc_info=e)

    finally:
        await page.close()
        await browser.close()
        if precioEncontrado > 0:
            logging.debug(str("Actualizando el precio " + str(precioEncontrado)))
            actual = None
            minimo = None
            alarma = None
            buscar = True

            if seguimiento.get(constants.ACTUAL) == "" or precioEncontrado != getFloatES(seguimiento.get(constants.ACTUAL)):
                actual = precioEncontrado
            if seguimiento.get(constants.MINIMO) == "" or precioEncontrado < getFloatES(seguimiento.get(constants.MINIMO)):
                minimo = precioEncontrado
            if seguimiento.get(constants.ALARMA) != "" and precioEncontrado <= getFloatES(seguimiento.get(constants.ALARMA)):
                alarma = precioEncontrado - 0.01
            if precioEncontrado < 0.5:
                buscar = False

            spreedUtils.actualizarPrecios(actual, minimo, alarma, buscar, seguimiento.get(constants.FILA), indices)

def getFloatES(num):
    return float(num.replace(".", "").replace(",", ".").replace('€', '').replace(' ', ''))

def getFloatUS(num):
    return float(num.replace(",", "").replace('€', '').replace(' ', ''))

def main():
    buscarCartasNuevas = configParserUtils.getConfigParserGet('buscarCartasNuevas')
    if buscarCartasNuevas and buscarCartasNuevas == "True":
        logging.info("------------------------------------------------------------")
        logging.info("Inicio busqueda de cartas nuevas")
        logging.info("------------------------------------------------------------")

        telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet('telegramLogChatId'), "Buscando cartas nuevas")
        finder.buscarCartasNuevas()

        logging.info("------------------------------------------------------------")
        logging.info("Fin busqueda de cartas nuevas")

    descargarImagenes = configParserUtils.getConfigParserGet('descargarImagenes')
    if descargarImagenes and descargarImagenes == "True":
        logging.info("------------------------------------------------------------")
        logging.info("Inicio descarga imagenes")
        logging.info("------------------------------------------------------------")

        telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet('telegramLogChatId'), "Buscando imagenes")
        imgDownloader.descargarImgs()

        logging.info("------------------------------------------------------------")
        logging.info("Fin descarga imagenes")


    logging.info("------------------------------------------------------------")
    logging.info("Inicio listado")
    logging.info("------------------------------------------------------------")

    fechaInicioEjecucion = datetime.now()
    horaLecturaSeguimiento = fechaInicioEjecucion.hour
    indicesSeguimientos = spreedUtils.getListaSeguimientos()

    while True:
        fechaInicioEscaneado = datetime.now()
        if fechaInicioEscaneado.hour != horaLecturaSeguimiento:
            telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet('telegramLogChatId'), "Refrescando seguimientos....")
            indicesSeguimientos = spreedUtils.getListaSeguimientos()
            horaLecturaSeguimiento = fechaInicioEscaneado.hour

        telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet('telegramLogChatId'), str("Escaneando listado(" + str(len(indicesSeguimientos[1])) + ") a las " + datetime.now().strftime("%H:%M")))

        for seg in indicesSeguimientos[1]:
            try:
                if len(seg) > 2 and seg.get(constants.ALARMA):
                    logging.info(str("Buscando la carta " + seg.get(constants.NUMERO) + " con alarma por " + str(seg.get(constants.ALARMA))))
                else:
                    logging.info(str("Buscando la carta " + seg.get(constants.NUMERO)))

                asyncio.get_event_loop().run_until_complete(busqueda(seg, indicesSeguimientos[0]))
            except Exception as e:
                logging.error("Error al buscar precio en %s" % seg.get(constants.TRADE), exc_info=e)

        telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet('telegramLogChatId'), "Fin de escaneado a las %s" % datetime.now().strftime("%H:%M"))

    telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet('telegramLogChatId'), "El bot ha terminado su ejecución a las %s" % datetime.now().strftime("%H:%M"))

    logging.info("------------------------------------------------------------")
    logging.info("Fin listado")
    logging.info("------------------------------------------------------------")

if __name__ == '__main__':
    main()
