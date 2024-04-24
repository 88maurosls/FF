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
                st.error("No 'application/ld+json' script found in the HTML content.")
                return []
        else:
            st.error(f"HTTP Error: {res.status_code}")
            return []
    except Exception as e:
        st.error(f"Error retrieving images from URL: {str(e)}")
        return []

def download_image(url):
    response = requests.get(url)
    if url.lower().endswith('.webp'):
        # Convert from webp to jpg only when needed
        image = Image.open(io.BytesIO(response.content))
        image = image.convert('RGB')
        buf = io.BytesIO()
        image.save(buf, format='JPEG')
        buf.seek(0)
        return buf.getvalue(), 'image/jpeg'
    else:
        # Return original image bytes
        return response.content, response.headers['Content-Type']

def show_images(image_urls):
    if image_urls:
        for url in image_urls:
            st.image(url, width=100)  # Display image
            bytes_data, mime_type = download_image(url)  # Preparing for download without displaying
            file_name = url.split('/')[-1]
            if mime_type == 'image/webp':
                file_name = file_name.replace('.webp', '.jpg')  # Change file extension if webp
            # Display download button
            st.download_button(label="Convert & Download", data=bytes_data, file_name=file_name, mime=mime_type)
    else:
        st.write("No images found.")

codice = st.text_input("Insert Farfetch ID:", "")
if st.button("Download Images"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
