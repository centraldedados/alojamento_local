
# == Configuração scrping RNAL =========================================
#

SETUP = {
	"URL": "https://rnt.turismodeportugal.pt/RNAL/ConsultaRegisto.aspx?Origem=CP&FiltroVisivel=True",
	"DOWNLOADS_TO": <vossa directoria de saida>,
	"FINALDESTINATION": <vossa directoria de destino>,
	"CONCELHOS_CSV": "Concelhos_CAOP2018.csv", # CSV sem cabeçalhos,
	"TS_FORMAT": "{0:%Y%m%d_%H%M}",
	"RETRIES_LIMIT": 900, # 900 * 2 = 1800 s = 30 min
	"HEADLESS": True,
	"BIG": ['1106', '1312'] # Lisboa e Porto
}

#
# URL - URL de acesso ao formulário de pesquisa do RNAL.
# DOWNLOADS_TO - Directoria onde são colocados os ficheiros baixados do 
# 				 site.
# FINALDESTINATION - Directoria onde são criadas as directorias de 
#					 destino final dos dados.
# CONCELHOS_CSV - Nome do ficheiro de listagem de concelhos, a colocar 
#                 junto deste ficheiro de configuração.
# TS_FORMAT - Formato de data e hora a incluir no nome de cada nova 
#			   directoria de destino final.
# RETRIES_LIMIT - Máximo de tentativas para encontrar o ficheiro baixado
#				   corrente.
# HEADLESS - True: a janela do browser é mantida fechada.
# BIG - Códigos DICO de concelhos a baixar em partes.
# 
# ======================================================================
