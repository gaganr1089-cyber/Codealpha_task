// ==========================================
// ELEMENTS
// ==========================================

const inputText = document.getElementById("inputText");

const outputText = document.getElementById("outputText");

const sourceLanguage =
    document.getElementById("sourceLanguage");

const targetLanguage =
    document.getElementById("targetLanguage");

const translateButton =
    document.getElementById("translateButton");

const translateText =
    document.getElementById("translateText");

const characterCount =
    document.getElementById("characterCount");

const translationStatus =
    document.getElementById("translationStatus");

const clearButton =
    document.getElementById("clearButton");

const copyButton =
    document.getElementById("copyButton");

const speakButton =
    document.getElementById("speakButton");

const swapButton =
    document.getElementById("swapButton");


// ==========================================
// CHARACTER COUNTER
// ==========================================

inputText.addEventListener("input", () => {

    const length = inputText.value.length;

    characterCount.textContent =
        `${length} / 5000`;

});


// ==========================================
// TRANSLATE
// ==========================================

translateButton.addEventListener("click", translate);


async function translate() {

    const text = inputText.value.trim();

    const source = sourceLanguage.value;

    const target = targetLanguage.value;


    // Validate input

    if (!text) {

        showStatus(
            "Please enter some text first.",
            "error"
        );

        inputText.focus();

        return;
    }


    // Same language

    if (
        source !== "auto" &&
        source === target
    ) {

        outputText.value = text;

        showStatus(
            "Source and target languages are the same.",
            "success"
        );

        return;
    }


    // Loading state

    setLoading(true);


    try {

        /*
         * IMPORTANT:
         *
         * The frontend communicates with Flask.
         *
         * Flask will communicate with
         * Google Cloud Translation API.
         */

        const response = await fetch(
            "http://127.0.0.1:5000/api/translate",
            {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    text: text,

                    source: source,

                    target: target

                })

            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Translation failed."
            );

        }


        // Display translation

        outputText.value =
            data.translation;


        showStatus(
            "Translation completed.",
            "success"
        );


    } catch (error) {

        console.error(
            "Translation error:",
            error
        );


        outputText.value = "";


        showStatus(
            "Unable to connect to translation server.",
            "error"
        );

    } finally {

        setLoading(false);

    }

}


// ==========================================
// LOADING STATE
// ==========================================

function setLoading(loading) {

    translateButton.disabled = loading;


    if (loading) {

        translateText.textContent =
            "Translating...";

        translationStatus.textContent =
            "Processing";

    } else {

        translateText.textContent =
            "Translate";

        translationStatus.textContent =
            "Ready";

    }

}


// ==========================================
// STATUS MESSAGE
// ==========================================

function showStatus(message, type) {

    translationStatus.textContent =
        message;


    if (type === "error") {

        translationStatus.style.color =
            "#dc2626";

    } else {

        translationStatus.style.color =
            "#16a34a";

    }

}


// ==========================================
// CLEAR
// ==========================================

clearButton.addEventListener("click", () => {

    inputText.value = "";

    outputText.value = "";

    characterCount.textContent =
        "0 / 5000";

    translationStatus.textContent =
        "Ready";

    translationStatus.style.color =
        "";

    inputText.focus();

});


// ==========================================
// COPY
// ==========================================

copyButton.addEventListener("click", async () => {

    const text =
        outputText.value.trim();


    if (!text) {

        showStatus(
            "Nothing to copy.",
            "error"
        );

        return;

    }


    try {

        await navigator.clipboard.writeText(text);


        showStatus(
            "Translation copied.",
            "success"
        );


    } catch (error) {

        console.error(error);

        showStatus(
            "Unable to copy translation.",
            "error"
        );

    }

});


// ==========================================
// TEXT TO SPEECH
// ==========================================

speakButton.addEventListener("click", () => {

    const text =
        outputText.value.trim();


    if (!text) {

        showStatus(
            "Nothing to speak.",
            "error"
        );

        return;

    }


    // Check browser support

    if (!("speechSynthesis" in window)) {

        showStatus(
            "Text-to-speech is not supported.",
            "error"
        );

        return;

    }


    window.speechSynthesis.cancel();


    const speech =
        new SpeechSynthesisUtterance(text);


    speech.lang =
        getSpeechLanguage(targetLanguage.value);


    window.speechSynthesis.speak(speech);

});


// ==========================================
// SPEECH LANGUAGE
// ==========================================

function getSpeechLanguage(language) {

    const languages = {

        en: "en-US",

        hi: "hi-IN",

        kn: "kn-IN",

        ta: "ta-IN",

        te: "te-IN",

        ml: "ml-IN",

        fr: "fr-FR",

        de: "de-DE",

        es: "es-ES",

        it: "it-IT",

        pt: "pt-PT",

        ja: "ja-JP",

        ko: "ko-KR",

        zh: "zh-CN"

    };


    return languages[language] || "en-US";

}


// ==========================================
// SWAP LANGUAGES
// ==========================================

swapButton.addEventListener("click", () => {

    // Can't swap auto-detection

    if (sourceLanguage.value === "auto") {

        showStatus(
            "Choose a source language before swapping.",
            "error"
        );

        return;

    }


    const oldSource =
        sourceLanguage.value;


    sourceLanguage.value =
        targetLanguage.value;


    targetLanguage.value =
        oldSource;


    // Swap text as well

    const oldText =
        inputText.value;


    inputText.value =
        outputText.value;


    outputText.value =
        oldText;


    // Update character count

    characterCount.textContent =
        `${inputText.value.length} / 5000`;


    showStatus(
        "Languages swapped.",
        "success"
    );

});