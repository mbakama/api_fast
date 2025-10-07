"""
Script pour exporter toutes les lectures de la base de données vers des fichiers JSON
"""
from database import SessionLocal
import models
import json
from datetime import date
import codecs

def sanitize_text(text):
    """Nettoie le texte pour éviter les problèmes d'encodage"""
    if text is None:
        return ""
    try:
        # Essayer de nettoyer le texte en le décodant puis en le réencodant
        return text.encode('utf-8', errors='ignore').decode('utf-8')
    except Exception:
        # En cas d'échec, retourner une chaîne vide
        return ""

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
        
        # Créer un fichier JSON unique pour toutes les lectures
        all_readings = []
        
        exported_count = 0
        for day in days:
            try:
                # Trouver les lectures matin et soir
                morning = next((r for r in day.readings if r.period == "matin"), None)
                evening = next((r for r in day.readings if r.period == "soir"), None)
                
                if not morning or not evening:
                    print(f"[WARNING] {day.date}: lectures incomplètes, ignoré.")
                    continue
                
                # Créer le dictionnaire de données avec nettoyage des textes
                data = {
                    "date": day.date.isoformat(),
                    "title": sanitize_text(day.title),
                    "month_id": day.month_id,
                    "morning_verse": sanitize_text(morning.content),
                    "morning_reference": sanitize_text(morning.reference),
                    "morning_author": sanitize_text(morning.author),
                    "evening_verse": sanitize_text(evening.content),
                    "evening_reference": sanitize_text(evening.reference),
                    "evening_author": sanitize_text(evening.author)
                }
                
                # Ajouter à la liste complète
                all_readings.append(data)
                
                # Nom du fichier individuel
                filename = f"reading_{day.date.isoformat()}.json"
                
                # Écrire le fichier JSON individuel
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"[OK] {filename} créé")
                exported_count += 1
                
            except Exception as e:
                print(f"[ERROR] Erreur avec le jour {day.date}: {e}")
                continue
        
        # Écrire toutes les lectures dans un seul fichier
        with open("all_readings.json", 'w', encoding='utf-8') as f:
            json.dump(all_readings, f, ensure_ascii=False, indent=2)
        
        print(f"\n[SUCCESS] {exported_count} fichiers JSON exportés!")
        print(f"[SUCCESS] Toutes les lectures exportées dans all_readings.json")
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'export: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    export_all_readings()
