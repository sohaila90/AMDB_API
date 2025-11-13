from flask import Flask, jsonify, request
from flask_cors import CORS
import requests, os
import time
import random
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

@app.route("/movies/newest", methods=["GET"])
def newest_movie():
    #her kopierer vi parametere
    params = DISCOVER_PARAMS.copy()
    #endrer sortering til nyeste først
    params["sort_by"] = "primary_release_date.desc"
    #hent data fra tmdb med reqyestget
    r = requests.get("https://api.themoviedb.org/3/discover/movie",
    params=params,
    headers=headers,
    )
    #konverter svar med json
    data = r.json()
    #hent ut listen
    results = data["results"]
    #ta de 3 første filmene
    newest_three = results[:3]
    #retuner med json
    return jsonify({"results": newest_three})
    
@app.route("/movies/popular", methods=["GET"])
def popular_movie():
        params = DISCOVER_PARAMS.copy()
        params["sort_by"] = "popularity.desc"
        params["page"] = 1 #start på side 1
        
        all_results = [] #her lagrer vi alt vi henter

        #hent første side
        r = requests.get(
             "https://api.themoviedb.org/3/discover/movie",
        params=params,
        headers=headers                 
        )
        data = r.json()
        
        #finn ut hvor mange sider som finnes
        total_pages = data.get("total_pages", 1)
        
        #legg til filmene fra første side
        all_results.extend(data.get("results", []))

        for page in range(2, min(total_pages + 1, 4)):
             params["page"] = page
             r = requests.get(
                  "https://api.themoviedb.org/3/discover/movie",
                  params=params,
                  headers=headers
             )
             if r.status_code != 200:
                  break
             data = r.json()
             all_results.extend(data.get("results", []))
             time.sleep(0.25) #unngå spamme apiet for fort

             top_movies = all_results[:20]

             #send som json til fronend
        return jsonify({"results": top_movies}), 200


@app.route("/movies/random", methods=["GET"])
def random_movie():
    #FIKSE DETTE SENERE-SPØR STIAN
    # cached = load_cache()
    # if cached:
    #     return jsonify(cached)

    params = DISCOVER_PARAMS.copy()
    params["sort_by"] = "vote_count.asc" 
    params["page"] = 1

    #tom kurv ingen filmer ennå
    random_movies_list = []

    r = requests.get("https://api.themoviedb.org/3/discover/movie",
    params=params,
    headers=headers
    )
    data = r.json()
    #her får jeg en eske med fimer, det er som en liten liste med filmer, [film1, film2]
    #total_results = data.get("total_results", 2)
    #når vi bruker extend heller man ut alle filmene en etter en i kurven
    random_movies_list.extend(data.get("results", []))
    save_cache(random_movies_list)
    print(random.sample(random_movies_list, k=1))
    random.sample(random_movies_list, k=11)
    random_eleven = (random.sample(random_movies_list, k=11))

    return jsonify(random_eleven)

if __name__ == "__main__":
    app.run(debug=True, port=8080)