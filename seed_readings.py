from database import SessionLocal
import models
from datetime import date

def seed_reading_oct_01():
    """Ajoute la lecture du 1er octobre 2025 si elle n'existe pas"""
    db = SessionLocal()
    try:
        # Vérifier si la lecture existe déjà
        existing_day = db.query(models.Day).filter(models.Day.date == date(2025, 10, 1)).first()
        if existing_day:
            print("Lecture du 1er octobre 2025 déjà présente.")
            return
        
        print("Ajout de la lecture du 1er octobre 2025...")
        
        # Créer le jour
        day = models.Day(
            date=date(2025, 10, 1),
            title="1er OCTOBRE - 5 Mashíyyat (Volonté - 11ème mois)",
            month_id=11
        )
        db.add(day)
        db.flush()
        
        # Lecture du matin
        morning = models.Reading(
            period="matin",
            content="Par Dieu, ô peuples! Des pleurs s'échappent de mes yeux et des yeux d'Ali [le Bab], au milieu de l'assemblée céleste, et mon coeur sanglote, et le coeur de Muhammad sanglote dans le très glorieux Tabernacle, et mon âme appelle, et les âmes des prophètes appellent ceux qui sont doués d'entendement [...] Ce n'est pas sur moi que je m'attriste mais sur celui qui viendra après moi, dans l'ombre de ma cause, avec une souveraineté indubitable et manifeste, car il ne sera pas le bienvenu quand il paraîtra: on rejettera ses signes, on contestera sa suprématie, on discutera avec lui et on trahira sa cause [...] Est-il possible [...] qu'après le lever du soleil de ton testament, au-dessus de l'horizon de ta plus grande tablette, les pieds de quiconque puissent glisser hors du droit chemin ? À ceci nous avons répondu: Ô ma Plume très glorifiée! Il t'appartient de t'occuper de ce qui t'a été ordonné par Dieu, le Magnifié, le Grand. Ne demande pas ce qui épuisera ton coeur et les coeurs des hôtes du paradis qui se sont rangés autour de ma cause merveilleuse [...] Il n'est, en vérité, que l'un de mes serviteurs [...] S'il s'éloignait, ne fût-ce qu'un moment, de l'ombre de la Cause, il serait sûrement réduit à néant.",
            author="Baha'u'llah",
            reference='cité dans Shoghi Effendi, "Dieu passe près de nous, p. 239',
            source_book='cité dans Shoghi Effendi, "Dieu passe près de nous, p. 239',
            day_id=day.id
        )
        
        # Lecture du soir
        evening = models.Reading(
            period="soir",
            content="Voici le jour où devraient être rendus manifestes les joyaux de la constance qui gisent cachés au plus profond de l'homme. Ô peuple de justice! Soyez aussi brillants que la lumière et aussi étincelants que le feu qui brûla dans le buisson ardent. L'éc1at du feu de votre amour ne peut que réunir et unifier les peuples et les familles de la terre qui s'affrontent, alors que la fureur de la flamme de l'inimitié et de la haine ne peut qu'entraîner conflit et ruine. Nous implorons Dieu de protéger ses créatures des mauvais desseins de leurs ennemis. Il a, en vérité, pouvoir sur toutes choses.",
            author="Baha'u'llah",
            reference="Les Tablettes de Baha'u'llah, p. 92-93",
            source_book="Les Tablettes de Baha'u'llah, p. 92-93",
            day_id=day.id
        )
        
        db.add_all([morning, evening])
        db.commit()
        print("Lecture du 1er octobre 2025 ajoutée avec succès.")
        
    except Exception as e:
        print(f"Erreur lors de l'ajout de la lecture: {e}")
        db.rollback()
    finally:
        db.close()

def seed_reading_oct_02():
    """Ajoute la lecture du 2 octobre 2025 si elle n'existe pas"""
    db = SessionLocal()
    try:
        # Vérifier si la lecture existe déjà
        existing_day = db.query(models.Day).filter(models.Day.date == date(2025, 10, 2)).first()
        if existing_day:
            print("Lecture du 2 octobre 2025 déjà présente.")
            return
        
        print("Ajout de la lecture du 2 octobre 2025...")
        
        # Créer le jour
        day = models.Day(
            date=date(2025, 10, 2),
            title="2 OCTOBRE - 6 Mashiyyat (Volonté - 11ème mois)",
            month_id=11
        )
        db.add(day)
        db.flush()
        
        # Lecture du matin
        morning = models.Reading(
            period="matin",
            content="L'humanité fléchit aujourd'hui sous le poids de l'inquiétude, du chagrin et de la douleur. Personne n'y échappe. Le monde est une vallée de larmes; mais, grâce à Dieu, le remède est à notre portée. Que notre coeur se détourne de la matière pour vivre dans le monde de l'esprit. Seul ce monde pleut nous donner la liberté. Si nous sommes entourés de difficultés, il nous suffit d'invoquer Dieu et, par sa grâce infinie, nous serons assistés [...] Quand nos pensées sont remplies par l'amertume vis-à-vis de ce monde, tournons notre esprit vers la douceur de la compassion divine, et un calme céleste nous envahira. Si nous sommes emprisonnés sur cette terre, notre esprit peut s'élever vers les cieux, et nous serons vraiment libres.",
            author="Abdu'l-Baha",
            reference="Causeries d'Abdu'l-Baha à Paris, p. 93-94",
            source_book="Causeries d'Abdu'l-Baha à Paris, p. 93-94",
            day_id=day.id
        )
        
        # Lecture du soir
        evening = models.Reading(
            period="soir",
            content="Chaque verset révélé par cette Plume est un portail brillant et étincelant qui laisse voir les gloires d'une vie sainte et pieuse, d'actes purs et irréprochables. Les appels et le message que nous avons livrés ne furent jamais destinés à un seul pays ou à un seul peuple. L'humanité entière doit fermement adhérer à ce qui lui a été révélé et accordé. C'est alors, et alors seulement, qu'elle atteindra la vraie liberté. La terre entière est illuminée de la gloire resplendissante de la révélation de Dieu [...] Voyez comme la plupart des hommes ont reçu la faculté d'entendre la parole très glorifiée de Dieu, parole dont doivent dépendre la réunion et la résurrection spirituelles de tous les hommes.",
            author="Baha'u'llah",
            reference="Les Tablettes de Baha'u'llah, p. 93",
            source_book="Les Tablettes de Baha'u'llah, p. 93",
            day_id=day.id
        )
        
        db.add_all([morning, evening])
        db.commit()
        print("Lecture du 2 octobre 2025 ajoutée avec succès.")
        
    except Exception as e:
        print(f"Erreur lors de l'ajout de la lecture: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_reading_oct_01()
    seed_reading_oct_02()
