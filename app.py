import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from PIL import Image
import io

session = requests.Session()  # Usare una sessione persistente per le richieste HTTP

@st.cache(allow_output_mutation=True, show_spinner=False)
def get_images_from_url(url):
    try:
        res = session.get(url, headers={'user-agent': 'some agent'})
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
                st.error("No 'application/ld+json' script found in the HTML content.")
                return []
        else:
            st.error(f"HTTP Error: {res.status_code}")
            return []
    except Exception as e:
        st.error(f"Error retrieving images from URL: {str(e)}")
        return []

def download_image(url):
    response = session.get(url)
    return response.content, response.headers.get('Content-Type', '')

def convert_image(image_data, content_type):
    if 'image/webp' in content_type:
        image = Image.open(io.BytesIO(image_data))
        image = image.convert('RGB')
        buf = io.BytesIO()
        image.save(buf, format='JPEG', quality=85)  # Ridurre la qualità per file più piccoli
        buf.seek(0)
        return buf.getvalue(), 'image/jpeg'
    return image_data, content_type

def show_images(image_urls):
    if image_urls:
        for url in image_urls:
            st.image(url, width=100)  # Display image
            # Use a placeholder to put the download button after the image is displayed
            btn = st.button("Convert & Download", key=url)
            if btn:
                with st.spinner('Processing image...'):
                    image_data, mime_type = download_image(url)
                    converted_data, final_mime_type = convert_image(image_data, mime_type)
                    st.download_button("Download Image", converted_data, file_name=url.split('/')[-1], mime=final_mime_type)
    else:
        st.write("No images found.")

codice = st.text_input("Insert Farfetch ID:", "")
if st.button("Search Images"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
