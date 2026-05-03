# FIX 02 — Broken Authentication
# Remplacement de la clé secrète faible par une clé aléatoire forte.

import secrets

# AVANT (vulnérable) --------------------------------------------------------
# app.secret_key = "secret"
# → devinable, forgeable avec itsdangerous

# APRÈS (corrigé) ------------------------------------------------------------
# secrets.token_hex(32) utilise le CSPRNG du système → 256 bits d'entropie
app_secret_key = secrets.token_hex(32)

# NOTE : en production, charger depuis une variable d'environnement
# pour que la clé persiste entre redémarrages (voir faille 08) :
#
# import os
# app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
