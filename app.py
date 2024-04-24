import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import numpy as np
import cv2
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
    except Exception as e:
        st.error(f"Errore durante il tentativo di recupero delle immagini dall'URL: {str(e)}")
        return []

def convert_image_to_jpg(image_url):
    response = requests.get(image_url)
    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    buffer = io.BytesIO()
    cv2.imwrite(buffer, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    buffer.seek(0)
    return buffer

def show_images(image_urls):
    if image_urls:
        for url in image_urls:
            col1, col2 = st.columns(2)
            with col1:
                st.image(url, caption="Originale", width=100)
            with col2:
                jpg_url = convert_image_to_jpg(url)
                st.image(jpg_url, caption="Convertita in JPG", width=100)
    else:
        st.write("Nessuna immagine trovata.")

codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
