import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurazione della sessione globale di requests
session = requests.Session()
retries = requests.packages.urllib3.util.retry.Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))
session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))

def get_images_from_url(url):
    res = session.get(url, headers={'user-agent': 'some agent'})
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
        st.write("Nessun elemento script trovato.")
        return []

def download_image(url):
    try:
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            filename = url.split('/')[-1]
            filepath = os.path.join("static", filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath
        else:
            st.write(f"Errore durante il download di {url}: Codice di stato {response.status_code}")
            return None
    except Exception as e:
        st.write(f"Errore durante il download di {url}: {e}")
        return None

def download_images(image_urls):
    saved_paths = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(download_image, url): url for url in image_urls}
        for future in as_completed(future_to_url):
            result = future.result()
            if result:
                saved_paths.append(result)
    return saved_paths

codice = st.text_input("ID Farfetch:", "")
if st.button("Scarica Immagini"):
    if codice:
        url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
        image_urls = get_images_from_url(url)
        saved_paths = download_images(image_urls)
        if saved_paths:
            for path in saved_paths:
                st.image(path, width=100)

