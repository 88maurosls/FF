import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import asyncio
import aiohttp

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

async def download_image(session, url, width=100):
    try:
        async with session.get(url) as response:
            image_content = await response.read()
            st.image(image_content, caption='Immagine', width=width)
    except Exception as e:
        st.error(f"Errore durante il download dell'immagine: {str(e)}")


async def download_images(image_urls, columns, width=100):
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, url, width) for url in image_urls]
        for task, column in zip(tasks, columns):
            await task
            with column:
                pass

def main():
    st.title("Downloader di Immagini da Farfetch")
    codice = st.text_input("Inserisci l'ID Farfetch:", "")
    if st.button("Scarica Immagini"):
        if codice:
            url = f'https://www.farfetch.com/shopping/item{codice}.aspx'
            image_urls = get_images_from_url(url)
            if image_urls:
                images_per_row = 3  # Numero di immagini per riga
                rows = [st.empty() for _ in range(len(image_urls) // images_per_row + 1)]
                for i, url in enumerate(image_urls):
                    row_index = i // images_per_row
                    with rows[row_index]:
                        st.image(url, caption=f"Immagine {i+1}", width=100)
            else:
                st.write("Nessuna immagine trovata.")

if __name__ == "__main__":
    main()



