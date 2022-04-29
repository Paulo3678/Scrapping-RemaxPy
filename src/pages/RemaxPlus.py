import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


from tkinter import *
from tkinter import ttk
import os
import shutil
import time


class RemaxPlus:

	def __init__(self):
		self.app 							= None
		self.input_url_pagina_corretor 		= None
		self.botao_gerar_planilha			= None
		self.label_carregando 				= None
		self.label_dados_pegos_atualmente	= None
		self.tamanho_botao_carregando		= 0
		self.numero_de_imoveis_pegos 		= 0
		self.imoves_pegos 					= []

	def iniciar(self):
		self.app = Tk()
		self.app.title("Gerador de planilhas")
		self.app.geometry("500x360")
		self.app.minsize(500,360)
		self.app.maxsize(500,360)
		frame = ttk.LabelFrame(self.app, width=290)
		frame.pack(padx=30, pady=70)

		label_url_pagina_corretor = ttk.Label(frame, text="Url página do corretor: ")
		label_url_pagina_corretor.grid(row=0, column=0,sticky=W)

		self.input_url_pagina_corretor = ttk.Entry(frame, width=50)
		self.input_url_pagina_corretor.grid(row=1, columnspan=4, padx=2, pady=3)

		self.botao_gerar_planilha = ttk.Button(frame, width=30, text="Gerar planilha", command=self.gerar_planilha)
		self.botao_gerar_planilha.grid(row=4, columnspan=5, padx=30, pady=5)

		self.label_carregando = ttk.Label(frame, width=0)
		self.label_carregando.config(background="green")
		self.label_carregando.grid(row=5, columnspan=5, padx=30, pady=5)

		self.label_dados_pegos_atualmente = ttk.Label(frame, text="Total de imóveis pegos: 0")
		self.label_dados_pegos_atualmente.grid(row=6, columnspan=4, padx=2, pady=3)

		self.app.mainloop()

	def gerar_planilha(self):
		self.get_imoveis_from_corretor_page(self.input_url_pagina_corretor.get())

	# funcao para realizar o webscraping
	def get_imoveis_from_corretor_page(self, url):
		
		#Pega os dados da url
		pagina 		= requests.get(url) #retorna 200 para req sucesso
		#pagina.content: Conteudo da Página; html.parser: interpreta o html
		soup 		= BeautifulSoup(pagina.content, 'html.parser')
		indicadores	= soup.select('.card-imovel>a')
		print(indicadores)

		for cardImovelA in indicadores:
			# print(" =============== BUSCANDO DADOS DO IMÓVEL =============== \n")
			self.app.update() # É necessário chamar root.update() de tempos em tempos para atualizar a tela gráfica do tkinter, para ver mais https://pt.stackoverflow.com/questions/337313/travamento-do-programa-ao-execultar-a-fun%C3%A7%C3%A3o-tkinter-python3

			hrefDoCard 				= cardImovelA['href'] # Pega o href de do <a>
			urlPaginaImovel 		= f'https://remaxrs.com.br/{hrefDoCard}' # Monta a url da pagina do imovel 
			requisicaoPaginaImovel	= requests.get(urlPaginaImovel) # Faz a requisição para página com os dados do imovel
			paginaDoImovel 			= BeautifulSoup(requisicaoPaginaImovel.content, 'html.parser') # Interpreta o html da página
			dados_imovel 			= self.buscar_dados_imovel(paginaDoImovel)

			# print("\n =============== DADOS CARREGADOS COM SUCESSO =============== \n")

			# ================= Buscando URL das Imagens =================
			link_das_imagens = self.buscar_imagens(urlPaginaImovel)
			
			dados_imovel['link_imagens'] = link_das_imagens
		
			self.imoves_pegos.append(dados_imovel)
			print(self.imoves_pegos)
			self.numero_de_imoveis_pegos += 1
			self.label_dados_pegos_atualmente['text'] = "Total de imóveis pegos: {}".format(self.numero_de_imoveis_pegos)
			self.atualizar_botao_carregando()

	def elementoExiste(self, buscador_do_elemento, buscadorCss, paginaDoImovel):
		if buscador_do_elemento in paginaDoImovel.prettify():
			return ((paginaDoImovel.select(buscadorCss))[0].text).strip()
		else:
			return None

	def buscar_imagens(self, urlPaginaImovel):
		self.app.update()

		# Instanciando o Chrome
		option = Options()
		option.headless = True
		option.add_argument("log-level=3") # Desativa os logs no terminal
		driver = webdriver.Chrome() # options=option, faz com que o chrome não aparece e rode em background
		# options=option

		driver.get(urlPaginaImovel)

		# Manipulando html
		driver.find_element(By.CSS_SELECTOR, 'div.verfotos').click() # Simulando cliques

		# Carregando todas imagens
		elemento_total_imagens 	= driver.find_element(By.CSS_SELECTOR, "span#lg-counter-all")
		html_total_imagens 		= elemento_total_imagens.get_attribute('outerHTML')
		soup_total_imagens 		= BeautifulSoup(html_total_imagens, 'html.parser')
		total_de_imagens 		= int(soup_total_imagens.text)
		link_das_imagens 		= []
		

		if(total_de_imagens > 15):
			total_de_imagens = 15
		# Clicando na seta para carregar as imagens
		
		for i in range(1, total_de_imagens, 1):
			driver.find_element(By.CSS_SELECTOR, 'div.lg-next').click()
			self.app.update()
			time.sleep(1)

		# Pegando o src das imagens
		elemento_pai_imagens 	= driver.find_element(By.CSS_SELECTOR, 'div.lg-inner')
		html_pai_imagens 		= elemento_pai_imagens.get_attribute('outerHTML')
		soup_pai_imagens		= BeautifulSoup(html_pai_imagens, 'html.parser')
		imagens 				= soup_pai_imagens.select('img.lg-object')

		# Criando array de src das imagens
		for imagen in imagens:
			link_das_imagens.append(imagen.attrs['src'])

		driver.quit() # Fecha o navegador
		return link_das_imagens

	def atualizar_botao_carregando(self):
		self.label_carregando.config(width=((self.tamanho_botao_carregando)+1))
		self.tamanho_botao_carregando+=1

	def buscar_dados_imovel(self, paginaDoImovel):
		self.app.update()
		titulo_do_imovel 			= self.elementoExiste('imovel-header', '.imovel-header>h2', paginaDoImovel)
		preco_imovel 				= self.elementoExiste('linhavalor', 'li.linhavalor>span>strong', paginaDoImovel)
		tamanho_imovel 				= self.elementoExiste('tabelaarea', 'li.tabelaarea', paginaDoImovel).replace('m²','')
		descricao_imovel 			= self.elementoExiste('boxleiamais', '.boxleiamais.maisdescricao>p', paginaDoImovel)
		
		numero_de_quartos 			= self.elementoExiste('tabeladormitorios', '.tabeladormitorios', paginaDoImovel)
		numero_de_suites			= None
		numero_de_banheiros 		= self.elementoExiste('tabelabanheiros', 'li.tabelabanheiros', paginaDoImovel)
		numero_de_vagas_de_carro 	= self.elementoExiste('tabelavagas', 'li.tabelavagas', paginaDoImovel)

		if not (numero_de_quartos is None):
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