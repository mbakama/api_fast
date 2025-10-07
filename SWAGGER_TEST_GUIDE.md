# Guide de test Swagger UI

## Étapes pour tester l'API :

1. **Ouvrir Swagger UI** : http://localhost:8000/docs

2. **Trouver l'endpoint** : `POST /readings/daily/`

3. **Cliquer sur "Try it out"**

4. **Saisir les données** directement dans les champs :

   ```json
   {
     "date": "2025-10-02",
     "title": "Test depuis Swagger UI",
     "month_id": 1,
     "morning_verse": "Ceci est un test de lecture du matin avec des caractères français et des apostrophes d'Abdu'l-Baha.",
     "morning_reference": "Causeries d'Abdu'l-Baha à Paris",
     "morning_author": "Abdu'l-Baha",
     "evening_verse": "Ceci est un test de lecture du soir avec tous les caractères spéciaux nécessaires.",
     "evening_reference": "Les Écrits de Bahá'u'lláh",
     "evening_author": "Bahá'u'lláh"
   }
   ```

5. **Cliquer sur "Execute"**

## ✅ Ce qui devrait fonctionner maintenant :

- ✅ **Caractères français** : é, è, ê, ô, â, î, û, ç, à
- ✅ **Apostrophes courbes** : ', ’
- ✅ **Accents** : á, é, í, ó, ú, ý
- ✅ **Tous les caractères Unicode**

## 🚨 Si vous avez encore des erreurs :

1. **Vérifiez que month_id existe** (utilisez 1 pour le test)
2. **Assurez-vous que tous les champs requis sont remplis**
3. **Vérifiez que la date est au format YYYY-MM-DD**

## 📝 Format des données attendu :

- `date`: "2025-10-02" (string)
- `title`: "Titre optionnel" (string, peut être null)
- `month_id`: 1 (entier, doit exister dans la DB)
- `morning_verse`: "Texte de la lecture" (string)
- `morning_reference`: "Référence optionnelle" (string, peut être null)
- `morning_author`: "Nom de l'auteur" (string)
- `evening_verse`: "Texte de la lecture" (string)
- `evening_reference`: "Référence optionnelle" (string, peut être null)
- `evening_author`: "Nom de l'auteur" (string)
