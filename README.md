# alojamento_local

Scraping e tratamento de dados do Registo Nacional do Alojamento Local

Scraping por concelho, baseado num scraper anterior, sobre RoboBrowser, criado por João Antunes, 

Na directoria de saída (configuarada em *fetch_rnal_setup.py*) é criada automaticamente uma nova pasta cujo nome se baseia na data e hora correntes. Dentro dessa pasta, o scraper coloca um CSV por concelho cujo nome tem a seguinte estrutura:

    Down_<DICO>_<NOME>.csv
  
DICO é o código CAOP de 4 dígitos e NOME o nome do concelho em maiusculas. 

## Exemplo de utilização
   
    python3 fetch_rnal.py   (baixa os 308 concelhos)
    python3 fetch_rnal.py -i 10 (baixa a partir do 11º inclusive)
    python3 fetch_rnal.py -i 1 -f 10 (baixa do 2º ao 11º inclusive)

## Dependências

Splinter (módulo Python -- pip install splinter)

## Ficheiros adionais necessários

- fetch_rnal_setup.py - configuração editável
- Concelhos_CAOP2018.csv - lista de todos os concelhos do país

**NOTA IMPORTANTE**:
Antes de usar, não esquecer de configurar as vossas directorias 
de trabalho em fetch_rnal_setup.py !

## Fonte da lista de concelhos

A identificação dos concelhos e dos respectivos código DICOFRE
encontra-se na página da [Carta Administrativa de Portugal (CAOP)](http://www.dgterritorio.pt/cartografia_e_geodesia/cartografia/carta_administrativa_oficial_de_portugal_caop/caop__download_/carta_administrativa_oficial_de_portugal___versao_2018__em_vigor_) onde a podemos baixar a partir do link 'Informação extra'.

