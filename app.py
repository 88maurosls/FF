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

# Funzione per convertire l'immagine in JPEG e codificarla in base64
def convert_and_encode_image(image_data):
    image = Image.open(io.BytesIO(image_data))
    if image.format == 'WEBP':
        image = image.convert('RGB')
    img_buffer = io.BytesIO()
    image.save(img_buffer, format="JPEG")
    encoded_image = base64.b64encode(img_buffer.getvalue()).decode()
    return encoded_image

# Interfaccia utente Streamlit
codice = st.text_input("Inserisci l'ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        for url in image_urls:
            st.image(url, width=300)
            if st.button("Convert & Download", key=url):
                with st.spinner('Processing image...'):
                    response = requests.get(url)
                    encoded_image = convert_and_encode_image(response.content)
                    href = f'<a href="data:image/jpeg;base64,{encoded_image}" download="image.jpg">Download Image</a>'
                    st.markdown(href, unsafe_allow_html=True)
