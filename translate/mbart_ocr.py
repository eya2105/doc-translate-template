import time
import tracemalloc
from mbart_model import model, tokenizer
from transformers import pipeline
from ..ocr.image_to_text import ImageToText
from fastapi import FastAPI
app = FastAPI() 
# Language detection pipeline
lang_detect_pipe = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection")

# Start measuring time and memory
start_time = time.time()
tracemalloc.start()

# Use OCR to extract text from image
ocr = ImageToText()
raw_text, corrected_text = ocr.process_image('Screenshot 2025-06-25 224812.png')
text = corrected_text

# Detect language
result = lang_detect_pipe(text, top_k=1, truncation=True)
detected_lang = result[0]['label']
print("Detected language:", detected_lang)

# Dynamically build mBART code
src_lang = f"{detected_lang}_IT" if detected_lang != "en" else "en_XX"

tokenizer.src_lang = src_lang
inputs = tokenizer(text, return_tensors="pt")
generated_tokens = model.generate(**inputs, forced_bos_token_id=tokenizer.lang_code_to_id["en_XX"])
translated = tokenizer.decode(generated_tokens[0], skip_special_tokens=True)

# Stop measuring memory and time
current, peak = tracemalloc.get_traced_memory()
end_time = time.time()
tracemalloc.stop()

print(translated)
print(f"Execution time: {end_time - start_time:.2f} seconds")
print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")