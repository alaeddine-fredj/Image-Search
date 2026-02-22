# 🔍 Image Search and Save Web App

## 📌 Project Overview

This project is a **web application** built with **Flask** that allows users to search for images on the web, view them in a gallery, and save selected images locally along with their source URLs.

Key features:
- Search for images using a text query
- Display search results in a gallery format
- Select and save images with corresponding source URLs
- Headless browser automation using Selenium

---

## ⚙️ How It Works

### 1️⃣ Backend (Flask)
- `app.py` handles routes:
  - `/` → Homepage with search input
  - `/search` → Perform image search and display results
  - `/save_image` → Save selected image and source URL

- Images are stored in `static/saved_images`
- Sessions are used to track current search results and selection

### 2️⃣ Image Search (Selenium & Bing Images)
- Uses **Selenium WebDriver** (Edge) in headless mode
- Searches Bing Images for the query
- Fetches first 10 image URLs and their source URLs
- Converts images to PIL format for preview

### 3️⃣ Frontend

- **Homepage (`index.html`)**: Simple search input with a logo and submit button
- **Results Page (`results.html`)**:
  - Displays images in a carousel-like gallery
  - Allows user to select an image
  - Selected image can be saved with a click

- Uses HTML, CSS, and JavaScript for navigation and image selection

### 4️⃣ Save Functionality
- Saves the selected image as a `.jpg` file
- Saves the corresponding source URL as a `.txt` file
- Filenames are generated based on the search query
- Handles duplicate filenames by appending a counter

---

## 🛠️ Requirements

- Python 3.x
- Flask
- Selenium
- PIL / Pillow
- Requests

Install dependencies:

```bash
pip install flask selenium pillow requests
```

- **Edge WebDriver** must be installed and available in PATH
- Internet connection required for image search

---

## 🎯 Learning Objectives

- Build a full-stack web app with Flask
- Automate web tasks using Selenium
- Display and interact with images in a gallery format
- Save web data (images and URLs) locally
- Use sessions to store temporary data

---
