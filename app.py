import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os

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

def download_image(image_url):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            file_name = os.path.basename(image_url).split('?')[0] + ".jpg"
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            st.success(f"Immagine salvata: {file_name}")
        else:
            st.error(f"Errore HTTP {response.status_code} durante il download di {image_url}")
    except Exception as e:
        st.error(f"Non è stato possibile salvare l'immagine {image_url}: {str(e)}")

def show_images(image_urls):
    if image_urls:
        for url in image_urls:
            st.image(url, width=100)
            download_image(url)
    else:
        st.write("Nessuna immagine trovata.")

codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
