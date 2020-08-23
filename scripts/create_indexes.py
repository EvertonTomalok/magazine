from crawler_magazine.model.db import Database

if __name__ == '__main__':
    with Database() as db:
        db._ensure_indexes()
