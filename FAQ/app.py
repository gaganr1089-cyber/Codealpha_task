from flask import Flask, render_template, request, jsonify
import json
import re
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================
# FLASK APPLICATION
# ==========================================

app = Flask(__name__)


# ==========================================
# DOWNLOAD NLTK DATA
# ==========================================

nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")


# ==========================================
# LOAD FAQ DATA
# ==========================================

try:
    with open("faq_data.json", "r", encoding="utf-8") as file:
        faq_data = json.load(file)

    print("======================================")
    print("FAQ DATA LOADED SUCCESSFULLY")
    print("Number of FAQs:", len(faq_data))
    print("======================================")

except Exception as e:
    print("======================================")
    print("ERROR LOADING FAQ DATA")
    print("Error:", e)
    print("======================================")

    faq_data = []


# ==========================================
# STOPWORDS
# ==========================================

stop_words = set(
    stopwords.words("english")
)


# ==========================================
# TEXT PREPROCESSING
# ==========================================

def preprocess(text):

    # Convert to lowercase
    text = text.lower()

    # Remove punctuation
    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        "",
        text
    )

    # Tokenize
    tokens = word_tokenize(text)

    # Remove stopwords
    tokens = [
        word
        for word in tokens
        if word not in stop_words
    ]

    # Return processed sentence
    return " ".join(tokens)


# ==========================================
# PREPROCESS ALL QUESTION VARIATIONS
# ==========================================

processed_questions = []

# Connect each question variation
# to its original FAQ
question_to_faq = []


for faq in faq_data:

    for question in faq["questions"]:

        processed_question = preprocess(
            question
        )

        processed_questions.append(
            processed_question
        )

        question_to_faq.append(
            faq
        )


# ==========================================
# CREATE TF-IDF MODEL
# ==========================================

if processed_questions:

    vectorizer = TfidfVectorizer()

    faq_vectors = vectorizer.fit_transform(
        processed_questions
    )

    print(
        "Total question variations:",
        len(processed_questions)
    )

    print(
        "TF-IDF model created successfully."
    )

else:

    vectorizer = None
    faq_vectors = None

    print(
        "WARNING: No questions found."
    )


# ==========================================
# FIND BEST ANSWER
# ==========================================

def get_answer(user_question):

    if not faq_data:
        return "The FAQ database is empty."

    if vectorizer is None:
        return "The FAQ system is not initialized."

    # Preprocess user question
    processed_question = preprocess(
        user_question
    )

    # Convert user question into TF-IDF vector
    user_vector = vectorizer.transform(
        [processed_question]
    )

    # Calculate cosine similarity
    similarity_scores = cosine_similarity(
        user_vector,
        faq_vectors
    )

    # Find highest similarity
    best_match_index = (
        similarity_scores.argmax()
    )

    # Get score
    best_score = similarity_scores[
        0
    ][best_match_index]

    # Get matching FAQ
    best_faq = question_to_faq[
        best_match_index
    ]

    # Display information in terminal
    print("--------------------------------------")
    print("User question:", user_question)
    print(
        "Similarity score:",
        round(best_score, 3)
    )

    # Confidence threshold
    if best_score < 0.25:

        return (
            "Sorry, I could not find a "
            "suitable answer to your question."
        )

    # Return FAQ answer
    return best_faq["answer"]


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================================
# ASK QUESTION
# ==========================================

@app.route("/ask", methods=["POST"])
def ask():

    try:

        # Receive JSON from browser
        data = request.get_json()

        print("--------------------------------------")
        print("Received data:", data)

        # Check data
        if not data:

            return jsonify({
                "answer": "No question was received."
            }), 400

        # Get question
        user_question = data.get(
            "question",
            ""
        ).strip()

        # Check empty question
        if not user_question:

            return jsonify({
                "answer": "Please enter a question."
            }), 400

        # Find answer
        answer = get_answer(
            user_question
        )

        print("Answer:", answer)

        # Send answer to browser
        return jsonify({
            "answer": answer
        })

    except Exception as e:

        print("--------------------------------------")
        print("ERROR IN /ask")
        print("Error:", e)

        return jsonify({
            "answer": (
                "An error occurred while "
                "processing your question."
            )
        }), 500


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    print()
    print("======================================")
    print("          FAQ AI CHATBOT")
    print("======================================")
    print("NLP: NLTK")
    print("Model: TF-IDF")
    print("Similarity: Cosine Similarity")
    print("FAQ count:", len(faq_data))
    print("======================================")
    print()
    print(
        "Open: http://127.0.0.1:5000"
    )
    print()
    
    app.run(
        debug=True
    )