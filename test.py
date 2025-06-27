from google import genai



if __name__ == "__main__":
    client = genai.Client(api_key="AIzaSyAKCQEreTKY8bew6cX3IN01wFOsosuDJUI")

    response = client.models.generate_content(
      model="gemini-2.0-flash", contents="用中文解释人工智能的基本原理"
    )
    print(response.text)