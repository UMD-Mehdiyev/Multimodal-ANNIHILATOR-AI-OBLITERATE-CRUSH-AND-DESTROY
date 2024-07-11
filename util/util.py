import requests
import datetime
from firebase_admin import storage

def download_file(url):
  # Common extensions to search for (adjust as needed)
  common_extensions = [".pdf", ".png", ".jpg", ".jpeg", ".wav", ".doc", ".txt", ".json"]

  # Split the URL path based on delimiters (adjust based on URL structure)
  url_parts = url.split("/")[-1].split("?")

  # Extract the filename part (assuming query string is separate)
  filename = url_parts[0]

  # Search for common extensions in the filename
  for extension in common_extensions:
    if extension in filename:
      final_filename = filename
      break  # Stop searching after finding the first match
  else:
      # No matching extension found, use the original filename
      final_filename = filename

  # Download the file using requests
  try:
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for unsuccessful downloads

    with open(final_filename, 'wb') as f:
      for chunk in response.iter_content(1024):
        if chunk:  # Filter out keep-alive new chunks
          f.write(chunk)

    return True, final_filename
  except requests.exceptions.RequestException as e:
    print(f"Error downloading file: {e}")
    return False, None
  

def generate_signed_url(bucket_name, file_path, expires_in=3600):  # Expires in 1 hour
  bucket = storage.bucket(bucket_name)
  blob = bucket.blob(file_path)
  expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in)
  url = blob.generate_signed_url(expiration=expiration, method="GET")
  return url

def process(content):
    # TODO
    return f"Processing: {content}"