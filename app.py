import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from PIL import Image
import io

@st.cache(allow_output_mutation=True, show_spinner=False)
def get_images_from_url(url):
    res = requests.get(url, headers={'user-agent': 'some agent'})
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, 'html.parser')
        script_data = soup.find('script', type='application/ld+json')
        if script_data:
            data = json.loads(script_data.text)
            images = data.get('image')
            return [img.get('contentUrl') if isinstance(img, dict) else img for img in images]
        else:
            st.error("No 'application/ld+json' script found in the HTML content.")
    else:
        st.error(f"HTTP Error: {res.status_code}")
    return []

def download_image(url):
    response = requests.get(url)
    return response.content, response.headers.get('Content-Type', '')

def convert_image(image_data, content_type):
    if 'image/webp' in content_type:
        image = Image.open(io.BytesIO(image_data))
        image = image.convert('RGB')
        buf = io.BytesIO()
        image.save(buf, format='JPEG')
        buf.seek(0)
        return buf.getvalue(), 'image/jpeg'
    return image_data, content_type

def show_images(image_urls):
    for url in image_urls:
        st.image(url, width=100)  # Display image
        btn = st.button("Convert & Download", key=url)
        if btn:
            # Process and show download button immediately when button is clicked
            with st.spinner('Processing image...'):
                image_data, content_type = download_image(url)
                converted_data, final_mime_type = convert_image(image_data, content_type)
                st.download_button("Download Image", converted_data, file_name=url.split('/')[-1], mime=final_mime_type)

codice = st.text_input("Insert Farfetch ID:", "")
if st.button("Search Images"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
