from database import SessionLocal, engine
import models

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
                (11, "Ma shíyyat", "Volonté"),
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

if __name__ == "__main__":
    print("Applying database schema...")
    models.Base.metadata.create_all(bind=engine)
    seed_months()
    seed_books()
