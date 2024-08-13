import random

def obtener_url_aleatoria():
    with open("url.txt","r") as archivo:
        contenido = archivo.read()
    
    # Dividir el contenido en una lista de URLs
    urls = contenido.split(',')
    
    # Elegir una URL aleatoria
    url_aleatoria = random.choice(urls).strip()
    print
    return url_aleatoria