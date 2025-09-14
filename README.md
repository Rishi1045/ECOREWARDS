# 🌱 ECOREWARDS

ECOREWARDS is a web application that encourages eco-friendly habits by rewarding users for sustainable actions.  
Users can log activities, earn eco-points, and track their contributions towards a greener planet.

---

## 🚀Features
- User authentication (login/signup)  
- Dashboard to view eco-points and rewards  
- Waste classification using CNN  
- Leaderboard to compare with other users  
- Chatbot assistant (powered by Gemini API)  
- Multi-waste detection(YOLOv8) (real-time & image upload)  

---

## 🛠 Tech Stack
- **Backend:** Flask, Python  
- **Frontend:** HTML, CSS, JavaScript  
- **Database:** MongoDB  
- **AI/ML:** YOLOv8, Keras, TensorFlow  
- **APIs:** Gemini API  

---

## ⚙️ Installation
```bash
# clone the repo
git clone https://github.com/Rishi1045/ECOREWARDS.git
cd ECOREWARDS

# setup virtual environment
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

# install dependencies
pip install -r requirements.txt

# run the app
python app.py
