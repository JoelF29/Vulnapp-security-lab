# Fix 07 — Hardcoded Credentials

## Faille
```python
# ❌ Vulnérable — credentials en dur dans le code
AWS_ACCESS_KEY_ID = 'AKIA1234567890ABCD'
AWS_SECRET_ACCESS_KEY = 'wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY'
AWS_REGION = 'us-east-1'

import boto3
s3 = boto3.client('s3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)
```

**Dangers :**
- Credentials visibles dans le code source
- Visibles sur GitHub si repo public
- Impossibles à rotater sans redéployer le code

## Fix
```python
# ✓ Sécurisé — variables d'environnement
import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Vérifier que les variables existent
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError('Variables AWS manquantes — vérifier le fichier .env')

import boto3
s3 = boto3.client('s3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)
```

## Fichier `.env` (ne pas committer)
```
AWS_ACCESS_KEY_ID=AKIA1234567890ABCD
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
```

## Fichier `.gitignore`
```
.env
.env.local
*.pem
*.key
```

## Alternative : Utiliser IAM Role (AWS EC2)
```python
# ✓ Meilleur : pas de credentials du tout, rôle IAM automatique
import boto3

# boto3 récupère automatiquement les credentials du rôle IAM
s3 = boto3.client('s3', region_name='us-east-1')
```

## Bonnes pratiques
1. **Jamais** mettre les secrets dans le code
2. **Toujours** utiliser des variables d'environnement ou secret managers
3. **En production :** AWS Secrets Manager, HashiCorp Vault, etc.
4. **En dev local :** fichier `.env` + `.gitignore`

## Ressources
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [AWS IAM Roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)
