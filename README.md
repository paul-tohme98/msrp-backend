# 🎵 Music Sheet Recognition and Playback (MSRP)

A deep learning application that recognizes music sheets from images,
processes them, and plays the music as audio or exports it as MP3.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python, Flask |
| AI / ML | TensorFlow, Keras, OpenCV |
| Frontend | ReactJS |
| Audio | MP3 export |

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/paul-tohme98/msrp-backend.git
cd msrp-backend
git checkout develop
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv msrp-venv

# Windows
.\msrp-venv\Scripts\activate

# macOS/Linux
source msrp-venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python BackendMain.py
```

---

## 📖 Usage

1. **Upload** a music sheet image
2. **Process** — the model recognizes musical symbols
3. **Playback** — listen to the generated audio
4. **Export** — save as MP3 (optional)

---

## 🤖 How It Works

- A neural network trained with **TensorFlow/Keras** detects and
  classifies musical symbols from the input image
- **OpenCV** handles image preprocessing and symbol extraction
- The **Flask** API orchestrates the pipeline and serves the
  ReactJS frontend

---

## 📄 License

MIT License — free to use and modify.