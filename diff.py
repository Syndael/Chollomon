import logging
import os

import cv2
from skimage import metrics

import configParserUtils
import constants
import imgDownloader
import spreedUtils
import telegramUtils

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO, handlers=[logging.FileHandler(os.path.join(os.path.abspath(os.path.dirname(__file__)), configParserUtils.getConfigParserGet(constants.LOG_FILE)), mode='w', encoding='UTF-8'), logging.StreamHandler()])


def main():
	diferenciasConf = configParserUtils.getConfigParserGet(constants.DIFERENCIA_IMG)
	diferenciasConfF = configParserUtils.getConfigParserGet(constants.DIFERENCIA_IMG_F)
	if diferenciasConf == '0':
		conf = 'EU-JP'
	elif diferenciasConf == '1':
		conf = 'EU-CM'
	elif diferenciasConf == '2':
		conf = 'EU-JP EU-CM'
	if diferenciasConfF == '0':
		forz = 'No'
	else:
		forz = 'Si'
	telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Buscando diferencias {} (forzado {})'.format(conf, forz))
	if diferenciasConf == '2':
		diff('0')
		diff('1')
	else:
		diff(diferenciasConf)

	diffs = spreedUtils.getCartasRevisar(diferenciasConf)
	if diffs:
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Encontradas las diferencias en ' + ', '.join(map(str, diffs)))
	telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Fin busqueda diferencias')


def diff(diferenciasConf):
	for carta in spreedUtils.getCartasDiff(diferenciasConf):
		diffImgOriginal = imgDownloader.descargarImg("diffImgOriginal.jpg", carta.get(constants.IMAGEN_EU))
		diffImgComparar = imgDownloader.descargarImg("diffImgComparar.jpg", carta.get(constants.IMAGEN_OTRO))
		dimensionesOriginales = (600, 430)
		imagenOriginal = cv2.imread(diffImgOriginal)
		imagenComparar = cv2.imread(diffImgComparar)
		imagenOriginal = cv2.resize(imagenOriginal, dimensionesOriginales)
		imagenComparar = cv2.resize(imagenComparar, dimensionesOriginales)
		valor = metrics.mean_squared_error(imagenOriginal, imagenComparar)
		try:
			spreedUtils.rellenarDiff(diferenciasConf, carta.get(constants.FILA), valor, carta.get(constants.CODIGO))
		except Exception as e:
			logging.error('Error rellenando la carta {} con el valor {}'.format(carta.get(constants.CODIGO), valor), e)


if __name__ == '__main__':
	main()
