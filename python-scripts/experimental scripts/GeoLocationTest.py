import spacy
import geopy

# Load NLP model for named entity recognition
nlp = spacy.load("en_core_web_sm")

# Sample text from an article
text = "The Eiffel Tower in Paris is an iconic landmark."

# Process the text to find location entities
doc = nlp(text)
locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]

# Initialize geolocator
geolocator = geopy.Nominatim(user_agent="wwf-nepal")

# Geocode locations
for location in locations:
    try:
        loc = geolocator.geocode(location)
        if loc:
            print(f"{location}: Latitude: {loc.latitude}, Longitude: {loc.longitude}")
        else:
            print(f"Location not found: {location}")
    except Exception as e:
        print(f"Error geocoding {location}: {e}")