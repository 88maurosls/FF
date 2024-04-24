import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor
from rembg import remove
from PIL import Image
import io

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
    except requests.RequestException as e:
        st.error(f"Errore durante il tentativo di recupero delle immagini dall'URL: {str(e)}")
        return []

def convert_to_jpeg(image_data):
    # Converte i dati dell'immagine in formato JPEG
    with io.BytesIO(image_data) as f:
        f.seek(0)
        jpeg_data = f.getvalue()
    return jpeg_data

def show_images(image_urls):
    if image_urls:
        with ThreadPoolExecutor() as executor:
            futures = []
            for url in image_urls:
                futures.append(executor.submit(load_and_display_image, url))
            for future in futures:
                image_data = future.result()
                if image_data:
                    st.image(image_data, caption='Immagine', use_column_width=True)
    else:
        st.write("Nessuna immagine trovata.")

def load_and_display_image(url):
    try:
        image_data = requests.get(url).content
        jpeg_data = convert_to_jpeg(image_data)
        return jpeg_data
    except requests.RequestException as e:
        st.error(f"Errore durante il caricamento dell'immagine da {url}: {str(e)}")
        return None

codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
