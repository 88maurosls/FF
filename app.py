import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os

# Assicurati che la cartella per le immagini esista
os.makedirs('downloaded_images', exist_ok=True)

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

def download_image(url):
    filename = url.split('/')[-1]
    filepath = os.path.join('downloaded_images', filename)
    if not os.path.exists(filepath):  # Evita il re-download se già esiste
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    return filepath

def show_images(image_urls):
    if image_urls:
        for url in image_urls:
            st.image(url, width=100)
            download_path = download_image(url)  # Scarica l'immagine
            st.download_button(label="Scarica", data=open(download_path, "rb"), file_name=os.path.basename(download_path), mime='image/jpeg')
    else:
        st.write("Nessuna immagine trovata.")

codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
