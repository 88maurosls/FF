import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from PIL import Image
import io

@st.cache(allow_output_mutation=True, show_spinner=False)
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

def show_images(image_urls):
    if image_urls:
        for url in image_urls:
            st.image(url, width=100)  # Display image
            # Use a placeholder to put the download button after the image is displayed
            download_placeholder = st.empty()
            download_placeholder.button("Convert & Download", key=url, on_click=handle_download, args=(download_placeholder, url))
    else:
        st.write("No images found.")

def handle_download(placeholder, url):
    # This function will be called when the user clicks "Convert & Download"
    placeholder.empty()  # Remove the button
    with st.spinner('Processing image...'):
        response = requests.get(url)
        image_data, mime_type = process_image(response.content, url)
        placeholder.download_button("Download Image", image_data, file_name=url.split('/')[-1], mime=mime_type)

def process_image(image_data, url):
    # Check if the image is webp and convert if necessary
    if '.webp' in url.lower():
        image = Image.open(io.BytesIO(image_data))
        image = image.convert('RGB')
        buf = io.BytesIO()
        image.save(buf, format='JPEG')
        buf.seek(0)
        return buf.getvalue(), 'image/jpeg'
    else:
        return image_data, 'image/png'  # Assume PNG if not JPEG or WEBP

codice = st.text_input("Insert Farfetch ID:", "")
if st.button("Search Images"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
