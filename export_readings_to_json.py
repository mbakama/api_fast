"""
Script pour exporter toutes les lectures de la base de données vers des fichiers JSON
"""
from database import SessionLocal
import models
import json
from datetime import date

def export_all_readings():
    """Exporte toutes les lectures de la BD vers des fichiers JSON"""
    db = SessionLocal()
    try:
        # Récupérer tous les jours avec leurs lectures
        days = db.query(models.Day).order_by(models.Day.date).all()
        
        if not days:
            print("Aucune lecture trouvée dans la base de données.")
            return
        
        print(f"Nombre de jours trouvés: {len(days)}")
        
        exported_count = 0
        for day in days:
            # Trouver les lectures matin et soir
            morning = next((r for r in day.readings if r.period == "matin"), None)
            evening = next((r for r in day.readings if r.period == "soir"), None)
            
            if not morning or not evening:
                print(f"[WARNING] {day.date}: lectures incomplètes, ignoré.")
                continue
            
            # Créer le dictionnaire de données
            data = {
                "date": day.date.isoformat(),
                "title": day.title,
                "month_id": day.month_id,
                "morning_verse": morning.content,
                "morning_reference": morning.reference,
                "morning_author": morning.author,
                "evening_verse": evening.content,
                "evening_reference": evening.reference,
                "evening_author": evening.author
            }
            
            # Nom du fichier
            filename = f"reading_{day.date.isoformat()}.json"
            
            # Écrire le fichier JSON
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"[OK] {filename} créé")
            exported_count += 1
        
        print(f"\n[SUCCESS] {exported_count} fichiers JSON exportés!")
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'export: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    export_all_readings()
