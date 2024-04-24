import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from PIL import Image
import io
from rembg import remove
import cv2

# Funzione per scaricare e memorizzare in cache le immagini
@st.cache(allow_output_mutation=True, suppress_st_warning=True, max_entries=20, ttl=3600)
def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            return image
        else:
            st.warning(f"Errore durante il download dell'immagine: {response.status_code}")
            return None
    except Exception as e:
        st.warning(f"Errore durante il download dell'immagine: {str(e)}")
        return None

# Funzione per convertire le immagini in formato JPEG utilizzando rembg
# Funzione per convertire le immagini in formato JPEG utilizzando rembg
# Funzione per convertire le immagini in formato JPEG utilizzando rembg
def convert_to_jpeg(image):
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        png_data = output.getvalue()
    # Carica l'immagine utilizzando OpenCV e salvala senza alcuna trasformazione
    img_np = cv2.imdecode(np.frombuffer(png_data, np.uint8), cv2.IMREAD_UNCHANGED)
    _, buf = cv2.imencode('.jpg', img_np)
    return Image.open(io.BytesIO(buf))



# Funzione per ottenere le immagini dall'URL
@st.cache(allow_output_mutation=True, suppress_st_warning=True, max_entries=10, ttl=3600)
def get_images_from_url(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
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
                st.warning("Nessun script di tipo 'application/ld+json' trovato nel contenuto HTML.")
                return []
        else:
            st.warning(f"Errore HTTP: {response.status_code}")
            return []
    except Exception as e:
        st.warning(f"Errore durante il recupero delle immagini dall'URL: {str(e)}")
        return []

# Funzione per visualizzare le immagini
def show_images(image_urls):
    if image_urls:
        for url in image_urls:
            st.subheader("Immagine")
            image = download_image(url)
            if image:
                jpeg_image = convert_to_jpeg(image)
                st.image(jpeg_image, use_column_width=True, caption='Immagine in formato JPEG')
    else:
        st.warning("Nessuna immagine trovata.")

# Funzione principale
def main():
    st.title("Scarica Immagini da Farfetch")

    codice = st.text_input("Inserisci l'ID Farfetch:", "")

    if st.button("Scarica Immagini"):
        if codice:
            url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
            image_urls = get_images_from_url(url)
            show_images(image_urls)

if __name__ == "__main__":
    main()
