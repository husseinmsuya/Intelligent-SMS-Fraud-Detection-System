from flask import Flask, render_template, request
import pickle
import nltk
import re
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

app = Flask(__name__)

with open("spam_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("tfidf_vectorizer.pkl", "rb") as f:
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
    app.run(debug=True)