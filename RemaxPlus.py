import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# PLANILHA
import openpyxl
import uuid

# OUTROS
import os


class RemaxPlus():

	def __init__(self):
		self.numero_de_imoveis_pegos 	= 0
		self.imoves_pegos 				= []

	def iniciar(self):
		paginacorretor = input("\033[94mDigite a url da página do corretor: \033[1;97m")

		self.gerar_planilha(paginacorretor)

	def gerar_planilha(self,paginacorretor):
		self.get_imoveis_from_corretor_page(paginacorretor)

		# CRIAR UMA PLANILHA(BOOK)
		book = openpyxl.Workbook()
		
		# SELECIONANDO UMA PÁGINA
		imovel_page = book['Sheet']

		# NOME DA LINHA
		imovel_page.append([
			'titulo-do-imovel', 
			"preco-imovel", 
			'descricao-imovel', 
			'tamanho-imovel', 
			'numero-de-quartos', 
			'numero-de-suites', 
			'numero-de-banheiro', 
			'numero-de-vagas-de-carro',
			'video',
			'imagem1',
			'imagem2',
			'imagem3',
			'imagem4',
			'imagem5',
			'imagem6',
			'imagem7',
			'imagem8',
			'imagem9',
			'imagem10',
			'imagem11',
			'imagem12',
			'imagem13',
			'imagem14',
			'imagem15',
			
		])


		# Montando array de imovels
		for imovel in self.imoves_pegos:
			todos_imoveis = [
				imovel['titulo_do_imovel'],
				imovel['preco_imovel'],
				imovel['descricao_imovel'],
				imovel['tamanho_imovel'],
				imovel['numero_de_quartos'],
				imovel['numero_de_suites'],
				imovel['numero_de_banheiros'],
				imovel['numero_de_vagas_de_carro'],
				imovel['link_imagens']['video'] if imovel['link_imagens']['video'] != None else "" 
			]


			for imagem in imovel['link_imagens']['imagens']:
				todos_imoveis.append(imagem)

			imovel_page.append(todos_imoveis)

		# ADICIONANDO DADO EM UM PÁGINA
		nome_planilha = uuid.uuid1()

		# SALVAR A PLANILHA
		book.save("planilhas/{}.xlsx".format(nome_planilha))

		print("\033[1;32mPlanilha criada com sucesso: /planilhas/{}.xlsx \033[1;97m".format(nome_planilha))

	def get_imoveis_from_corretor_page(self, url):
		
		#PEGANDO OS DADOS DA URL
		pagina 		= requests.get(url) #retorna 200 para req sucesso
		#pagina.content: Conteudo da Página; html.parser: interpreta o html
		soup 		= BeautifulSoup(pagina.content, 'html.parser')
		indicadores	= soup.select('.card-imovel>a')

		for cardImovelA in indicadores:
			# BUSCANDO DADOS DO IMÓVEL
			hrefDoCard 				= cardImovelA['href'] # Pega o href de do <a>
			urlPaginaImovel 		= f'https://remaxrs.com.br/{hrefDoCard}' # Monta a url da pagina do imovel 
			requisicaoPaginaImovel	= requests.get(urlPaginaImovel) # Faz a requisição para página com os dados do imovel
			paginaDoImovel 			= BeautifulSoup(requisicaoPaginaImovel.content, 'html.parser') # Interpreta o html da página
			dados_imovel 			= self.buscar_dados_imovel(paginaDoImovel)

			# BUSCANDO URL DAS IMAGENS
			link_das_imagens = self.buscar_imagens(urlPaginaImovel)
			
			dados_imovel['link_imagens'] = link_das_imagens
		
			self.imoves_pegos.append(dados_imovel)
			self.numero_de_imoveis_pegos += 1
			os.system("cls")

	def elementoExiste(self, buscador_do_elemento, buscadorCss, paginaDoImovel):
		if buscador_do_elemento in paginaDoImovel.prettify():
			return ((paginaDoImovel.select(buscadorCss))[0].text).strip()
		else:
			return "null"

	def buscar_imagens(self, urlPaginaImovel):
		# Instanciando o Chrome
		option = Options()  
		option.headless = True
		option.add_argument("log-level=3") # Desativa os logs no terminal
		driver = webdriver.Chrome("./chromedriver",options=option) # options=option, faz com que o chrome não aparece e rode em background
		# options=option

		driver.get(urlPaginaImovel)

		# Manipulando html
		driver.find_element(By.CSS_SELECTOR, 'div.verfotos').click() # Simulando cliques

		# Carregando todas imagens
		elemento_total_imagens 	= driver.find_element(By.CSS_SELECTOR, "span#lg-counter-all")
		html_total_imagens 		= elemento_total_imagens.get_attribute('outerHTML')
		soup_total_imagens 		= BeautifulSoup(html_total_imagens, 'html.parser')
		total_de_imagens 		= int(soup_total_imagens.text)
		link_das_imagens 		= {
			"imagens": [],
			"video": "null"
		}
		
		time.sleep(2)

		if(total_de_imagens > 15):
			total_de_imagens = 15
		# Clicando na seta para carregar as imagens
		
		for i in range(1, total_de_imagens, 1):
			driver.find_element(By.CSS_SELECTOR, 'div.lg-next').click()
			time.sleep(1)
			print("\033[1;32mImagem {} coletada!".format(i))

		# Pegando o src das imagens
		elemento_pai_imagens 	= driver.find_element(By.CSS_SELECTOR, 'div.lg-inner')
		html_pai_imagens 		= elemento_pai_imagens.get_attribute('outerHTML')
		soup_pai_imagens		= BeautifulSoup(html_pai_imagens, 'html.parser')
		imagens 				= soup_pai_imagens.select('img.lg-object')
		
		# Criando array de src das imagens
		for imagen in imagens:
			link_das_imagens['imagens'].append(imagen.attrs['src'])

		# BUSCANDO VIDEO
		iframe = soup_pai_imagens.select("div.lg-item>div.lg-video-cont>div.lg-video>iframe")

		if(iframe != []):
			link_das_imagens['video'] = iframe[0]['src']
			print("\033[1;32mVídeo coletado com sucesso!\033[1;97m")

		driver.quit() # Fecha o navegador
		return link_das_imagens

	def buscar_dados_imovel(self, paginaDoImovel):
		os.system("clear")
		print("\033[1;31mNúmero de imóveis pegos até o momento: {}\033[1;97m".format(self.numero_de_imoveis_pegos))
		titulo_do_imovel 			= self.elementoExiste('imovel-header', '.imovel-header>h2', paginaDoImovel)
		preco_imovel 				= self.elementoExiste('linhavalor', 'li.linhavalor>span>strong', paginaDoImovel)
		tamanho_imovel 				= self.elementoExiste('tabelaarea', 'li.tabelaarea', paginaDoImovel).replace('m²','')
		descricao_imovel 			= self.elementoExiste('boxleiamais', '.boxleiamais.maisdescricao>p', paginaDoImovel)
		
		numero_de_quartos 			= self.elementoExiste('tabeladormitorios', '.tabeladormitorios', paginaDoImovel)
		numero_de_suites			= "null"
		numero_de_banheiros 		= self.elementoExiste('tabelabanheiros', 'li.tabelabanheiros', paginaDoImovel)
		numero_de_vagas_de_carro 	= self.elementoExiste('tabelavagas', 'li.tabelavagas', paginaDoImovel)

		# if not (numero_de_quartos is None):
		# 	if "suíte" in numero_de_quartos:
		# 		localizaSeparador 	= list(numero_de_quartos).index('(')
		# 		numero_de_suites 	= list(numero_de_quartos)[(localizaSeparador + 1)]
		if not (numero_de_quartos == "null"):
			if "suíte" in numero_de_quartos:
				localizaSeparador 	= list(numero_de_quartos).index('(')
				numero_de_suites 	= list(numero_de_quartos)[(localizaSeparador + 1)]
		dados = {
			"titulo_do_imovel": titulo_do_imovel,
			"preco_imovel": preco_imovel,
			"tamanho_imovel": tamanho_imovel,
			"descricao_imovel": descricao_imovel,
			"numero_de_quartos": numero_de_quartos,
			"numero_de_suites": numero_de_suites,
			"numero_de_banheiros": numero_de_banheiros,
			"numero_de_vagas_de_carro": numero_de_vagas_de_carro,
			"link_imagens": []
		}
		return dados
