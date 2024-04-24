import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from webptools import dwebp

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

def convert_webp_to_jpg(image_url):
    try:
        # Download the WebP image
        response = requests.get(image_url)
        if response.status_code == 200:
            webp_data = response.content
            # Convert WebP to JPG
            jpg_data = dwebp(webp_data)
            return jpg_data
        else:
            st.error(f"Errore nel scaricare l'immagine WebP da {image_url}")
            return None
    except Exception as e:
        st.error(f"Errore durante la conversione dell'immagine WebP in JPG: {str(e)}")
        return None

def show_images(image_urls):
    if image_urls:
        for url in image_urls:
            jpg_data = convert_webp_to_jpg(url)
            if jpg_data:
                st.image(jpg_data, caption='Immagine convertita da WebP a JPG', width=100)
    else:
        st.write("Nessuna immagine trovata.")

codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
