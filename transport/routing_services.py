# MONPROJETTRANSPORTPFA/transport/routing_services.py
import openrouteservice
from django.conf import settings
# import logging # On va utiliser print pour ce débogage
# logger = logging.getLogger(__name__)

def get_route_from_ors(coordinates_list, profile='driving-car'):
    print("--- [ROUTING DEBUG] Entrée dans get_route_from_ors ---")
    print(f"[ROUTING DEBUG] Coordonnées reçues: {coordinates_list}")
    
    if not settings.ORS_API_KEY or len(coordinates_list) < 2:
        print("!!! [ROUTING ERROR] ORS_API_KEY non configurée !!!")
        return None
    
    try:
        client = openrouteservice.Client(key=settings.ORS_API_KEY)
        
        # Essayer d'abord avec le routage standard
        try:
            routes = client.directions(
                coordinates=coordinates_list,
                profile=profile,
                format_out='geojson',
                instructions=True,
                instructions_format='text',
                language='fr',
            )
        except openrouteservice.exceptions.ApiError as e:
            if 'routable point' in str(e):
                print("[ROUTING DEBUG] Tentative avec options simplifiées...")
                # Essai 2 : Sans options problématiques
                routes = client.directions(
                    coordinates=coordinates_list,
                    profile=profile,
                    format_out='geojson',
                    instructions=False  # Désactive les instructions pour simplifier
                )
            else:
                raise

        # Traitement de la réponse
        if routes and 'features' in routes:
            feature = routes['features'][0]
            geometry = feature.get('geometry', {})
            properties = feature.get('properties', {})
            summary = properties.get('summary', {})
            
            route_info = {
                'distance_km': summary.get('distance', 0) / 1000.0,
                'duration_sec': summary.get('duration', 0),
                'geometry_geojson': geometry,
                'instructions_text': "Consultez l'application pour le détail.",
                'raw_response': routes
            }
            return route_info

    except Exception as e:
        print(f"!!! [ROUTING ERROR] Échec final : {str(e)} !!!")
    
    return None
def geocode_address_ors(address_string):
    print(f"--- [GEOCODE DEBUG] Entrée dans geocode_address_ors pour adresse: '{address_string}' ---") # DEBUG
    if not settings.ORS_API_KEY:
        print("!!! [GEOCODE ERROR] ORS_API_KEY non configurée pour le géocodage. !!!") # DEBUG
        return None

    client = openrouteservice.Client(key=settings.ORS_API_KEY)
    try:
        geocode_result = client.pelias_search(
            text=address_string,
            size=1
        )
        print(f"[GEOCODE DEBUG] Réponse brute du géocodage ORS pour '{address_string}': {geocode_result}") # DEBUG

        if geocode_result and geocode_result.get('features') and len(geocode_result['features']) > 0:
            coordinates = geocode_result['features'][0]['geometry']['coordinates']
            print(f"[GEOCODE DEBUG] Adresse '{address_string}' géocodée en (lon, lat): {coordinates}") # DEBUG
            return tuple(coordinates)
        else:
            print(f"!!! [GEOCODE WARNING] Impossible de géocoder l'adresse: '{address_string}'. !!!") # DEBUG
            return None
    except openrouteservice.exceptions.ApiError as e:
        print(f"!!! [GEOCODE API ERROR] Erreur API Geocoding ORS pour '{address_string}': {e} !!!") # DEBUG
        return None
    except Exception as e:
        import traceback
        print(f"!!! [GEOCODE UNEXPECTED ERROR] Erreur inattendue lors du géocodage ORS pour '{address_string}': {e} !!!") # DEBUG
        print(f"!!! [GEOCODE UNEXPECTED ERROR TRACEBACK] {traceback.format_exc()} !!!") # DEBUG
        return None