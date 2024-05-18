# Projet de Fin d'études (Final Year Project)

# Music Sheet Recognition and Playback (MSRP)

---

## Purpose
MSRP is an application designed to recognize music sheets from input images, process them, and play the music as audio. Additionally, it provides functionality to save the played music as an MP3 file. This application aims to simplify the process of converting music sheets into playable audio, facilitating musicians in learning, practicing, and sharing music.

---

## Getting Started
To set up and run MSRP locally on your machine, follow these steps:

### 1. Clone the Repository
```bash
git clone https://github.com/paul-tohme98/msrp-backend.git
git pull
git checkout develop
````

### 2. Create a Virtual Environment
Navigate to the project directory and create a virtual environment named msrp-venv:
```bash
cd msrp
python -m venv msrp-venv
```
### 3. Activate the Virtual Environment
On Windows:
```bash
.\msrp-venv\Scripts\activate
```
On macOS/Linux:
```bash
source msrp-venv/bin/activate
```
### 4. Install Requirements
Install the required packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```
### 5. Run the Application
Run the BackendMain.py file to start the application:
```bash
python BackendMain.py
```

---

## Usage

Once the application is running, follow these steps to use MSRP:

1. **Upload Music Sheet Image**:
   Upload an image containing the music sheet you want to process.

2. **Process and Playback**:
   Process the uploaded image to recognize the music and playback the audio.

3. **Save as MP3**:
   Optionally, save the played music as an MP3 file for future use.
 image containing the music sheet you want to process.

---

## Contributing

Contributions to MSRP are welcome! If you encounter any bugs, have suggestions for improvements, or would like to contribute new features, feel free to open an issue or submit a pull request on GitHub.

Links I found useful while developing this project :

https://github.com/aashrafh/Mozart

https://github.com/cal-pratt/SheetVision/tree/master

https://github.com/OMR-Research/tf-end-to-end/blob/master/ctc_training.py

---

## License

This project is licensed under the MIT License. Feel free to use and modify the code for your own purposes.

---
