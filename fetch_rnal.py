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
from os.path import join as path_join, exists, getctime
from shutil import copyfile
from datetime import datetime as dt
from time import localtime, sleep

from splinter import Browser

from fetch_rnal_setup import SETUP

# Carregamento da lista de concelhos
def read_concelhos(p_setup, out_concdict):
	
	fl = open(p_setup['CONCELHOS_CSV'])
	cnt = 0
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

		if p_browser.is_element_not_present_by_id("wt103", wait_time=2):
			print("Nao ha link para download")

		# Clicar o link de download, depois de obtido o resultado
		p_browser.click_link_by_id("wt103")
		
		# Fechar o popup de aviso ao utilizador
		alert = p_browser.get_alert()
		alert.accept()

# Mover o CSV corrente para o destino final		
def move_downloaded_files(p_setup, p_finalfolder, p_concdict, p_starttime, p_dico):
	
	frompath = p_setup["DOWNLOADS_TO"]
	
	found = False
	retries = 0
	
	# O aparecimento de cada novo ficheiro baixado é assíncrono, pelo que 
	#  é  necessário aguardar por ele.
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
					found = True
					destfull = path_join(p_finalfolder, 'Down_{0}_{1}.csv'.format(p_dico, p_concdict[p_dico]))
					copyfile(fullpath, destfull)
					unlink(fullpath)
					
		# Espera dois segundos
		sleep(2)
				
				
        		
def main(p_setup, minidx=0, maxidx=-1):

	# Rotina / função principal
	
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
	
	# Para cada código de concelho ...
	for ci, dico in enumerate(concdict.keys()):

		# Avançar para o concelho inicial
		if minidx > 0 and ci < minidx:
			continue

		try:
			
			# Registar o timestamp corrente para detectar qual o ficheiro 
			#  correspondente à presente tentativa de baixar
			ref_datetime = dt.now()

			print(ci, dico, concdict[dico], ref_datetime)

			# Baixar o concelho atual
			baixarConcelho(browser, dico)
			
			# Copiar ficheiro baixado para o destino final
			move_downloaded_files(p_setup, final_dest_path, concdict, ref_datetime, dico)
							
			# Voltar ao formulario principal 
			browser.reload()
				
		except Exception as ex:
			print(ex)
			
		# Sair após o concelho final
		if maxidx > -1 and ci >= maxidx:
			break

		
	if not browser is None:
		browser.quit()

# Ponto de entrada principal		
if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description='Scraping do RNAL')
	parser.add_argument('-i', default=0, help='n.ordem concelho inicial', type=int)	
	parser.add_argument('-f', default=-1, help='n.ordem concelho final', type=int)	
	
	args = parser.parse_args()
	
	main(SETUP, minidx=args.i, maxidx=args.f)

