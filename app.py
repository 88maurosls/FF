import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from PIL import Image
import io
import os  # Aggiunta dell'importazione di os

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

def download_and_convert_image(image_url):
    try:
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content))
        file_name = os.path.basename(image_url).split('?')[0] + ".jpg"
        image.save(file_name, "JPEG")
        st.success(f"Immagine convertita e salvata come: {file_name}")
    except Exception as e:
        st.error(f"Non è stato possibile convertire o salvare l'immagine {image_url}: {str(e)}")

def show_images(image_urls):
    if image_urls:
        for url in image_urls:
            st.image(url, width=100)
            download_and_convert_image(url)
    else:
        st.write("Nessuna immagine trovata.")

codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
