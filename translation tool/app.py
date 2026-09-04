from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json()

        text = data.get("text", "").strip()
        source = data.get("source", "auto")
        target = data.get("target", "en")

        if not text:
            return jsonify({
                "error": "Please enter some text."
            }), 400

        # Auto-detect source language
        if source == "auto":
            source = "auto"

        translator = GoogleTranslator(
            source=source,
            target=target
        )

        translated_text = translator.translate(text)

        return jsonify({
            "translation": translated_text
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)