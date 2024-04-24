import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os
import urllib.request

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
        for url in image_urls:
            image = urllib.request.urlopen(url).read()
            st.image(image, width=100, caption=f"Immagine: {url}")
            if st.button("Scarica", key=url):
                download_image(url)
    else:
        st.write("Nessuna immagine trovata.")

def download_image(url):
    try:
        image_name = os.path.basename(url)
        with urllib.request.urlopen(url) as response:
            with open(image_name, "wb") as out_file:
                out_file.write(response.read())
        st.success(f"Immagine scaricata con successo: {image_name}")
    except Exception as e:
        st.error(f"Errore durante il download dell'immagine: {str(e)}")

def main():
    st.title("Downloader di Immagini da Farfetch")
    codice = st.text_input("Inserisci l'ID Farfetch:", "")
    if st.button("Scarica Immagini"):
        if codice:
            url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
            image_urls = get_images_from_url(url)
            show_images(image_urls)

if __name__ == "__main__":
    main()
