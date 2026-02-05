import os

# Charger .env si disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import optionnel de Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

# Configuration Supabase
SUPABASE_URL = "https://vzztgsmetcmydxkjqtyv.supabase.co"
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')

supabase = None


def _get_client():
    """Initialise le client Supabase si nécessaire"""
    global supabase
    if not SUPABASE_AVAILABLE:
        return None
    if supabase is None and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase


def sauvegarder_score(pseudo, score_joueur):
    """Sauvegarde un score dans la table highscore"""
    client = _get_client()
    if client is None:
        raise ConnectionError("Supabase non configuré (installez: pip install supabase)")
    data = {"name": pseudo, "score": score_joueur}
    response = client.table("highscore").insert(data).execute()
    return response


def recuperer_high_scores(limite=10):
    """Récupère les meilleurs scores triés par ordre décroissant"""
    client = _get_client()
    if client is None:
        return []
    response = client.table("highscore") \
        .select("name, score") \
        .order("score", desc=True) \
        .limit(limite) \
        .execute()
    return response.data
