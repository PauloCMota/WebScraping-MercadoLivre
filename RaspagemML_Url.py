import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import tkinter as tk
from tkinter import PhotoImage
import webbrowser
import sys
import os


# Função para coletar os produtos de uma página
def coletar_produtos(soup):
    produtos = soup.find_all("div", class_="ui-search-result__wrapper")
    lista_produtos = []
    for produto in produtos:
        link_elem = produto.find("a")
        link_url = link_elem["href"] if link_elem else "Link não disponível"

        titulo_element = produto.find("a", class_="poly-component__title")
        titulo = titulo_element.text if titulo_element else "Título não disponível"

        preco_elem = produto.find("div", class_="poly-price__current")
        preco = preco_elem.text if preco_elem else "Preço não disponível"

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

        # Buscar link para próxima página
        next_button = soup.find("li", class_="andes-pagination__button--next")
        if next_button:
            next_link = next_button.find("a")
            if next_link and "href" in next_link.attrs:
                url_atual = next_link["href"]
            else:
                url_atual = None  # Finaliza o loop se não houver link
        else:
            url_atual = None  # Finaliza o loop se não houver próximo botão

    return lista_total_produtos


# Interface gráfica Tkinter
root = tk.Tk()
root.title("Mercado Livre Scraper")

# Configurações de cores
bg_color = "#FFE600"  # Amarelo do Mercado Livre
title_color = "#00387b"  # Azul do Mercado Livre

# Ajuste para carregar a imagem dependendo de o código estar sendo executado como script ou como executável
if getattr(sys, 'frozen', False):
    # Quando o script estiver congelado (executável)
    caminho_logo = os.path.join(sys._MEIPASS, 'mercado_livre_logo.png')
else:
    # Durante o desenvolvimento normal
    caminho_logo = 'mercado_livre_logo.png'

# Logotipo do Mercado Livre
logo_img = PhotoImage(file=caminho_logo)
label_logo = tk.Label(root, image=logo_img, bg=bg_color)
label_logo.grid(row=0, column=0, padx=(10, 0))

# Título com logo ao lado
label_titulo = tk.Label(root, text="Mercado Livre Scraper", font=("Arial", 18, "bold"), bg=bg_color, fg=title_color)
label_titulo.grid(row=0, column=1, pady=10)

# Campo de entrada e botão de busca
label_produto = tk.Label(root, text="Digite o produto:", bg=bg_color, fg=title_color)
label_produto.grid(row=1, column=0, columnspan=2)

entry_produto = tk.Entry(root, width=50)
entry_produto.grid(row=2, column=0, columnspan=2, pady=5)

button_buscar = tk.Button(root, text="Buscar", bg=title_color, fg="white", width=20)
button_buscar.grid(row=3, column=0, columnspan=2, pady=10)

# Área de resultado com scroll
frame_resultado = tk.Frame(root, bg=bg_color)
frame_resultado.grid(row=4, column=0, columnspan=2, pady=(10, 0))

scrollbar = tk.Scrollbar(frame_resultado)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_resultado = tk.Text(frame_resultado, yscrollcommand=scrollbar.set, wrap="word", width=100, height=25, bg="white")
text_resultado.pack()
scrollbar.config(command=text_resultado.yview)

# Função para abrir URL ao clicar
def abrir_url(event):
    index = text_resultado.index(tk.CURRENT)
    url = text_resultado.get(f"{index} linestart", f"{index} lineend").strip()
    if url.startswith("http"):
        webbrowser.open(url)


# Função para exibir os produtos ao clicar no botão
def exibir_produtos():
    produto = entry_produto.get()
    url_pesquisa = f"https://lista.mercadolivre.com.br/{quote(produto)}#D[A:{quote(produto)}]"

    lista_total_produtos = coletar_proximas_paginas(url_pesquisa)
    text_resultado.delete("1.0", tk.END)

    text_resultado.tag_config("preco", foreground="red")
    text_resultado.tag_config("url", foreground="blue", underline=True)

    for produto in lista_total_produtos:
        text_resultado.insert(tk.END, f"Titulo: {produto['titulo']}\n")

        preco_inicio = text_resultado.index(tk.END)
        text_resultado.insert(tk.END, f"Preço: {produto['preco']}\n")
        preco_fim = text_resultado.index(tk.END)
        text_resultado.tag_add("preco", preco_inicio, preco_fim)

        url_inicio = text_resultado.index(tk.END)
        text_resultado.insert(tk.END, f"{produto['link_url']}\n\n")
        url_fim = text_resultado.index(tk.END)
        text_resultado.tag_add("url", url_inicio, url_fim)


button_buscar.config(command=exibir_produtos)
text_resultado.tag_bind("url", "<Button-1>", abrir_url)

root.config(bg=bg_color)

root.geometry("600x500")
root.mainloop()
