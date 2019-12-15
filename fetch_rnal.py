# -*- coding: utf-8 -*-

# ======================================================================
# Licença MIT / MIT License
# ======================================================================
# Copyright © , Rui Cavaco
# ----------------------------------------------------------------------
# Por este meio, é dada permissão, livre de encargos, a qualquer pessoa 
# de obter uma cópia deste software e da documentação associada 
# (o "Software"), de negociar o Software sem restrições, incluindo os
# direitos de usar, copiar, modificar, fundir, publicar, distribuir, 
# sub-licenciar e/ou vender cópias do Software, sem restrições, e de
# permitir às pessoas a quem o Software seja fornecido que o façam 
# também, sob as seguintes condições:
# A notificação de copyright e a notificação de permissões concedidas, 
# dadas acima, deverão ser incluídas em todas as cópias ou partes 
# substanciais do Software.
# O SOFTWARE É FORNECIDO "AS IS", TAL COMO SE ENCONTRA, SEM GARANTIAS DE
# QUALQUER TIPO, SEJAM EXPLÍCITAS OU IMPLÍCITAS, INCLUINDO, MAS NÃO SE
# LIMITANDO A, GARANTIAS DE COMERCIALIZAÇÃO, DE ADEQUAÇÃO PARA UM
# PROPÓSITO ESPECÍFICO E DE NÃO TRANSGRESSÃO DA LEI. EM CASO ALGUM SERÃO
# ADMISSÍVEIS REIVINDICAÇÕES POR PERDAS E DANOS IMPUTÁVEIS AOS AUTORES 
# OU DETENTORES DO COPYRIGHT, DECORRENTES DA UTILIZAÇÃO, LEGAL OU 
# ILÍCITA, DO SOFTWARE OU DE QUALQUER FORMA LIGADOS AO SOFTWARE OU A 
# DERIVAÇÕES DO MESMO.
# ======================================================================
# Project history
# ----------------------------------------------------------------------
# (RC, 2019-11-16) - Criação
# (RC, 2019-12-14) - Final
# ======================================================================
#
# ======================================================================
# Scraping do Registo Nacional do Alojamento Local, por concelho.
# ----------------------------------------------------------------------
# Baseado num scraper anterior, sobre RoboBrowser, 
#  criado por João Antunes.
#
#  Exemplo de utilização:
#    
#      python3 fetch_rnal.py   (baixa os 308 concelhos)
#      python3 fetch_rnal.py -i 10 (baixa a partir do 11º inclusive)
#      python3 fetch_rnal.py -i 1 -f 10 (baixa do 2º ao 11º inclusive)
#
#  Dependências:
# 
#  		Splinter (módulo Python -- pip install splinter)
#
# ======================================================================
# Ficheiros adionais necessários
# ----------------------------------------------------------------------
# 
# -- fetch_rnal_setup.py - configuração editável
# -- Concelhos_CAOP2018.csv - lista de todos os concelhos do país
# 
#  NOTA IMPORTANTE!! 
# 	Antes de usar, não esquecer de configurar as vossas directorias 
#      de trabalho em fetch_rnal_setup.py !
#
# -- Fonte da lista de concelhos  -------------------------------------
#
# A identificação dos concelhos e dos respectivos código DICOFRE
#  encontra-se na página ...
#       http://www.dgterritorio.pt/cartografia_e_geodesia/cartografia/carta_administrativa_oficial_de_portugal_caop/caop__download_/carta_administrativa_oficial_de_portugal___versao_2018__em_vigor_/
#
#   ... onde a podemos baixar a partir do link 'Informação extra'.
#
# ======================================================================

import argparse

from os import listdir, unlink, rename, mkdir
from os.path import join as path_join, exists, getctime, getsize
#from shutil import copyfile
from datetime import datetime as dt
from time import localtime, sleep
from re import split as re_split

from splinter import Browser

from fetch_rnal_setup import SETUP

MAX_COUNTER = 60

# Método de cópia de ficheiros com transformação da codificação de 
#  caracteres de Latin-1 (ISO_8859-1:1987, semelhante a Windows-1252 mas
#  mais abrangente) para UTF-8.
def copyfile(p_frompath, p_topath):
	READSZ = 100
	with open(p_frompath, 'r', encoding="latin-1") as rfilehandle:
		with open(p_topath, 'w', encoding="utf-8") as tfilehandle:
			readcontents = rfilehandle.readlines(READSZ)
			while len(readcontents) > 0:
				tfilehandle.writelines(readcontents)
				readcontents = rfilehandle.readlines(READSZ)
			

# Carregamento da lista de concelhos
def read_concelhos(p_setup, out_concdict):
	
	fl = open(p_setup['CONCELHOS_CSV'])

	for row in fl:
		dicofre, conc = row.split(';')
		out_concdict[dicofre] = conc.strip()

# Operação de baixar o CSV do concelho corrente		
def baixarConcelho(p_browser, p_dico_str):
	
		if p_browser.is_element_not_present_by_id("wt140", wait_time=2):
			print("Nao ha selector de concelhos")
	
		# Seleccionar o concelho
		#   eliminado trailing zeros
		dico = str(int(p_dico_str))
		p_browser.select("wt140", dico)
		
		# Clicar em Pesquisar
		p_browser.find_by_id("wt131").click()

		counter = 0
		while counter < MAX_COUNTER and p_browser.is_element_not_present_by_id("wt103", wait_time=2):
			counter += 1
			sleep(2)
			
		if p_browser.is_element_not_present_by_id("wt103"):	
			raise RuntimeError("Nao ha link para download")			

		# Clicar o link de download, depois de obtido o resultado
		p_browser.click_link_by_id("wt103")
		
		# Fechar o popup de aviso ao utilizador
		alert = p_browser.get_alert()
		alert.accept()

# Operação de baixar multiplos CSV do concelho corrente		
def baixarConcelhoParte(p_browser, p_dico_str, fromdate=None, todate=None):
	
		if p_browser.is_element_not_present_by_id("wt140", wait_time=2):
			print("Nao ha selector de concelhos")
	
		# Seleccionar o concelho
		#   eliminado trailing zeros
		dico = str(int(p_dico_str))
		p_browser.select("wt140", dico)
		
		# Marcar data de inicio
		if not fromdate is None:
			
			counter = 0
			while counter < MAX_COUNTER and p_browser.is_element_not_present_by_id("wtData1", wait_time=2):
				counter += 1
				sleep(2)

			if p_browser.is_element_not_present_by_id("wtData1"):
				raise RuntimeError("Nao ha caixa de data inicial")	
				
			p_browser.fill('wtData1', fromdate)

		# Marcar data de fim
		if not todate is None:
			
			counter = 0
			while counter < MAX_COUNTER and p_browser.is_element_not_present_by_id("wtData2", wait_time=2):
				counter += 1
				sleep(2)

			if p_browser.is_element_not_present_by_id("wtData2"):
				raise RuntimeError("Nao ha caixa de data final")	
				
			p_browser.fill('wtData2', todate)
		
		# Clicar em Pesquisar
		p_browser.find_by_id("wt131").click()

		counter = 0
		while counter < MAX_COUNTER and p_browser.is_element_not_present_by_id("wt103", wait_time=2):
			counter += 1
			sleep(2)
			
		if p_browser.is_element_not_present_by_id("wt103"):	
			raise RuntimeError("Nao ha link para download")			

		# Clicar o link de download, depois de obtido o resultado
		p_browser.click_link_by_id("wt103")
		
		# Fechar o popup de aviso ao utilizador
		alert = p_browser.get_alert()
		alert.accept()

# Mover o CSV corrente para o destino final		
def move_downloaded_files(p_setup, p_finalfolder, p_concdict, p_starttime, p_dico, p_exec_idx, opt_suffix=''):
	
	frompath = p_setup["DOWNLOADS_TO"]
	
	found = False
	retries = 0
	
	# O aparecimento de cada novo ficheiro baixado é assíncrono, pelo que 
	#  é  necessário aguardar pelo respectivo fecho.
	# São executadas sucessivas tentativas de encontrar um ficheiro CSV
	#  com data posterior a p_starttime separadas por um intervalo de dois segundos 
	#  até um número máximo de tentativas indicado em p_setup["RETRIES_LIMIT"].
	
	while not found and retries < p_setup["RETRIES_LIMIT"]:
	
		retries += 1
		for fl in listdir(frompath):
			
			if fl.endswith(".csv"):
				
				fullpath = path_join(frompath, fl)				
				
				creation_time = getctime(fullpath)
				structTime = localtime(creation_time)			
				creationDT = dt(*structTime[:6])
				
				if creationDT < p_starttime:
					# Se o ficheiro encontrado é anterior a p_starttime, 
					#  pertence a uma execução anterior e deve ser apagado.
					unlink(fullpath)
				else:
					# O ficheiro CSV pretendido está identificado, vamos copia-lo
					#  para o destino final com um nome que indica o concelho 
					#  respectivo
					
					########################################################
					# SOLUÇÃO ISSUE #2
					########################################################
					# Necessário verificar se o browser já terminou de 
					#  preencher o ficheiro baixado, avaliando se, após
					#  um segundo, o tamanho se mantem igual e maior que
					#  zero.
					maxcounttest = 20
					counttest = 0
					prevsz = 0
					sz = getsize(fullpath)
					while counttest < maxcounttest and (sz < 1 or sz != prevsz):
						counttest += 1
						sleep(1)
						prevsz = sz
						sz = getsize(fullpath)
						
					if sz < 1:
						raise RuntimeError("Ficheiro de download esta' vazio")
					
					found = True
					concname = p_concdict[p_dico]
					if len(opt_suffix) > 0:
						fname = 'Down_{0}_{1}_{2}.csv'.format(p_dico, concname, opt_suffix)
					else:
						fname = 'Down_{0}_{1}.csv'.format(p_dico, concname)
					
					print(">", p_exec_idx, concname, fname)	
					destfull = path_join(p_finalfolder, fname)
					copyfile(fullpath, destfull)
					unlink(fullpath)
					
		# Espera dois segundos
		sleep(2)
		
	#print("retries download:", retries)	
				
				
        		
def main(p_setup, minidx=0, maxidx=-1, opt_excs=[]):

	# Rotina / função principal
	#
	# Segue a ordem da lista de concelhos CAOP para baixar cada
	#  concelho sequencialmente.
	#
	# Parâmetros -------------------------------------------------------
	# minidx - minimo indice da lista CAOP - primeiro concelho a 
	#   processar, -1 começa do início
	# maxidx - máximo indice da lista CAOP - último concelho a 
	#   processar, -1 indica o final da lista
	#
	#  Parâmetro opcional
	# opt_excs - códigos DICO a excluir do processamento, 
	#	em texto separado por vírgulas
	# ------------------------------------------------------------------

	# Alteracoes de perfil do utilizador do Firefox para garantir que os 
	#  downloads sao encaminhados para uma pasta, sem interaccao com o 
	#  utilizador, evitando a abertura do popup a perguntar se o utilizador 
	#  quer baixar ou abrir o ficheiro.	
	profile = {
		"browser.download.folderList": 2,
		"browser.download.dir": p_setup["DOWNLOADS_TO"],
		"browser.download.useDownloadDir": True,
		"browser.helperApps.neverAsk.saveToDisk": "text/csv"
	}
	
	# Leitura dos códigos DICO e nomes de concelho da lista configurada
	#  em CONCELHOS_CSV
	concdict = {}
	read_concelhos(p_setup, concdict)
	# print(concdict)
	
	########################################################
	# SOLUÇÃO ISSUE #1
	########################################################
	# Divisao dos concelhos maiores em partes para evitar
	#  'connection reset'			
	datas_download_parcial = [	
		[None,"2014-12-31"],		
		["2015-01-01", "2015-12-31"],		
		["2016-01-01", "2016-06-30"],
		["2016-07-01", "2016-12-31"],
		["2017-01-01", "2017-06-30"],
		["2017-07-01", "2017-12-31"],
		["2018-01-01", "2018-03-31"],
		["2018-04-01", "2018-06-30"],
		["2018-07-01", "2018-09-30"],
		["2018-10-01", "2018-12-31"],
		["2019-01-01", "2019-06-30"],
		["2019-07-01", "2019-12-31"]
		
		# ["2020-01-01", None]
	]
	#
	sufixos_download_parcial = [
		"ATE2014",
		"2015",
		"2016_1SEM",
		"2016_2SEM",
		"2017_1SEM",
		"2017_2SEM",
		"2018_1TRIM",
		"2018_2TRIM",
		"2018_3TRIM",
		"2018_4TRIM",
		"2019_1SEM",
		"2019_2SEM"
		#"DESDE2020"
	]
	########################################################
		
	# Preparacao da directoria para destino final dos ficheiros CSV
	# definitvos, copia dos ficheiros baixados mas com nomes alterados 
	ts_dirname = p_setup["TS_FORMAT"].format(dt.now())
	final_dest_path = path_join(p_setup["FINALDESTINATION"], ts_dirname)
	if not exists(final_dest_path):
		try:
			mkdir(final_dest_path)
		except OSError:
			print ("Criação de directoria %s falhou" % final_dest_path)
		else:
			print ("Criação de directoria foi bem sucedida em %s " % final_dest_path)	

	browser = Browser('firefox', profile_preferences=profile, headless=p_setup["HEADLESS"])
	browser.visit(p_setup["URL"])

	if len(opt_excs) > 0:
		print("Concelhos a excluir:", opt_excs)
		
	exec_idx = 0
	
	# Para cada código de concelho ...
	for ci, dico in enumerate(concdict.keys()):
				
		# Saltar excepções
		if dico in opt_excs:
			continue

		# Avançar para o concelho inicial
		if minidx > 0 and ci < minidx:
			continue
			
		exec_idx += 1

		try:
			
			# Registar o timestamp corrente para detectar qual o ficheiro 
			#  correspondente à presente tentativa de baixar
			ref_datetime = dt.now()

			# Baixar o concelho atual			
			if dico in p_setup["BIG"]:	
				########################################################
				# SOLUÇÃO ISSUE #1
				########################################################
				# Divisao dos concelhos maiores em partes para evitar
				#  'connection reset'			
				for i, sufixo in enumerate(sufixos_download_parcial):					
					fromd, tod = datas_download_parcial[i]
					baixarConcelhoParte(browser, dico, fromdate=fromd, todate=tod)
					# Copiar ficheiro baixado para o destino final
					move_downloaded_files(p_setup, final_dest_path, concdict, ref_datetime, dico, exec_idx, opt_suffix=sufixo)	
					# Voltar ao formulario principal 
					browser.reload()
			else:	
				baixarConcelho(browser, dico)
				# Copiar ficheiro baixado para o destino final
				move_downloaded_files(p_setup, final_dest_path, concdict, ref_datetime, dico, exec_idx)		
												
				# Voltar ao formulario principal 
				browser.reload()
				
		except Exception as ex:
			#raise ex
			print("... excecao em main():", ex)
			
		# Sair após o concelho final
		if maxidx > -1 and ci >= maxidx:
			break

		
	if not browser is None:
		browser.quit()

# Ponto de entrada principal		
if __name__ == "__main__":

	# Parâmetros opcionais ---------------------------------------------
	# -i - minimo indice da lista CAOP - primeiro concelho a processar
	# -f - máximo indice da lista CAOP - último concelho a processar
	# -x - códigos DICO a excluir do processamento, 
	#	em texto separado por vírgulas
	# ------------------------------------------------------------------
	
	parser = argparse.ArgumentParser(description='Scraping do RNAL')
	parser.add_argument('-i', default=0, help='n.ordem concelho inicial', type=int)	
	parser.add_argument('-f', default=-1, help='n.ordem concelho final', type=int)	
	parser.add_argument('-x', default="", help='exclusoes, DICO seprados por virgulas')	
	
	args = parser.parse_args()
	
	exceptions = []
	if len(args.x) > 0:
		exceptions.extend([spl for spl in re_split("[, ]", args.x) if len(spl.strip()) > 0])
	
	main(SETUP, minidx=args.i, maxidx=args.f, opt_excs=exceptions)

