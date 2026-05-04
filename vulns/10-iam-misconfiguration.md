# Faille 10 — IAM Misconfiguration

## Concept

Sur AWS, **IAM** = Identity & Access Management = système de permissions.

Une "mauvaise config IAM" = donner trop de permissions à un utilisateur/rôle.

**Principe fondamental :** Least Privilege — chaque service doit avoir le **minimum** de permissions pour fonctionner.

---

## Exploit

**Scénario :**
1. Tu déploies ton app sur une instance EC2
2. L'app a besoin de :
   - Lire des fichiers sur S3 (bucket `app-uploads`)
   - Écrire dans DynamoDB (table `app-data`)
   - Envoyer des logs à CloudWatch

**Tu configures le rôle IAM trop largement :**
```json
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*"
}
```

Ça veut dire : "L'app peut tout faire sur TOUS les buckets S3."

**L'attaquant exploite une SSRF (faille 09) :**
1. Récupère les credentials IAM via le metadata service
2. Utilise ces credentials pour accéder à TOUS les buckets S3 (données clients, backups, etc.)
3. Utilise `iam:*` pour créer un compte administrateur permanent
4. Accès complet à AWS

**Capital One 2019 :**
- SSRF → metadata service → credentials du rôle IAM
- Le rôle avait `s3:*` sur tous les buckets
- Résultat : 106 millions de dossiers clients lus

---

## Vulnérable vs Sécurisé

### ❌ Vulnérable (`10-app-role-vulnerable.json`)

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iam:*",
      "Resource": "*"
    }
  ]
}
```

**Problèmes :**
- `s3:*` = toutes les actions S3 sur TOUS les buckets (delete, put-bucket-policy, etc.)
- `iam:*` = création d'utilisateurs, modification de rôles, vol de credentials
- `dynamodb:*` et `ec2:*` = accès total à ces services

---

### ✓ Sécurisé (`10-app-role-fixed.json`)

```json
{
  "Statement": [
    {
      "Sid": "S3ReadOnly",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::app-uploads",
        "arn:aws:s3:::app-uploads/*"
      ]
    },
    {
      "Sid": "DynamoDBAppTable",
      "Effect": "Allow",
      "Action": ["dynamodb:GetItem", "dynamodb:Query", "dynamodb:PutItem"],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/app-data"
    }
  ]
}
```

**Améliorations :**
- `s3:GetObject` + `s3:ListBucket` seulement (pas delete, pas put-bucket-policy)
- Limité au bucket `app-uploads` (Resource ARN spécifique)
- DynamoDB limité à une table précise
- Pas d'IAM permissions (l'app ne crée pas d'utilisateurs)
- Pas d'EC2 permissions

---

## Bonnes pratiques IAM

**Règle 1 — Least Privilege**
```
Action: "s3:*" ❌
Action: ["s3:GetObject", "s3:ListBucket"] ✓
```

**Règle 2 — Resource Specificity**
```
Resource: "*" ❌
Resource: "arn:aws:s3:::app-uploads/*" ✓
```

**Règle 3 — Audit avec AWS IAM Access Analyzer**
- Trouve les permissions inutilisées
- Revois régulièrement les policies

**Règle 4 — Temporary Credentials**
```
Utilisateur IAM statique ❌
Rôle IAM avec credentials temporaires ✓
```

---

## Classification

- **OWASP Top 10 :** A01:2021 — Broken Access Control
- **CWE :** CWE-276 — Incorrect Default Permissions
- **Impact :** Escalade de privilèges, compromission de toute l'infra AWS

## Ressources

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Capital One 2019 Breach Details](https://aws.amazon.com/blogs/security/handling-aws-security-findings-in-security-hub/)
- [IAM Policy Examples](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_examples.html)
