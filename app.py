import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from PIL import Image
import io
from urllib.parse import urlparse

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

def convert_and_show_images(image_urls):
    if image_urls:
        for url in image_urls:
            response = requests.get(url)
            image = Image.open(io.BytesIO(response.content))
            filename = urlparse(url).path.split('/')[-1].split('.')[0] + '.jpg'  # Estensione cambiata in '.jpg'
            if image.format == 'WEBP':
                image = image.convert('RGB')
                buf = io.BytesIO()
                image.save(buf, format='JPEG')
                st.image(buf.getvalue(), caption=filename)
            else:
                st.image(image, caption=filename)
    else:
        st.write("Nessuna immagine trovata.")

codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        convert_and_show_images(image_urls)
