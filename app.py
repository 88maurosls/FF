import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

@st.cache_data
def get_images_from_url(url):
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

def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        print(f"Errore durante il download dell'immagine: {str(e)}")
        return None

def show_images(image_urls):
    for url in image_urls:
        content = download_image(url)
        if content:
            st.image(content, use_column_width=True, caption=url)

def main():
    st.title("Downloader di Immagini da Farfetch")
    codice = st.text_input("Inserisci l'ID Farfetch:", "")
    if st.button("Scarica Immagini"):
        if codice:
            url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
            image_urls = get_images_from_url(url)
            if image_urls:
                show_images(image_urls)
            else:
                st.write("Nessuna immagine trovata.")

if __name__ == "__main__":
    main()
