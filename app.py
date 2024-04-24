import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
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
    except Exception as e:
        st.error(f"Errore durante il tentativo di recupero delle immagini dall'URL: {str(e)}")
        return []

def convert_image_to_jpg(image_url):
    # Se l'URL contiene già .jpg, restituisci l'URL stesso
    if '.jpg' in image_url.lower():
        return image_url
    # Altrimenti, converti l'immagine in formato JPG e restituisci l'URL
    response = requests.get(image_url)
    image = Image.open(io.BytesIO(response.content))
    image_rgb = image.convert('RGB')  # Convert to RGB in case of alpha channel
    buffer = io.BytesIO()
    image_rgb.save(buffer, format='JPEG')
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
                st.image(jpg_url, caption="Convertita in JPG", width=100) # Mostra la vera immagine JPG
    else:
        st.write("Nessuna immagine trovata.")

codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
