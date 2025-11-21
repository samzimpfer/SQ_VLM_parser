from dotenv import load_dotenv
from openai import OpenAI
import os
from pdf2image import convert_from_path
from io import BytesIO


# Load prompt from file
def load_prompt(prompt_file="prompt.txt"):
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read().strip()


# Function to create a file with the Files API
def create_file(file_path):
  # Convert PDF to PNG in memory
  images = convert_from_path(file_path, poppler_path="/opt/homebrew/opt/poppler/bin")

  # Since all PDFs are one page, get the first (and only) image
  png_image = images[0]
  
  # Convert PIL Image to PNG bytes in memory
  png_bytes = BytesIO()
  png_image.save(png_bytes, format='PNG')
  png_bytes.seek(0)  # Reset to beginning of BytesIO object
  
  # Create file with the PNG bytes
  result = client.files.create(
      file=("image.png", png_bytes, "image/png"),
      purpose="vision",
  )
  return result.id


def request(prompt, file_id):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "file_id": file_id,
                    "detail": "high"
                },
            ],
        }],
    )
    return response


def analyze_image(file_id):
    return request(prompt, file_id)
    


# Initialize client
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Set constants
prompt = load_prompt()
file_path = "../data/J15951_S00756/J15951_S00756.pdf"

# Read file
print("Reading file...", flush=True)
file_id = create_file(file_path)
print("File ID: ", file_id, flush=True)

# Generate response
print("Generating response...", flush=True)
response = analyze_image(file_id)
print("Response: ", response.output_text, flush=True)