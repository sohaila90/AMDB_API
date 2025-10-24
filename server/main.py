from flask import Flask, jsonify, request
from flask_cors import CORS
import requests, os
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_API_KEY}",
}

# Egypt + arabisk originalspråk, men ENGELSK tekst tilbake
DISCOVER_PARAMS = {
    "include_adult": "false",
    "include_video": "false",
    "language": "en-US",            # titler/overview på engelsk når tilgjengelig
    "page": 1,
    "sort_by": "popularity.desc",
    "with_origin_country": "EG",    # kun fra Egypt
    "with_original_language": "ar", # arabisk originalspråk
}

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/movies", methods=["GET", "POST"])
def movies():
    # For nå: uansett GET/POST -> returner Egypt-liste
    r = requests.get(
        "https://api.themoviedb.org/3/discover/movie",
        headers=headers,
        params=DISCOVER_PARAMS,
    )
    return jsonify(r.json()), r.status_code

if __name__ == "__main__":
    app.run(debug=True, port=8080)


# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import requests, os
# from dotenv import load_dotenv

# load_dotenv()
# TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# url = "https://api.themoviedb.org/3/discover/movie"

# TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# headers = {
#     "accept": "application/json",
#     "Authorization": f"Bearer {TMDB_API_KEY}"
#  }

# DISCOVER_PARAMS = {
#     "include_adult": "false",
#     "include_video": "false",
#     "language": "en-US",
#     "page": 1,
#     "region": "EG",
#     "sort_by": "popularity.desc",
#     "with_origin_country": "EG",
#     "with_original_language": "ar"
# }

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": '*'}})


# @app.route("/movies", methods=["POST", "GET"])
# def movies():
#     if request.method == "POST":
#         data = request.get_json() or {}
#         movie_title = (data.get("movie") or "").strip()

#         if not movie_title:
#             #tomt søk vis egyp filmer
#             r = requests.get("https://api.themoviedb.org/3/discover/movie",
#             headers=headers, params=DISCOVER_PARAMS)
#             return jsonify(r.json()), r.status_code
        
#         #søk etter film, behold bara arabiske fra egy
#         r = requests.get("https://api.themoviedb.org/3/search/movie",
#         headers=headers,
#         params={"query": movie_title,
#                 "include_adult": "false",
#                 "page": 1,
#                 "language": "en-US"
#                 })

#         data = r.json()

#         # data["results"] = [
#         #     m for m in data.get("results", [])
#         #     if m.get("original_language") == "ar"
#         # ]
#         return jsonify(data), r.status_code
    
#      # hvis GET (ikke POST)
#     r = requests.get("https://api.themoviedb.org/3/discover/movie",
#                      headers=headers, params=DISCOVER_PARAMS)
#     return jsonify(r.json()), r.status_code

# # response = requests.get("https://api.themoviedb.org/3/search/movie", headers=headers, params={"query": movie_title, "language": "ar-EGY"}).json()

# if __name__ == "__main__":
#     print("TMDB key found:")
#     app.run(debug=True, port=8080)