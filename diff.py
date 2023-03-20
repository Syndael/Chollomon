import logging
import os

import cv2
import numpy
import numpy as np

import configParserUtils
import constants
import imgDownloader
import spreedUtils
import telegramUtils

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO, handlers=[logging.FileHandler(os.path.join(os.path.abspath(os.path.dirname(__file__)), configParserUtils.getConfigParserGet(constants.LOG_FILE)), mode='w', encoding='UTF-8'), logging.StreamHandler()])


def main():
	telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Buscando diferencias')
	diferenciasConf = configParserUtils.getConfigParserGet(constants.DIFERENCIA_IMG)
	for carta in spreedUtils.getCartasDiff(diferenciasConf):
		diffImgOriginal = imgDownloader.descargarImg("diffImgOriginal.jpg", carta.get(constants.IMAGEN_EU))
		diffImgComparar = imgDownloader.descargarImg("diffImgComparar.jpg", carta.get(constants.IMAGEN_OTRO))

		dimensionesOriginales = (430, 600)

		imagenOriginal = cv2.imread(diffImgOriginal, 0)
		imagenOriginal = cv2.resize(imagenOriginal, dimensionesOriginales, interpolation=cv2.INTER_AREA)
		imagenComparar = cv2.imread(diffImgComparar, 0)
		imagenComparar = cv2.resize(imagenComparar, dimensionesOriginales, interpolation=cv2.INTER_AREA)

		diferencia = cv2.absdiff(imagenOriginal, imagenComparar)
		diferencia = diferencia.astype(np.uint8)
		diferencia = (numpy.count_nonzero(diferencia) * 100) / diferencia.size

		spreedUtils.rellenarDiff(diferenciasConf, carta.get(constants.FILA), diferencia, carta.get(constants.CODIGO))

	telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Fin busqueda diferencias')


# 		thresh = cv2.threshold(diferencia, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
# 		contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# 		contours = contours[0] if len(contours) == 2 else contours[1]
#
# 		mask = np.zeros(imagenOriginal.shape, dtype='uint8')
# 		filled = imagenComparar.copy()
# 		for c in contours:
# 			area = cv2.contourArea(c)
# 			if area > 100:
# 				x, y, w, h = cv2.boundingRect(c)
# 				cv2.rectangle(imagenOriginal, (x, y), (x + w, y + h), (36, 255, 12), 2)
# 				cv2.rectangle(imagenComparar, (x, y), (x + w, y + h), (36, 255, 12), 2)
# 				cv2.drawContours(mask, [c], 0, (0, 255, 0), -1)
# 				cv2.drawContours(filled, [c], 0, (0, 255, 0), -1)
#
# 		imagenOriginalClean = cv2.imread(diffImgOriginal, 0)
# 		imagenOriginalClean = cv2.resize(imagenOriginalClean, dimensionesOriginales, interpolation=cv2.INTER_AREA)
# 		fila1 = np.hstack((imagenOriginalClean, imagenOriginal, imagenComparar))
# 		fila2 = np.hstack((filled, diferencia, mask))
# 		mostrarImg(np.vstack((fila1, fila2)))
#
#
# def mostrarImg(image, conversion=cv2.COLOR_BGR2RGB):
# 	image = cv2.cvtColor(image, conversion)
# 	plt.imshow(image)
# 	plt.xticks([])
# 	plt.yticks([])
# 	plt.show()


if __name__ == '__main__':
	main()
