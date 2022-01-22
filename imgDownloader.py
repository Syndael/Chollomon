import os, urllib.request, configParserUtils, spreedUtils, requests, logging, constants
logging.basicConfig(filename=os.path.join(os.path.abspath(os.path.dirname(__file__)), constants.LOG_FILE), filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)
from os.path import exists

def descargarImgs():
    imgs = spreedUtils.getListaImagenes()
    for img in imgs:
        nombreImg = str("img_" + img.get(constants.NUMERO) + ".png")
        rutaImg = os.path.join(os.path.abspath(os.path.dirname(__file__)), "img", nombreImg)
        if not exists(rutaImg):
            descargarImg(nombreImg, img.get(constants.URL_IMAGEN), rutaImg)
        else:
            logging.debug(str("No se descarga la " + img.get(constants.NUMERO)))

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
