import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from PIL import Image
import io

# Funzione per scaricare e memorizzare in cache le immagini
@st.cache(allow_output_mutation=True, suppress_st_warning=True, max_entries=20, ttl=3600)
def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            return image
        else:
            st.warning(f"Errore durante il download dell'immagine: {response.status_code}")
            return None
    except Exception as e:
        st.warning(f"Errore durante il download dell'immagine: {str(e)}")
        return None

# Funzione per convertire le immagini in formato JPEG
def convert_to_jpeg(image):
    with io.BytesIO() as output:
        image.save(output, format="JPEG")
        jpeg_data = output.getvalue()
    return Image.open(io.BytesIO(jpeg_data))

# Funzione per ottenere le immagini dall'URL
@st.cache(allow_output_mutation=True, suppress_st_warning=True, max_entries=10, ttl=3600)
def get_images_from_url(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            script_data = soup.find('script', type='application/ld+json')
            if script_data:
                data = json.loads(script_data.text)
                images = data.get('image')
                image_urls = []
                if
