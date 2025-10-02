from database import SessionLocal
import models
from datetime import date
import json
import glob
import os

def load_readings_from_json():
    """
    Charge automatiquement toutes les lectures depuis les fichiers JSON reading_*.json
    """
    db = SessionLocal()
    try:
        # Trouver tous les fichiers reading_*.json
        json_files = glob.glob("reading_*.json")
        
        if not json_files:
            print("Aucun fichier reading_*.json trouvé.")
            return
        
        print(f"Fichiers JSON trouvés: {len(json_files)}")
        
        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                reading_date = date.fromisoformat(data['date'])
                
                # Vérifier si la lecture existe déjà
                existing_day = db.query(models.Day).filter(models.Day.date == reading_date).first()
                if existing_day:
                    print(f"[OK] {data['date']} deja present, ignore.")
                    continue
                
                print(f"[INFO] Ajout de {data['date']}...")
                
                # Créer le jour
                day = models.Day(
                    date=reading_date,
                    title=data['title'],
                    month_id=data['month_id']
                )
                db.add(day)
                db.flush()
                
                # Lecture du matin
                morning = models.Reading(
                    period="matin",
                    content=data['morning_verse'],
                    author=data['morning_author'],
                    reference=data['morning_reference'],
                    source_book=data['morning_reference'],
                    day_id=day.id
                )
                
                # Lecture du soir
                evening = models.Reading(
                    period="soir",
                    content=data['evening_verse'],
                    author=data['evening_author'],
                    reference=data['evening_reference'],
                    source_book=data['evening_reference'],
                    day_id=day.id
                )
                
                db.add_all([morning, evening])
                db.commit()
                print(f"[SUCCESS] {data['date']} ajoute avec succes.")
                
            except Exception as e:
                print(f"[ERROR] Erreur avec {json_file}: {e}")
                db.rollback()
                continue
        
        print(f"\n[SUCCESS] Import termine!")
        
    except Exception as e:
        print(f"Erreur générale: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_readings_from_json()
