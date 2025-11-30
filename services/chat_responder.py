
import os
import logging
import json
import time

from kivy.app import App
from services.image_processor import ImageProcessor

processor = ImageProcessor(
    checkpoint_path="models/best_model_for_inference.pth",
    arch="resnet50",
    img_size=224
)

def classify_selected_image() -> str:
    try:
        app = App.get_running_app()
    except Exception:
        return "App not running."

    if app is None:
        return "App not running."

    img_path = getattr(app, "selected_image_path", None)
    if not img_path:
        return "No image selected."

    try:
        return processor.predict(img_path)
    except Exception as e:
        logging.exception("Image prediction failed.")
        return "Image analysis unavailable."


import logging
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO)

client = genai.Client()


def get_random_reply(
    user_text: str,
    *,
    temperature: float = 0.2,
    max_output_tokens: int = 2048
) -> str:


    try:
        image_info = classify_selected_image().strip()
    except Exception:
        logging.exception("Failed to call classify_selected_image()")
        image_info = "Image analysis unavailable."

    system_instructions = (
        "You are a careful, compassionate general-practice doctor. "
        "You ONLY provide general information and safe home-aid tips, "
        "NOT prescriptions, NOT drug dosages, and NOT definitive diagnoses.\n\n"
        "Always include:\n"
        "1) Possible causes (only possibilities, never definitive)\n"
        "2) Simple safe home-care steps\n"
        "3) Red-flag symptoms that require urgent medical care\n"
        "4) What the patient should do next / which doctor to visit\n\n"
        "If image information is provided, use it only as hints, never as proof."
        "Don't act as a AI but a professional doctor"
    )

    prompt = (
        "Patient description / question:"
        f"{user_text.strip()}"
        "Image analysis result:"
        f"{image_info}"
        "Now respond following the above medical safety rules."
    )

    print(prompt)
    try:
        gen_config = types.GenerateContentConfig(
            system_instruction=system_instructions,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=gen_config,
        )


        def extract_gemini_text(response):
            try:
                if getattr(response, "text", None):
                    return response.text.strip()
            except Exception:
                pass

            try:
                candidates = getattr(response, "candidates", None)
                if not candidates:
                    return ""

                for candidate in candidates:
                    content = getattr(candidate, "content", None)
                    if not content:
                        continue

                    parts = getattr(content, "parts", None)
                    if not parts:
                        continue

                    for part in parts:
                        # Each part may contain 'text'
                        text = getattr(part, "text", None)
                        if text:
                            return text.strip()
            except Exception as e:
                logging.error(f"Gemini nested extract failed: {e}")

            return ""

        final_text = extract_gemini_text(response)

    except Exception as e:
        logging.exception("Gemini API request failed.")
        return "Unable to generate response at the moment. Please try again later."

    if final_text:
        final_text += (
            "\n\n---\n"
            "**Medical disclaimer:** This information is for general guidance only "
            "and is NOT a substitute for professional medical advice, diagnosis, or treatment. "
            "If symptoms worsen or you notice any red-flag signs, seek a doctor immediately."
        )

    return final_text
