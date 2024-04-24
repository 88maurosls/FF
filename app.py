import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

def get_images_from_url(url):
    res = requests.get(url, headers={'user-agent': 'some agent'})
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, 'html.parser')
        script_data = soup.find('script', type='application/ld+json')
        if script_data:
            data = json.loads(script_data.text)
            images = data.get('image')
            image_urls = []
            if images:
                if isinstance(images, list):
                    for img in images:
                        if isinstance(img, dict):
                            image_url = img.get('contentUrl')
                            if image_url:
                                image_urls.append(image_url)
                else:
                    if isinstance(images, dict):
                        image_url = images.get('contentUrl')
                        if image_url:
                            image_urls.append(image_url)
            return image_urls
        else:
            st.error("Nessun script di tipo 'application/ld+json' trovato nel contenuto HTML.")
            return []
    else:
        st.error(f"Errore HTTP: {res.status_code}")
        return []

def show_images(image_urls):
    if image_urls:
        for url in image_urls:
            response = requests.head(url)
            if response.status_code == 200:
                st.image(url, width=100)
            else:
                st.write(f"Impossibile visualizzare l'immagine: {url}")
    else:
        st.write("Nessuna immagine trovata.")

codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
