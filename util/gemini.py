import google.generativeai as genai
import os

def createModel():
  genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
  model = genai.GenerativeModel('gemini-1.5-flash')
  return model

def process_text(content):
  pass