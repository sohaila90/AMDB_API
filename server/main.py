from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=ar-EGY&page=1&region=Egypt&sort_by=popularity.desc&with_origin_country=EG&with_original_language=en"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0N2QzYTA5OGQwNmViZmZiYTc0OWQ2ZmUzNWMyYjk1ZSIsIm5iZiI6MTc2MDY4NjIwNi4wMjQ5OTk5LCJzdWIiOiI2OGYxZjA3ZWRkMGNlMmM3YzM3NGY2OTYiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.ZOd43cZenLcI1ElxSiuTe99LrSBcDOiVEd5hYTMdUqk"
 }

response = requests.get(url, headers=headers)

print(response.text)
print(response.json)


original_title = response.json()['results'][2]['original_title']
print(original_title)

app = Flask(__name__)
cors = CORS(app, origins='*')
# apiKey = ''

@app.route("/movies", methods=["POST", "GET"])
def movies():
    if request.method == "POST":
        movie = request.get_json()
        if movie and "movie" in movie: 
            response = requests.get(f'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=ar-EGY&page=1&sort_by=popularity.desc&with_origin_country=EG&with_original_language=ar{movie}&appid={apiKey}&units=metrics').json()
            if response:
                return jsonify(response)
        else:
            return jsonify("Invalid data recived"), 400

    return jsonify("Funker du flasky?")

if __name__ == "__main__":
    app.run(debug=True, port=8080)