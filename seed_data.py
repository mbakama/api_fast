from database import SessionLocal, engine
import models
from datetime import date

def seed_months():
    db = SessionLocal()
    try:
        if db.query(models.Month).count() == 0:
            print("Seeding Baha'i months...")
            bahai_months = [
                (1, "Bahá", "Splendeur"), 
                (2, "Jalál", "Gloire"), 
                (3, "Jamál", "Beauté"),
                (4, "‘Aẓamat", "Grandeur"), 
                (5, "Núr", "Lumière"), 
                (6, "Raḥmat", "Miséricorde"),
                (7, "Kalimát", "Paroles"), 
                (8, "Kamál", "Perfection"), 
                (9, "Asmá’", "Noms"),
                (10, "‘Izzat", "Puissance"), 
                (11, "Mashíyyat", "Volonté"),
                 (12, "‘Ilm", "Savoir"),
                (13, "Qudrat", "Pouvoir"), 
                (14, "Qawl", "Parole"), 
                (15, "Masá’il", "Questions"),
                (16, "Sharaf", "Honneur"), 
                (17, "Sulṭán", "Souveraineté"), 
                (18, "Mulk", "Empire"),
                (19, "‘Alá’", "Élévation")
            ]
            for number, name, translation in bahai_months:
                month = models.Month(name=name, translation=translation, number=number)
                db.add(month)
            db.commit()
            print(f"{len(bahai_months)} months seeded successfully.")
        else:
            print("Months table is not empty. Seeding skipped.")
    except Exception as e:
        print(f"Error seeding months: {e}")
        db.rollback()
    finally:
        db.close()

def seed_books():
    db = SessionLocal()
    try:
        if db.query(models.Book).count() == 0:
            print("Seeding books...")
            books = [
                models.Book(
                    title="Les Paroles cachées",
                    author="Baha'u'llah",
                    url="https://www.bahai.org/fr/library/authoritative-texts/bahaullah/hidden-words/"
                ),
                models.Book(
                    title="Dieu passe près de nous",
                    author="Shoghi Effendi",
                    url="https://www.bahai.org/fr/library/authoritative-texts/shoghi-effendi/god-passes-by/"
                )
            ]
            db.add_all(books)
            db.commit()
            print(f"{len(books)} books seeded successfully.")
        else:
            print("Books table is not empty. Seeding skipped.")
    except Exception as e:
        print(f"Error seeding books: {e}")
        db.rollback()
    finally:
        db.close()

def gregorian_to_bahai_date(gregorian_date: date) -> tuple:
    """
    Convertit une date grégorienne en date Baha'i.
    Basé sur le fait que le 27 septembre 2025 = 1 Mashíyyat 182
    
    Args:
        gregorian_date: Date grégorienne
    
    Returns:
        tuple: (jour_bahai, mois_bahai, année_bahai)
    """
    # Point de référence: 27 septembre 2025 = 1 Mashíyyat 182 (11ème mois, année 182)
    reference_gregorian = date(2025, 9, 27)
    reference_bahai_day = 1
    reference_bahai_month = 11  # Mashíyyat
    reference_bahai_year = 182
    
    # Calculer la différence en jours
    days_diff = (gregorian_date - reference_gregorian).days
    
    # Calculer la position Baha'i
    total_days_from_ref = reference_bahai_day - 1 + (reference_bahai_month - 1) * 19 + days_diff
    
    # Gérer les années
    bahai_year = reference_bahai_year
    while total_days_from_ref < 0:
        bahai_year -= 1
        total_days_from_ref += 365  # Approximation (19*19 + 4 jours intercalaires)
    
    while total_days_from_ref >= 365:
        bahai_year += 1
        total_days_from_ref -= 365
    
    # Calculer le mois et le jour dans l'année
    if total_days_from_ref < 19 * 18:  # Les 18 premiers mois
        bahai_month = (total_days_from_ref // 19) + 1
        bahai_day = (total_days_from_ref % 19) + 1
    elif total_days_from_ref < 19 * 18 + 4:  # Jours intercalaires
        bahai_month = 19  # Ayyám-i-Há
        bahai_day = total_days_from_ref - (19 * 18) + 1
    else:  # 19ème mois ('Alá')
        bahai_month = 19
        bahai_day = total_days_from_ref - (19 * 18) - 4 + 1
    
    return bahai_day, bahai_month, bahai_year

def get_day_info_from_gregorian(gregorian_date: date = None) -> str:
    """
    Retourne les informations d'un jour spécifique au format:
    "26 SEPTEMBRE - 8 'Izzat (Puissance - 10ème mois)"
    
    Args:
        gregorian_date: Date grégorienne (si None, utilise la date du jour)
    
    Returns:
        str: Information formatée du jour
    """
    if gregorian_date is None:
        gregorian_date = date.today()
    
    db = SessionLocal()
    try:
        # Convertir la date grégorienne en date Baha'i
        bahai_day, bahai_month_number, bahai_year = gregorian_to_bahai_date(gregorian_date)
        
        # Récupérer le mois Baha'i
        month = db.query(models.Month).filter(models.Month.number == bahai_month_number).first()
        
        if not month:
            return f"Mois Baha'i {bahai_month_number} non trouvé"
        
        # Noms des mois grégoriens en français (abrégés)
        gregorian_months = [
            "JAN", "FÉV", "MAR", "AVR", "MAI", "JUN",
            "JUL", "AOU", "SEP", "OCT", "NOV", "DÉC"
        ]
        
        gregorian_month_name = gregorian_months[gregorian_date.month - 1]
        
        # Formatage selon l'exemple: "26 SEP - 1 Asmá' (Noms - 9ème mois)"
        ordinal_suffix = "er" if bahai_month_number == 1 else "ème"
        
        base_info = f"{gregorian_date.day} {gregorian_month_name} - {bahai_day} {month.name} ({month.translation} - {bahai_month_number}{ordinal_suffix} mois)"
        
        return base_info
        
    except Exception as e:
        return f"Erreur: {e}"
    finally:
        db.close()

def get_feast_info(gregorian_date: date = None) -> dict:
    """
    Retourne les informations de fête si c'est un jour de fête (1er jour du mois Baha'i).
    
    Args:
        gregorian_date: Date grégorienne (si None, utilise la date du jour)
    
    Returns:
        dict: Information sur la fête ou None
    """
    if gregorian_date is None:
        gregorian_date = date.today()
    
    db = SessionLocal()
    try:
        bahai_day, bahai_month_number, bahai_year = gregorian_to_bahai_date(gregorian_date)
        
        if bahai_day == 1:  # Premier jour du mois = fête
            month = db.query(models.Month).filter(models.Month.number == bahai_month_number).first()
            if month:
                return {
                    "is_feast": True,
                    "feast_name": f"Fête de {month.name}",
                    "month_name": month.name,
                    "month_translation": month.translation,
                    "month_number": bahai_month_number
                }
        
        return {"is_feast": False}
        
    except Exception as e:
        return {"is_feast": False, "error": str(e)}
    finally:
        db.close()

def get_today_bahai_info() -> str:
    """
    Retourne les informations du jour actuel au format Baha'i.
    
    Returns:
        str: Information formatée du jour actuel
    """
    return get_day_info_from_gregorian()

if __name__ == "__main__":
    print("Applying database schema...")
    models.Base.metadata.create_all(bind=engine)
    seed_months()
    seed_books()
    
    # Exemples d'utilisation des nouvelles fonctions
    print("\nExemples d'utilisation:")
    
    # Informations du jour actuel
    print("Aujourd'hui:", get_today_bahai_info())
    
    # Informations pour une date spécifique
    test_date = date(2024, 4, 28)
    print(f"Le {test_date.strftime('%d/%m/%Y')}:", get_day_info_from_gregorian(test_date))
    
    # Test avec le premier jour d'un mois (fête)
    feast_date = date(2024, 3, 21)  # Premier jour de l'année Baha'i (Naw-Rúz)
    print(f"Fête - Le {feast_date.strftime('%d/%m/%Y')}:", get_day_info_from_gregorian(feast_date))
    
    # Test de conversion de date
    bahai_day, bahai_month, bahai_year = gregorian_to_bahai_date(test_date)
    print(f"Conversion: {test_date} -> Jour {bahai_day}, Mois {bahai_month}, Année {bahai_year}")
