from database import SessionLocal, engine
import models

def clear_data():
    db = SessionLocal()
    try:
        print("Clearing all data from Month and Book tables...")
        db.query(models.Month).delete()
        db.query(models.Book).delete()
        db.commit()
        print("Tables cleared successfully.")
    except Exception as e:
        print(f"Error clearing tables: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_data()
