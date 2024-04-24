import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from PIL import Image
import io
import base64

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

# Funzione per convertire l'immagine in base64
def convert_image(image_data):
    image = Image.open(io.BytesIO(image_data))
    if image.format == 'WEBP':
        image = image.convert('RGB')
    img_buffer = io.BytesIO()
    image.save(img_buffer, format="JPEG")
    return base64.b64encode(img_buffer.getvalue()).decode(), "image/jpeg"

# Funzione per visualizzare le immagini e fornire il link di download
def show_images(image_urls):
    for url in image_urls:
        st.image(url, width=300)
        if st.button("Convert & Download", key=url):
            with st.spinner('Processing image...'):
                response = requests.get(url)
                image_data, content_type = convert_image(response.content)
                encoded_image_data = f"data:{content_type};base64,{image_data}"
                st.markdown(f'<a href="{encoded_image_data}" download="image.jpg">Download Image</a>', unsafe_allow_html=True)

# Interfaccia utente Streamlit
codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
