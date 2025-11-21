import ollama
import os
from pdf2image import convert_from_path
from io import BytesIO
import json

# ------------------------------
# Configuration
# ------------------------------
PDF_PATH = "../data/J15951_S00756/J15951_S00756.pdf"
TEMP_IMAGE_PATH = "temp_page.png"
MODEL_NAME = "llava"  # You can switch to llava-phi3, moondream, llava:34b, etc.


# Load prompt from file
def load_prompt(prompt_file="prompt.txt"):
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read().strip()
        

def pdf_to_png(pdf_path: str, output_path: str):
    print("Converting PDF to PNG...")

    # macOS often uses poppler from Homebrew:
    # brew install poppler
    # Try common Homebrew locations (Apple Silicon first, then Intel)
    poppler_paths = [
        "/opt/homebrew/opt/poppler/bin",  # Apple Silicon Mac
        "/usr/local/opt/poppler/bin",     # Intel Mac
    ]
    
    poppler_path = None
    for path in poppler_paths:
        if os.path.exists(path):
            poppler_path = path
            break
    
    if poppler_path:
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
    else:
        # Fallback: try without specifying path (if poppler is in system PATH)
        images = convert_from_path(pdf_path)

    # Take only first page
    image = images[0]

    image.save(output_path, "PNG")
    print(f"Saved image to {output_path}")

    return output_path


# ------------------------------
# Call Ollama Vision Model
# ------------------------------

def run_ollama_vision(model: str, image_path: str, prompt: str):
    print("Sending image to Ollama model...")

    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [image_path]
            }
        ]
    )

    return response["message"]["content"]


# ------------------------------
# Main Execution
# ------------------------------

def main():
    prompt = load_prompt()

    # 1. Convert PDF → PNG
    image_path = pdf_to_png(PDF_PATH, TEMP_IMAGE_PATH)

    # 2. Run Ollama model
    raw_output = run_ollama_vision(MODEL_NAME, image_path, prompt)
    
    print("\nRaw model output:\n")
    print(raw_output)

    # 3. Try parsing JSON
    print("\nAttempting to parse JSON output...\n")

    try:
        data = json.loads(raw_output)
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("❌ Model returned invalid JSON. Here is the raw output:")
        print(raw_output)
        print("\nError:", e)


if __name__ == "__main__":
    main()
