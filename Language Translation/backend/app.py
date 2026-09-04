from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

import os
import requests


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# CREATE FLASK APPLICATION
# ==========================================

app = Flask(__name__)


# Allow frontend to communicate with Flask

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*"
        }
    }
)


# ==========================================
# GOOGLE TRANSLATION API
# ==========================================

GOOGLE_API_KEY = os.getenv(
    "GOOGLE_TRANSLATE_API_KEY"
)

GOOGLE_TRANSLATE_URL = (
    "https://translation.googleapis.com/"
    "language/translate/v2"
)


# ==========================================
# CHECK API KEY
# ==========================================

if not GOOGLE_API_KEY:

    print(
        "WARNING: GOOGLE_TRANSLATE_API_KEY "
        "is not configured."
    )


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "message": "Language Translation API is running",
        "service": "LinguaTranslate",
        "version": "1.0"
    })


# ==========================================
# API HEALTH CHECK
# ==========================================

@app.route("/api/health", methods=["GET"])
def health():

    api_configured = bool(
        GOOGLE_API_KEY
    )

    return jsonify({

        "success": True,

        "backend": "running",

        "translation_api_configured":
            api_configured

    })


# ==========================================
# TRANSLATION ENDPOINT
# ==========================================

@app.route(
    "/api/translate",
    methods=["POST"]
)
def translate():

    try:

        # ----------------------------------
        # Check API key
        # ----------------------------------

        if not GOOGLE_API_KEY:

            return jsonify({
                "success": False,
                "error":
                    "Google Translation API key "
                    "is not configured."
            }), 500


        # ----------------------------------
        # Get JSON request
        # ----------------------------------

        data = request.get_json()


        if not data:

            return jsonify({
                "success": False,
                "error":
                    "Request body is required."
            }), 400


        # ----------------------------------
        # Extract values
        # ----------------------------------

        text = data.get("text", "").strip()

        source = data.get(
            "source",
            "auto"
        )

        target = data.get(
            "target",
            "en"
        )


        # ----------------------------------
        # Validate text
        # ----------------------------------

        if not text:

            return jsonify({
                "success": False,
                "error":
                    "Text cannot be empty."
            }), 400


        # ----------------------------------
        # Character limit
        # ----------------------------------

        if len(text) > 5000:

            return jsonify({
                "success": False,
                "error":
                    "Text cannot exceed "
                    "5000 characters."
            }), 400


        # ----------------------------------
        # Validate target language
        # ----------------------------------

        allowed_languages = {

            "en",
            "hi",
            "kn",
            "ta",
            "te",
            "ml",
            "fr",
            "de",
            "es",
            "it",
            "pt",
            "ja",
            "ko",
            "zh"

        }


        if target not in allowed_languages:

            return jsonify({
                "success": False,
                "error":
                    "Unsupported target language."
            }), 400


        # ----------------------------------
        # Prepare Google API request
        # ----------------------------------

        payload = {

            "q": text,

            "target": target

        }


        # Google can detect the source
        # language when source = auto.

        if source != "auto":

            if source not in allowed_languages:

                return jsonify({
                    "success": False,
                    "error":
                        "Unsupported source language."
                }), 400

            payload["source"] = source


        # ----------------------------------
        # Send request to Google
        # ----------------------------------

        response = requests.post(

            GOOGLE_TRANSLATE_URL,

            params={
                "key": GOOGLE_API_KEY
            },

            json=payload,

            timeout=15

        )


        # ----------------------------------
        # Handle Google API errors
        # ----------------------------------

        if response.status_code != 200:

            try:

                google_error = response.json()

                error_message = (
                    google_error
                    .get("error", {})
                    .get(
                        "message",
                        "Google Translation API error."
                    )
                )

            except Exception:

                error_message = (
                    "Google Translation API "
                    "returned an error."
                )


            return jsonify({

                "success": False,

                "error": error_message

            }), response.status_code


        # ----------------------------------
        # Read Google response
        # ----------------------------------

        result = response.json()


        translations = (
            result
            .get("data", {})
            .get("translations", [])
        )


        if not translations:

            return jsonify({

                "success": False,

                "error":
                    "No translation was returned."

            }), 500


        translation = translations[0].get(
            "translatedText",
            ""
        )


        detected_language = translations[0].get(
            "detectedSourceLanguage",
            source
        )


        # ----------------------------------
        # Return result to frontend
        # ----------------------------------

        return jsonify({

            "success": True,

            "translation": translation,

            "source": detected_language,

            "target": target

        })


    except requests.exceptions.Timeout:

        return jsonify({

            "success": False,

            "error":
                "Translation service timed out."

        }), 504


    except requests.exceptions.RequestException:

        return jsonify({

            "success": False,

            "error":
                "Could not connect to Google "
                "Translation API."

        }), 502


    except Exception as error:

        print(
            "Unexpected error:",
            error
        )


        return jsonify({

            "success": False,

            "error":
                "An unexpected server error occurred."

        }), 500


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )
    