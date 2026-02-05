import os
from supabase import create_client, Client

# Charger .env si disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv pas installé

# Remplace par tes vraies informations
url = "https://vzztgsmetcmydxkjqtyv.supabase.co"
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', 'sb_secret_YEJ0KlF0pnqQtXx59YJORQ_r7Y0FKHo')  # Fallback pour dev

supabase: Client = create_client(url, key)

def sauvegarder_score(pseudo, score_joueur):
    data = {"name": pseudo, "score": score_joueur}
    # Insertion dans la table 'highscore'
    response = supabase.table("highscore").insert(data).execute()
    return response

def recuperer_high_scores(limite=10):
    # Récupère les meilleurs scores, triés par ordre décroissant
    response = supabase.table("highscore") \
        .select("name, score") \
        .order("score", desc=True) \
        .limit(limite) \
        .execute()
    return response.data