import logging
import os
import re
import shutil

import configParserUtils
import constants
import filler
import finder
import scan
import telegramUtils

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO, handlers=[logging.FileHandler(os.path.join(os.path.abspath(os.path.dirname(__file__)), configParserUtils.getConfigParserGet(constants.LOG_FILE)), mode='w', encoding='UTF-8'), logging.StreamHandler()])


def sobreEscribirConfig(config):
	sobrescrito = False
	if config:
		if not os.path.exists(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.tmp')) and os.path.exists(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.txt')):
			os.rename(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.txt'), os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.tmp'))
		if os.path.exists(os.path.join(os.path.abspath(os.path.dirname(__file__)), config)):
			shutil.copy(os.path.join(os.path.abspath(os.path.dirname(__file__)), config), os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.txt'))
			sobrescrito = True
		else:
			restablecerConfig()

	configParserUtils.reloadConfigParser()
	return sobrescrito


def restablecerConfig():
	if os.path.exists(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.tmp')):
		if os.path.exists(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.txt')):
			os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.txt'))
		os.rename(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.tmp'), os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.txt'))


def main():
	cadenas = configParserUtils.getConfigParserGet(constants.CADENA)
	ejecuciones = []
	if cadenas and re.match(r'([0-9a-zA-Z_]+.txt\|[a-zA-Z]+;?)+', cadenas):
		for cadena in cadenas.split(';'):
			if not cadena:
				logging.debug("Bloque vacio")
			elif re.match(r'([0-9a-zA-Z_]+.txt\|[a-zA-Z]+)', cadena):
				ejecucion = cadena.split('|')
				ejecuciones.append({constants.CADENA_CONF: ejecucion[0], constants.CADENA_PRG: ejecucion[1]})
			else:
				logging.warning('No se ha incluido la cadena {}, está mal formateada'.format(cadena))

	telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Se ejecutarán en cadena los siguientes bloques: {}'.format(ejecuciones))
	for ejecucion in ejecuciones:
		sobrescrito = sobreEscribirConfig(ejecucion.get(constants.CADENA_CONF))
		telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), 'Ejecutando: {}'.format(ejecucion))
		if sobrescrito:
			try:
				# if ejecucion.get(constants.CADENA_PRG) == 'diff':
				# 	diff.main()
				# el
				if ejecucion.get(constants.CADENA_PRG) == 'finder':
					finder.main()
				elif ejecucion.get(constants.CADENA_PRG) == 'filler':
					filler.main()
				elif ejecucion.get(constants.CADENA_PRG) == 'scan':
					scan.main()
				else:
					logging.warning('El proceso {} no está implementado'.format(ejecucion.get(constants.CADENA_PRG)))
			except Exception as e:
				msgError = 'Error ejecutando el bloque {}'.format(ejecucion)
				logging.error(msgError, e)
				restablecerConfig()
				telegramUtils.enviarMensajeTelegram(configParserUtils.getConfigParserGet(constants.TELEGRAM_LOG_CHAT_ID), msgError)
		else:
			logging.warning('No se ha encontrado la conf del bloque {}'.format(ejecucion))

	restablecerConfig()


if __name__ == '__main__':
	main()
