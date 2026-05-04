# Faille 11 — S3 Bucket Public

## Concept

Sur AWS S3, chaque bucket peut être **public** ou **privé**.

- **Public** = n'importe qui sur internet peut télécharger les fichiers
- **Privé** = seul le propriétaire (ou les rôles IAM autorisés) peuvent accéder

**Le problème :** Les devs oublient de configurer le bucket en privé, ou oublient de déplacer les données sensibles.

Résultat : données publiquement accessibles.

---

## Exploit

**Scénario :**
1. Tu déploies une app qui a besoin de stocker des backups
2. Tu crées un bucket S3 mais tu oublies de le configurer en privé
3. Tu mets un fichier `backup-2024.sql` (base de données complète) dedans

**L'attaquant fait :**
```bash
# Découvrir le bucket (enumerate ou via scanning)
curl https://myapp-data-bucket-123456789.s3.amazonaws.com/

# Télécharger la base de données
curl https://myapp-data-bucket-123456789.s3.amazonaws.com/backup-2024.sql > backup.sql

# Revendre les données sur le dark net
```

**Impact :** 
- Données clients exfiltrées
- Credentials AWS dans le backup → accès à l'infra
- Chantage / extorsion

---

## Vulnérable vs Sécurisé

### ❌ Vulnérable (`11-s3-bucket-vulnerable.tf`)

```terraform
# Bloque rien — tout est public
block_public_acls       = false
block_public_policy     = false
ignore_public_acls      = false
restrict_public_buckets = false

# N'importe qui peut accéder
Principal = "*"
Action = ["s3:GetObject", "s3:ListBucket"]

# Fichier lisible publiquement
acl = "public-read"
```

### ✓ Sécurisé (`11-s3-bucket-fixed.tf`)

```terraform
# Bloque TOUT accès public
block_public_acls       = true
block_public_policy     = true
ignore_public_acls      = true
restrict_public_buckets = true

# Accès seulement via rôle IAM
Principal = {
  AWS = "arn:aws:iam::ACCOUNT:role/app-role"
}

# Fichier privé (pas d'ACL public)
# Chiffrement server-side
# Versioning activé
# Logging activé
```

---

## Bonnes pratiques S3

**Règle 1 — Block Public Access**
```
Toujours set block_public_acls = true
```

**Règle 2 — IAM Policies, pas Public Access**
```
Accès via rôles IAM seulement, jamais Principal = "*"
```

**Règle 3 — Chiffrement**
```
server_side_encryption_configuration + AES256
```

**Règle 4 — Versioning + Logging**
```
Versioning = Enabled (accidental delete recovery)
Logging = Enabled (audit trail)
```

**Règle 5 — Scan régulièrement**
```
AWS Config + S3 Block Public Access Monitor
```

---

## Incident Réel

**Capital One 2019 :**
1. SSRF vulnerability → credentials IAM
2. Rôle IAM avec `s3:*` → accès à tous les buckets
3. Bucket public mal configuré → données exfiltrées
4. **106 millions de dossiers clients lus**

---

## Classification

- **OWASP Top 10 :** A01:2021 — Broken Access Control
- **CWE :** CWE-732 — Incorrect Permission Assignment
- **AWS Best Practice :** [S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)
- **Impact :** Data breach, compliance violations, regulatory fines

---

## Ressources

- [AWS S3 Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security.html)
- [OWASP Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [Terraform AWS S3](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket)
