import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from PIL import Image
import io

session = requests.Session()  # Usare una sessione persistente per le richieste HTTP

@st.cache(allow_output_mutation=True, show_spinner=False)
def get_images_from_url(url):
    res = session.get(url, headers={'user-agent': 'some agent'})
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

def handle_conversion(url):
    response = session.get(url)
    image_data, content_type = response.content, response.headers.get('Content-Type', '')
    if 'image/webp' in content_type:
        image = Image.open(io.BytesIO(image_data))
        image = image.convert('RGB')
        buf = io.BytesIO()
        image.save(buf, format='JPEG')
        buf.seek(0)
        image_data = buf.getvalue()
        content_type = 'image/jpeg'
    return image_data, content_type, url.split('/')[-1].replace('.webp', '.jpg')

def show_images(image_urls):
    if image_urls:
        for url in image_urls:
            st.image(url, width=100)  # Display image
            btn_key = f"btn_{url}"
            if st.button("Convert & Download", key=btn_key):
                # Store the URL in session state on button click
                st.session_state['download_url'] = url
                st.session_state['button_clicked'] = btn_key

    # Check if a download has been triggered
    if 'button_clicked' in st.session_state and st.session_state['button_clicked']:
        image_data, mime_type, file_name = handle_conversion(st.session_state['download_url'])
        st.download_button(
            label="Download Image",
            data=image_data,
            file_name=file_name,
            mime=mime_type,
            key='download' + st.session_state['button_clicked']
        )
        # Reset the state
        del st.session_state['button_clicked']

codice = st.text_input("Insert Farfetch ID:", "")
if st.button("Search Images"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        show_images(image_urls)
