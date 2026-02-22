from flask import Flask, render_template, request, redirect, url_for, session
from PIL import Image
from io import BytesIO
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import re
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

# Directory to save images
IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'static', 'saved_images')


def create_edge_driver():
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    driver = webdriver.Edge(options=options)
    driver.maximize_window()
    return driver


def perform_search(query):
    driver = create_edge_driver()
    driver.get(f'https://www.bing.com/images/search?q={query}')

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "iusc"))
        )
    except TimeoutException:
        print("Images did not load in time.")
        driver.quit()
        return [], [], []

    containers1 = driver.find_elements(By.CLASS_NAME, 'iusc')
    image_urls = []
    for container in containers1[:10]:  # Fetch source URLs corresponding to the first five images
        try:
            m_data = container.get_attribute('m')
            m_data_dict = json.loads(m_data)
            image_url = m_data_dict.get('murl')
            if image_url:
                image_urls.append(image_url)
        except Exception as e:
            print(f"An error occurred: {e}")

    containers2 = driver.find_elements(By.CLASS_NAME, 'lnkw')
    source_urls = []
    for container in containers2[:10]:  # Fetch source URLs corresponding to the first five images
        try:
            a_tag = container.find_element(By.TAG_NAME, 'a')
            href = a_tag.get_attribute('href')
            if href:
                source_urls.append(href)
        except Exception as e:
            print(f"An error occurred: {e}")

    images_display = []
    for url in image_urls:
        # Check if the URL is not None before making a request
        if url:
            try:
                response = requests.get(url, verify=False)  # Ignore SSL verification error
                if response.status_code == 200 and response.headers.get('content-type', '').startswith('image'):
                    img = Image.open(BytesIO(response.content))
                    images_display.append(img)
                else:
                    images_display.append(None)
            except Exception as e:
                print(f"An error occurred while fetching image: {e}")
                images_display.append(None)
        else:
            images_display.append(None)  # Handle the case where the URL is None

    driver.quit()

    return image_urls, images_display, source_urls


def save_image(image_url, source_url, search_query):
    try:
        response = requests.get(image_url, verify=False)  # Ignore SSL verification error
        if response.status_code == 200:
            # Construct a valid filename from the search query
            filename_base = re.sub(r'[<>:"/\\|?*]', '', search_query)
            filename = f"{filename_base}.jpg"
            txt_filename = f"{filename_base}.txt"
            
            # Initialize counter and file paths
            count = 0
            image_path = os.path.join(IMAGE_DIR, filename)
            txt_path = os.path.join(IMAGE_DIR, txt_filename)

            # Append a number to the filename if it already exists
            while os.path.isfile(image_path) or os.path.isfile(txt_path):
                count += 1
                filename = f"{filename_base}{count}.jpg"
                txt_filename = f"{filename_base}{count}.txt"
                image_path = os.path.join(IMAGE_DIR, filename)
                txt_path = os.path.join(IMAGE_DIR, txt_filename)
            
            # Save the image and its source URL
            with open(image_path, 'wb') as f:
                f.write(response.content)
            with open(txt_path, 'w') as f:
                f.write(source_url)
    except Exception as e:
        print(f"An error occurred while saving image: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['search_query']
    image_urls, images_display, source_urls = perform_search(search_query)
    if not image_urls:
        return render_template('no_results.html')

    # Store the URLs in the session
    session['image_urls'] = image_urls
    session['source_urls'] = source_urls
    session['search_query'] = search_query  # Store the search query in session

    return render_template('result.html', image_urls=image_urls, images_display=images_display,
                           source_urls=source_urls)


@app.route('/save_image', methods=['POST'])
def save_image_route():
    selected_image_idx = int(request.form.get('selected_image'))
    image_urls = session.get('image_urls')
    source_urls = session.get('source_urls')
    search_query = session.get('search_query')  # Retrieve the search query from session

    if image_urls and source_urls and search_query:
        image_url = image_urls[selected_image_idx] if selected_image_idx < len(image_urls) else None
        source_url = source_urls[selected_image_idx] if selected_image_idx < len(source_urls) else None

        if image_url and source_url:
            # Save the selected image and its source URL with the search query
            save_image(image_url, source_url, search_query)
            return redirect(url_for('index'))

    return "Error: Selected image URL or source URL not found."


if __name__ == '__main__':
    app.run(debug=True)
