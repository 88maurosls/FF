import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os
import urllib.request
import base64

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
                st.error("Nessun script di tipo 'application/ld+json' trovato nel contenuto HTML.")
                return []
        else:
            st.error(f"Errore HTTP: {res.status_code}")
            return []
    except Exception as e:
        st.error(f"Errore durante il tentativo di recupero delle immagini dall'URL: {str(e)}")
        return []

def main():
    st.title("Downloader di Immagini da Farfetch")
    codice = st.text_input("Inserisci l'ID Farfetch:", "")
    if st.button("Scarica Immagini"):
        if codice:
            url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
            image_urls = get_images_from_url(url)
            if image_urls:
                for i, url in enumerate(image_urls, start=1):
                    st.write(f"Immagine {i}:")
                    st.image(url, use_column_width=True)
                    download_button_label = f"Scarica Immagine {i}"
                    download_image(url, download_button_label)

def download_image(url, button_label):
    image_content = urllib.request.urlopen(url).read()
    base64_image = base64.b64encode(image_content).decode('utf-8')
    href = f'<a href="data:image/jpeg;base64,{base64_image}" download="{os.path.basename(url)}">{button_label}</a>'
    st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
