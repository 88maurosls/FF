import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os
from PIL import Image
from io import BytesIO

@st.cache(allow_output_mutation=True)
def get_images_from_url(url):
    try:
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
                                image_urls.append(img.get('contentUrl'))
                    else:
                        if isinstance(images, dict):
                            image_urls.append(images.get('contentUrl'))
                return image_urls
            else:
                st.error("Nessun script di tipo 'application/ld+json' trovato nel contenuto HTML.")
                return []
        else:
            st.error(f"Errore HTTP: {res.status_code}")
            return []
    except Exception as e:
        st.error(f"Errore durante il tentativo di recupero delle immagini dall'URL: {str(e)}")
        return []

def show_images(image_urls):
    if image_urls:
        for i, url in enumerate(image_urls):
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            img.save(f'image_{i}.png')
            st.image(url, width=100)
    else:
        st.write("Nessuna immagine trovata.")

def download_images(image_urls):
    if image_urls:
        for i, url in enumerate(image_urls):
            with open(f'image_{i}.png', "rb") as file:
                btn = st.download_button(
                    label="Download Image",
                    data=file,
                    file_name=f'image_{i}.png',
                    mime="image/png"
                )
    else:
        st.write("Nessuna immagine disponibile per il download.")

codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
        download_images(image_urls)
