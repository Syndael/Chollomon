import configparser
import os

lectorConfig = None


def getConfigParserGet(clave):
	return getConfigParser().get('config', clave)


def getConfigParser():
	global lectorConfig
	if lectorConfig is None:
		lectorConfig = configparser.RawConfigParser()
		ficheroConfig = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.txt')
		lectorConfig.read(ficheroConfig)

	return lectorConfig


def reloadConfigParser():
	global lectorConfig
	lectorConfig = None
	return getConfigParser()
