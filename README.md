# NumPy Photo Editor

A local photo editor built with NumPy and Streamlit.

I created this project to learn NumPy through practical image processing.

## Features

- Upload PNG, JPEG, and WebP images
- Adjust brightness
- Convert images to grayscale
- Crop images
- Compare original and edited versions
- Download the result as a PNG

## Getting Started

Tested with Python 3.12.

Open a terminal in the project folder and run:

```powershell
.\Baslat.bat
```

The launcher creates a virtual environment and installs dependencies on the first run.

Open in your browser:

http://127.0.0.1:8501

Keep the terminal open while using the app.

## Project Structure

- `app.py` — interface, image loading, and downloads
- `islemler.py` — NumPy image processing functions
- `stil.css` — interface styling
- `requirements.txt` — dependencies
- `Baslat.bat` — Windows launcher

## Built With

Python · NumPy · Streamlit · Pillow

## Notes

Images are processed locally. The working image and exported PNG are resized to a maximum of 1600 pixels on the longest side.
