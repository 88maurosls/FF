import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from PIL import Image
import io
import tempfile

# Funzione per ottenere le immagini dall'URL
@st.cache(allow_output_mutation=True)
def get_images_from_url(url):
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            script_data = soup.find('script', type='application/ld+json')
            if script_data:
                data = json.loads(script_data.text)
                images = data.get('image')
                image_urls = []
                if isinstance(images, list):
                    image_urls = [img['contentUrl'] if isinstance(img, dict) else img for img in images]
                elif isinstance(images, dict):
                    image_urls.append(images['contentUrl'])
                return image_urls
            else:
                st.error("No 'application/ld+json' script found in the HTML content.")
                return []
        else:
            st.error(f"HTTP Error: {res.status_code}")
            return []
    except Exception as e:
        st.error(f"Error retrieving images from URL: {str(e)}")
        return []

# Funzione per scaricare e salvare l'immagine come file JPEG temporaneo
def download_image_as_temp_jpg(image_url):
    try:
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content))
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        image.save(temp_file.name, "JPEG")
        return temp_file
    except Exception as e:
        st.error(f"Error downloading image: {str(e)}")
        return None

# Interfaccia utente Streamlit
codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        for idx, url in enumerate(image_urls, start=1):
            st.image(url, width=300, caption=f"Immagine {idx}")
            temp_file = download_image_as_temp_jpg(url)
            if temp_file is not None:
                st.markdown(f"<a href='{temp_file.name}' download>Scarica Immagine {idx}</a>", unsafe_allow_html=True)
