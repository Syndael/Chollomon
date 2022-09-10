# Config
LOG_FILE = "logFile"
CHROMIUM = "chromium"
ENTORNO_DOCKER = "entornoDocker"
BUCLE_INFINITO = "bucleInfinito"
BUSCAR_CARTAS_NUEVAS = "buscarCartasNuevas"
CANTIDAD_BUSQUEDAS = "cantidadBusquedas"
COLECCIONES_BUSQUEDAS = "coleccionesBusquedas"
COPIAR_FORMULA = "copiarFormula"
COPIAR_DATOS_GENERALES = "copiarDatosGenerales"
COPIAR_IMAGEN = "copiarImagen"
DESCARGAR_IMAGENES = "descargarImagenes"
ENVIAR_SIN_PRECIO = "enviarSinPrecio"
FORZAR_PRIMERA_BUSQUEDA = "forzarPrimeraBusqueda"
MODO_BUSCADOR = "modoBuscador"
MODO_ESCANEO = "modoEscaneo"
TELEGRAM_BOT_TOKEN = "telegramBotToken"
TELEGRAM_CHAT_CANAL_CHOLLOS_ID = "telegramChatCanalChollosId"
TELEGRAM_CHAT_CANAL_CARTAS_ID = "telegramChatCanalCartasId"
TELEGRAM_LOG_CHAT_ID = "telegramLogChatId"
TIEMPO_MINIMO_BUSQUEDA = "tiempoMinimoBusqueda"
TIEMPO_MINIMO_BUSQUEDA_SPREADSHEET = "tiempoMinimoBusquedaSpreadsheet"
TIEMPO_MINIMO_BUSQUEDA_TELEGRAM = "tiempoMinimoBusquedaTelegram"
WORKBOOK_NAME = "workbookName"

# Urls templates
URL_TEMPLATE_GLOBAL = "https://world.digimoncard.com/images/cardlist/card/"
URL_TEMPLATE_GLOBAL_20220811 = "https://s3.amazonaws.com/prod.bandaitcgplus.files.api/card_image/DG-EN/"
URL_TEMPLATE_JP = "https://digimoncard.com/images/cardlist/card/"
URLS_IMG_FORMAT = ".png"
URL_API_DATOS = "https://digimoncard.io/api-public/search.php?card={}"

# Mapas finder
CANTIDAD = "can"
FORMAT = "form"
PREFIJO = "pre"
TEMPORADA = "temp"

PRE_TEMP_BT = "BT"
PRE_TEMP_EX = "EX"
PRE_TEMP_P = "P"
PRE_TEMP_ST = "ST"
PRE_ALTER = "_P"
PRE_ALTER_20220811 = "P"
SEPARADOR_TEMP = "-"
SEPARADOR_CONFIG = ","
TAG_SELLADO = "-SLL"

WEB_TRADER = "CardTrader"
WEB_MARKET = "CardMarket"

TAMANHO_MIN_IMG = 3000

# Sheet
SHEET_NAME_ALBUM = "Album"
SHEET_NAME_DATOS = "Datos"
SHEET_NAME_PRECIOS_AUX = "Precios Aux"
SHEET_NAME_PRECIOS_MARKET = "Precios Market"
SHEET_NAME_PRECIOS_TRADER = "Precios Trader"
SHEET_NAME_IMGS = "IMGs"

FILA = "fila"

# Campos Sheet
ACTUAL = "Actual"
ALARMA = "Alarma"
BUSCAR = "Buscar"
CODIGO = "Código"
COLOR = "Color"
COMPRA = "Compra"
DP = "DP"
EVOL = "Evol"
FMINIMO = "FMinimo"
MAIN_EFF = "Main Effect"
MINIMO = "Minimo"
NOMBRE = "Nombre"
NUMERO = "Número"
PLAY = "Play"
SOUR_EFF = "Source Effect"
TIPO = "Tipo"
URL_IMAGEN = "URL Imagen"
URL_JAPO = "URL Japo"
URL_PRECIO = "URL Precio"
FORMATEO_IMG = "img_{}.png"
FORMATEO_1 = "{}"
FORMATEO_2 = "{}_dummy"
FORMATEO_3 = "e_{}_dummy"

FRM_AL_B = "=VLOOKUP(A{};Datos!A:M;4;FALSE)"
FRM_AL_H = "=I{}<>A{}"
FRM_AL_I = "=VLOOKUP(A{};Datos!A:M;3;FALSE)"
FRM_AL_K = "=VLOOKUP(A{};Datos!A:M;2;FALSE)"
FRM_AL_L = "=VLOOKUP(A{};Datos!A:M;5;FALSE)"
FRM_AL_M = "=VLOOKUP(A{};Datos!A:M;6;FALSE)"
FRM_AL_N = "=VLOOKUP(A{};Datos!A:M;7;FALSE)"
FRM_AL_O = "=VLOOKUP(A{};Datos!A:M;8;FALSE)"
FRM_AL_P = "=VLOOKUP(A{};Datos!A:M;9;FALSE)"
FRM_AL_V = "=IMAGE(VLOOKUP(A{};Datos!A:M;IF(C{}=\"-\";13;12);FALSE))"
FRM_AL_Y = "=IF(W{}=\"\";\"\";W{}/X{})"
FRM_AL_Z = "=VLOOKUP(A{};'Precios Aux'!A:F;2;FALSE)"
FRM_AL_AA = "=VLOOKUP(A{};'Precios Aux'!A:F;4;FALSE)"
FRM_AL_AB = "=VLOOKUP(A{};'Precios Aux'!A:F;5;FALSE)"
FRM_AL_AC = "=VLOOKUP(A{};'Precios Aux'!A:F;6;FALSE)"
FRM_AL_AD = "=VLOOKUP(A{};'Precios Aux'!A:F;3;FALSE)"
FRM_AL_AE = "=IF(NOT(AA{}=\"\");(IF(C{}=\"-\";0;IF(C{};1;0))+IF(D{}=\"-\";0;IF(D{};1;0)))*AA{};0)*IF(NOT(ISERR(SEARCH(\"-SLL\";A{})));X{};1)"

FRM_DA_B = "=ARRAY_CONSTRAIN(SPLIT(A{};\"-\";FALSE);1;1)"
FRM_DA_C = "=SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(IFERROR(REPLACE(A{};SEARCH(\"_\";A{});3;\"_\");IFERROR(REPLACE(A{}; IFERROR(SEARCHB(\"P-\";A{}) + 1;0) + FIND(\"P\";SUBSTITUTE(A{};\"P-\";\"\"));9;\"\");A{}));\"-AUX\";\"\");\"-SLL\";\"\");\"_\";\"\")"

FRM_PMTI_B = "=VLOOKUP(A{};Datos!A:M;4;FALSE)"
FRM_PMT_C = "=AND(OR(H{}=\"\";H{}>0,5;G{}=\"\";G{}>0,5);NOT(J{}=\"\"))"
FRM_PMT_D = "=VLOOKUP(A{};Album!A:G;7;FALSE)"
FRM_PMT_E = "=VLOOKUP(A{};Album!A:C;3;FALSE)"
FRM_PM_J = "=VLOOKUP(A{};Album!A:W;20;FALSE)"
FRM_PT_J = "=VLOOKUP(A{};Album!A:W;21;FALSE)"
FRM_PMT_K = "=IMAGE(VLOOKUP(A{};Datos!A:M;12;FALSE))"

FRM_IM_B = "=SUBSTITUTE(A{};\"-JP\";\"\")"
FRM_IM_D = "=VLOOKUP(A{};Datos!A:M;2;FALSE)"
FRM_IM_E = "=VLOOKUP(A{};Album!A:D;3;FALSE)"
FRM_IM_F = "=VLOOKUP(A{};Album!A:D;4;FALSE)"
FRM_IM_G = "=VLOOKUP(A{};Datos!A:M;12;FALSE)"
FRM_IM_H = "=VLOOKUP(A{};Datos!A:M;13;FALSE)"
FRM_IM_I = "=IMAGE(G{})"
FRM_IM_J = "=IMAGE(H{})"
FRM_IM_K = "=VLOOKUP(A{};Album!A:AC;27;FALSE)"
FRM_IM_M = "=NOT(ISERROR(SEARCH(\"-SLL\";A{})))"
