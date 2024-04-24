import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from PIL import Image
import io

# Gestione della sessione HTTP per ottimizzare le richieste
session = requests.Session()

@st.cache(allow_output_mutation=True)
def get_images_from_url(url):
    try:
        res = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
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

def convert_image(image_data):
    image = Image.open(io.BytesIO(image_data))
    if image.format == 'WEBP':
        image = image.convert('RGB')
        buf = io.BytesIO()
        image.save(buf, format='JPEG')
        buf.seek(0)
        return buf.getvalue(), 'image/jpeg'
    else:
        return image_data, 'image/png'

def show_images(image_urls):
    if image_urls:
        for url in image_urls:
            st.image(url, width=300)
            if st.button("Convert & Download", key=url):
                with st.spinner('Processing image...'):
                    response = session.get(url)
                    image_data, content_type = convert_image(response.content)
                    mime_type = 'image/jpeg' if 'jpeg' in content_type else 'image/png'
                    file_name = url.split('/')[-1].replace('.webp', '.jpg') if 'webp' in content_type else url.split('/')[-1]
                    st.download_button("Download Image", image_data, file_name=file_name, mime=mime_type)
    else:
        st.write("No images found.")

codice = st.text_input("Enter Farfetch ID:", "")
if st.button("Search Images"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
