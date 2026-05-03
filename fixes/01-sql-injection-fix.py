# FIX 01 — SQL Injection
# Remplacement de la concaténation de chaîne par une requête paramétrée.

from werkzeug.security import check_password_hash

# AVANT (vulnérable) --------------------------------------------------------
# user = db.execute(
#     f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
# ).fetchone()
# if user:
#     ...  # connecté sans vérification du mot de passe

# APRÈS (corrigé) ------------------------------------------------------------
# 1. Requête paramétrée : le ? empêche toute injection SQL
# 2. Vérification du hash séparée : check_password_hash ne se contourne pas par SQLi

def login_secure(db, username, password):
    user = db.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()

    if user and check_password_hash(user['password'], password):
        return user  # authentification réussie
    return None      # échec
