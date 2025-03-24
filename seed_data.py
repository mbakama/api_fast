from datetime import date
from database import SessionLocal, engine
import models

def seed_database():
    db = SessionLocal()
    
    try:
        # Création d'un mois
        jamal = models.Month(
            name="Jamal",
            translation="Beauté",
            number=3
        )
        db.add(jamal)
        db.flush()  # Pour obtenir l'ID du mois
        
        # Création des jours
        jour_28_avril = models.Day(
            date=date(2024, 4, 28),
            month_id=jamal.id,
            special_event="FÊTE DES 19 JOURS DE LA BEAUTÉ"
        )
        db.add(jour_28_avril)
        db.flush()
        
        # Lectures du 28 avril
        lectures_28_avril = [
            models.Reading(
                day_id=jour_28_avril.id,
                period="matin",
                content="Ô FILS DE L'EXISTENCE! Aime-moi pour que je puisse t'aimer. Si tu ne m'aimes pas, par aucun moyen mon amour ne pourra t'atteindre. Sache-le, ô serviteur.",
                author="Baha'u'llah",
                source_book="Les Paroles cachées",
                page="p. 10",
                reference="n° 5"
            ),
            models.Reading(
                day_id=jour_28_avril.id,
                period="matin",
                content="Ô FILS DE L'HOMME! Sache te contenter de moi et ne cherche nul autre pour te secourir, car personne en dehors de moi ne te suffira jamais.",
                author="Baha'u'llah",
                source_book="Les Paroles cachées",
                page="p. 14",
                reference="n° 17"
            ),
            models.Reading(
                day_id=jour_28_avril.id,
                period="soir",
                content="Oublie le monde de la création, 0 Plume, tourne-toi vers le visage de ton Seigneur...",
                author="Baha'u'llah",
                source_book="Dieu passe près de nous",
                page="p. 146",
                reference=""
            )
        ]
        db.add_all(lectures_28_avril)
        
        # Ajout des livres sources
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
        
        # Commit final
        db.commit()
        print("Données d'exemple ajoutées avec succès!")
        
    except Exception as e:
        print(f"Erreur lors de l'ajout des données : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    models.Base.metadata.create_all(bind=engine)
    seed_database() 