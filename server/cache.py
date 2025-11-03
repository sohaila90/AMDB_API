import json, os, time

#filen som lagrer den "cacha" API responsen
CACHE_FILE = "movies_cache.json" 
#hvor lenge skal cachen leve? (i sekunder). 86400 sekunder * 2 = 2 dager
CACHE_TTL = 60 * 60 * 24 * 2 
def load_cache():
    """Load cached movie data if it exists and is not expired"""
    
    #hvis cache fila ikke finnes, return None
    if not os.path.exists(CACHE_FILE): 
        return None
    
    #sjekk hvor gammel filen er
    file_age_seconds = time.time() - os.stat(CACHE_FILE).st_mtime
    
    #hvis fila er eldre enn TTL (time to live), ignorer den
    if file_age_seconds > CACHE_TTL:
        print("⚠️ Cache expired - fetching fresh data...")
        return None
    
    #last inn cache
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    #sjekk om results er tom
    if isinstance(data, list) and not data:
        print("⚠️ Cache empty - fetching fresh data...")
        return None
    
    #cachen finnes og er fortsatt valid - load og return den
    print("Cache hit ✅")
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_cache(data):
    """Write data to the cache file"""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)
    print("Cache saved ✅")