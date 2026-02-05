import os
from supabase import create_client, Client

# Remplace par tes vraies informations
url = "https://vzztgsmetcmydxkjqtyv.supabase.co"
key = "sb_secret_YEJ0KlF0pnqQtXx59YJORQ_r7Y0FKHo"

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