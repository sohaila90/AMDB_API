from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()
print("TMDB key found:", os.getenv("TMDB_API_KEY"))

url = "https://api.themoviedb.org/3/discover/movie"

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_API_KEY}"
 }

params = {
    "include_adult": "false",
    "include_video": "false",
    "language": "ar-EGY",
    "page": 1,
    "region": "EG",
    "sort_by": "popularity.desc",
    "with_origin_country": "EG",
    "with_original_language": "en"
}

response = requests.get(url, headers=headers, params=params)

print(response.text)
print(response.json)


original_title = response.json()['results'][2]['original_title']
print(original_title)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": '*'}})
apiKey = '47d3a098d06ebffba749d6fe35c2b95e'

@app.route("/movies", methods=["POST", "GET"])
def movies():
    if request.method == "POST":
        data = request.get_json()
        movie_title = data.get("movie")

        if not movie_title or not movie_title.strip():
            return jsonify({"error": "Missing movie title"}), 400
        
        response = requests.get("https://api.themoviedb.org/3/search/movie", headers=headers, params={"query": movie_title, "language": "ar-EGY"}).json()
            
        return jsonify(response)
        
    return jsonify({"message": "Backend fungerer!"})

if __name__ == "__main__":
    print("TMDB key found:", os.getenv("TMDB_API_KEY"))
    app.run(debug=True, port=8080)