from crawler_magazine.model.db import Database

if __name__ == "__main__":
    print("Creating indexes.")
    with Database() as db:
        db._ensure_indexes()
    print("All done!")
