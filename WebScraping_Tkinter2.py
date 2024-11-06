import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import tkinter as tk
import webbrowser


# Função para coletar os produtos de uma página
def coletar_produtos(soup):
    produtos = soup.find_all("div", class_="ui-search-result__wrapper")
    lista_produtos = []

    for produto in produtos:
        link_url = produto.find("a", class_="ui-search-link")["href"]
        preco_elem = produto.find('div',
                                  class_="ui-search-item__group ui-search-item__group--price ui-search-item__group--price-grid-container")
        preco = preco_elem.text if preco_elem else "Preço não disponível"

        titulo_element = produto.find('h2', class_="ui-search-item__title")
        titulo = titulo_element.text if titulo_element else "Título não disponível"

        lista_produtos.append({
            "titulo": titulo,
            "link_url": link_url,
            "preco": preco,
        })

    return lista_produtos


# Função para encontrar a próxima página e coletar os produtos
def coletar_proximas_paginas(url_base):
    lista_total_produtos = []
    url_atual = url_base

    while url_atual:
        response = requests.get(url_atual)
        soup = BeautifulSoup(response.text, 'html.parser')

        lista_produtos = coletar_produtos(soup)
        lista_total_produtos.extend(lista_produtos)
        next_button = soup.find("span", class_="andes-pagination__arrow-title", text="Siguiente")

        if next_button:
            url_next = next_button.parent["href"]
            url_atual = url_next
        else:
            url_atual = None

    return lista_total_produtos


# Interface gráfica Tkinter
root = tk.Tk()
root.title("Mercado Livre Scraper")

# Widgets
label_produto = tk.Label(root, text="Digite o produto:")
label_produto.pack()

entry_produto = tk.Entry(root)
entry_produto.pack()

button_buscar = tk.Button(root, text="Buscar")
button_buscar.pack()

# Scrollbar e Text widget para exibir os produtos
scrollbar = tk.Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_resultado = tk.Text(root, yscrollcommand=scrollbar.set)
text_resultado.pack(expand=True, fill=tk.BOTH)

scrollbar.config(command=text_resultado.yview)


# Função para lidar com a ação de clicar nos URLs
def abrir_url(event):
    index = text_resultado.index(tk.CURRENT)
    url = text_resultado.get(f"{index} linestart", f"{index} lineend")
    if url.startswith("http"):
        webbrowser.open(url)  # Abre o URL no navegador padrão


# Função para exibir os produtos ao clicar no botão
def exibir_produtos():
    produto = entry_produto.get()

    # Constrói a URL de pesquisa no Mercado Livre
    url_pesquisa = f"https://lista.mercadolivre.com.br/{quote(produto)}#D[A:{quote(produto)}]"

    # Coleta os produtos de todas as páginas
    lista_total_produtos = coletar_proximas_paginas(url_pesquisa)

    # Limpa o Text widget antes de adicionar novos resultados
    text_resultado.delete("1.0", tk.END)

    # Configura a tag para o preço em vermelho
    text_resultado.tag_config("preco", foreground="red")
    text_resultado.tag_config("url", foreground="blue", underline=True)

    # Exibe as informações
    for produto in lista_total_produtos:
        text_resultado.insert(tk.END, f"Titulo: {produto['titulo']}\n")

        # Insere o preço com a tag "preco" para ficar em vermelho
        preco_inicio = text_resultado.index(tk.END)
        text_resultado.insert(tk.END, f"Preço: {produto['preco']}\n")
        preco_fim = text_resultado.index(tk.END)
        text_resultado.tag_add("preco", preco_inicio, preco_fim)

        text_resultado.insert(tk.END, f"URL: {produto['link_url']}\n\n")
        # Marca o link para ser clicável
        url_inicio = text_resultado.index(tk.END + "-2 lines")
        url_fim = text_resultado.index(tk.END)
        text_resultado.tag_add("url", url_inicio, url_fim)


# Ativa a função exibir_produtos ao clicar no botão
button_buscar.config(command=exibir_produtos)

# Associa a ação de clicar nas URLs à função abrir_url
text_resultado.tag_bind("url", "<Button-1>", abrir_url)

root.config(bg="#120a8f")  # Azul marinho: #120a8f

# Define as dimensões da janela
largura_janela = 400
altura_janela = 300
largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()
pos_x = (largura_tela // 2) - (largura_janela // 2)
pos_y = (altura_tela // 2) - (altura_janela // 2)
root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

root.mainloop()

