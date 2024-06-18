import google.generativeai as genai

# Replace with your actual API key
API_KEY = ""


genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

summary = model.generate_content("text")
print(f"summary: {summary}")
print(f"summary text: {summary.text}")

