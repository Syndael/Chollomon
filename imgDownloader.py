import os, urllib.request, configParserUtils, spreedUtils, requests, logging, constants
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO, handlers=[logging.FileHandler(os.path.join(os.path.abspath(os.path.dirname(__file__)), configParserUtils.getConfigParserGet(constants.LOG_FILE)), mode='w', encoding='UTF-8'), logging.StreamHandler()])
from os.path import exists

def descargarImgs():
    imgs = spreedUtils.getListaImagenes()
    for img in imgs:
        nombreImg = str("img_" + img.get(constants.CODIGO) + ".png")
        rutaImg = os.path.join(os.path.abspath(os.path.dirname(__file__)), "img", nombreImg)
        if not exists(rutaImg):
            rutaDescarga = descargarImg(nombreImg, img.get(constants.URL_IMAGEN), rutaImg)
            if os.path.getsize(rutaDescarga) < constants.TAMANHO_MIN_IMG:
                os.remove(rutaDescarga)
        else:
            logging.debug(str("No se descarga la " + img.get(constants.CODIGO)))

def descargarImg(nombreImg, url, rutaImg = None):
    logging.info(str("Descargando " + nombreImg + " " + url))
    rutaFinal = None
    if rutaImg:
        rutaFinal = rutaImg
    else:
        rutaFinal = os.path.join(os.path.abspath(os.path.dirname(__file__)), "img", nombreImg)

    f = open(rutaFinal,'wb')
    response = requests.get(url)
    f.write(response.content)
    f.close()

    return rutaFinal
