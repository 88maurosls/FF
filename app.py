import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from PIL import Image
from io import BytesIO

@st.cache_resource
def get_images_from_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, 'html.parser')
        script_data = soup.find('script', type='application/ld+json')
        if script_data:
            data = json.loads(script_data.text)
            images = data.get('image')
            if images:
                return images if isinstance(images, list) else [images]
        else:
            st.error("Nessun script di tipo 'application/ld+json' trovato nel contenuto HTML.")
    else:
        st.error(f"Errore HTTP: {res.status_code}")
    return []


def show_images(images):
    if images:
        for img in images:
            if isinstance(img, dict):
                img_url = img.get('contentUrl')
                st.image(img_url, width=100, caption=img_url)
    else:
        st.write("Nessuna immagine trovata.")

def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img.save(f'temp_image.png')
        with open('temp_image.png', "rb") as file:
            st.download_button(
                label="Download Image",
                data=file,
                file_name='downloaded_image.png',
                mime="image/png"
            )

codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        images = get_images_from_url(url)
        show_images(images)
        if st.button("Download Selected Image"):
            for image in images:
                if isinstance(image, dict):
                    img_url = image.get('contentUrl')
                    download_image(img_url)
