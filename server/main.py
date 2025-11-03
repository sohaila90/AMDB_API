from flask import Flask, jsonify, request
from flask_cors import CORS
import requests, os
import time
from cache import load_cache, save_cache
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
    "sort_by": "title.asc",
    "with_origin_country": "EG",    # kun fra Egypt
    "with_original_language": "ar", # arabisk originalspråk
}

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/movies", methods=["GET", "POST"])
def movies():
    cached = load_cache()
    if cached:
        return jsonify(cached)
    
    #Ingen cache? Da henter vi alle sidene fra TMDb
    all_results = [] #alle resultatene blir lagret her
    page = 1 #starter på side 1
    params = DISCOVER_PARAMS.copy() #lag en kopi av DISCOVER_PARAMS, fordi vi skal dynamisk endre "page"
    params["page"] = page
    
    print("Fetching page 1...")
    start_time = time.time()
    
    # Start med å hente den første siden
    # For nå: uansett GET/POST -> returner Egypt-liste
    r = requests.get(
        "https://api.themoviedb.org/3/discover/movie",
        headers=headers,
        params=params,
    )
    data = r.json()

    
    total_pages = data.get("total_pages", 1) #hent ut "total_pages" verdien fra resultatet
    all_results.extend(data.get("resutls", [])) #legg til dataen i all_results (extend er det samme som append)
    
    #loop gjennom de resterende sidene. I results står det hvor mange siden det er
    for page in range(2, total_pages + 1): #start på side 2 (vi har allerde gjort side 1), og øk med 1, til vi har vært igjennom alle
        params["page"] = page #oppdater hvilken page vi skal hente. Dette er hvorfor vi lagde en kopi av DISCOVER_PARAMS
        r = requests.get(
            "https://api.themoviedb.org/3/discover/movie",
            headers=headers,
            params=params,
        )
        if r.status_code != 200: #200 == OK, hvis vi vår noe annet enn OK, så stopper vi. Her bør du ha bedre feilhåndtering så du vet hva som evt. går galt
            break
        data = r.json()
        all_results.extend(data.get("results", [])) #legg til de nye resultatene i arrayet ditt

        elapsed = time.time() - start_time
        pages_done = page
        pages_left = total_pages - pages_done
        avg_time = elapsed / pages_done
        eta = pages_left * avg_time
        
        print(f"✅ Page {page}/{total_pages} done "
              f"| {pages_done}/{total_pages} pages | "
              f"Time elapsed: {elapsed:.1f}s | "
              f"ETA: {eta:.1f}s")
        time.sleep(0.25) #pass på at vi ikke overstiger rate limit (40 requests per 10. sekund (40/10 = 0.25))
    
    #oppdater cache
    save_cache(all_results)
    return jsonify({"results": all_results, "total_results": len(all_results)}), r.status_code #returner resultatene fra alle sidene


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