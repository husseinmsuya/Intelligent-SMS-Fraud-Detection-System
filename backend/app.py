from flask import Flask, render_template, request
import pickle
import nltk
import re
import os
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

# Download NLTK data on startup (needed on Render)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)

# Paths relative to backend/app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "..", "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "..", "frontend", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

with open(os.path.join(BASE_DIR, "spam", "spam_model.pkl"), "rb") as f:
    model = pickle.load(f)
with open(os.path.join(BASE_DIR, "tfidf", "tfidf_vectorizer.pkl"), "rb") as f:
    tfidf = pickle.load(f)

stemmer = PorterStemmer()
stop_words = set(stopwords.words("english"))


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    tokens = nltk.word_tokenize(text)
    tokens = [w for w in tokens if w not in stop_words]
    tokens = [stemmer.stem(w) for w in tokens]
    return " ".join(tokens)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    message = request.form.get("message", "").strip()
    if not message:
        return render_template(
            "index.html",
            error="Please enter a message before running analysis.",
        )
    cleaned = clean_text(message)
    vectorized = tfidf.transform([cleaned])
    result = model.predict(vectorized)[0]
    proba = model.predict_proba(vectorized)
    confidence = round(max(proba[0]) * 100, 2)
    label = "Spam" if str(result).lower() == "spam" or result == 1 else "Safe"
    risk_level = "High risk" if label == "Spam" else "Low risk"
    return render_template(
        "index.html",
        result=result,
        label=label,
        risk_level=risk_level,
        confidence=confidence,
        message=message,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
