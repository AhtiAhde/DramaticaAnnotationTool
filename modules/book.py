class Book():
    def __init__(self, db):
        self.db = db

    ### General Helpers ###
    
    def _get_role_annotations(self, book_id, user_id):
        return self.db.session.execute('''
                SELECT annotool.characters.name, COALESCE(annotool.role_annotations.role, 'Unknown') AS role 
                    FROM annotool.characters 
                LEFT JOIN annotool.role_annotations 
                    ON (annotool.characters.id=annotool.role_annotations.char_id 
                        AND annotool.role_annotations.user_id=:user_id)
                WHERE 
                    annotool.characters.book_id=:book_id''',
                {
                    "book_id": book_id, 
                    "user_id": user_id
                })
    
    ## This method has been "overloaded" for handling the writes too
    def parse_characters(self, book_id, user_id=-1):
        book = {}
        result = self.db.session.execute(
            "SELECT * FROM annotool.books WHERE id=:book_id LIMIT 1",
            {"book_id": book_id})
        books = result.fetchall()
        book = dict(books[0])

        if user_id == -1:
            result = self.db.session.execute(
                "SELECT * FROM annotool.characters WHERE book_id=:book_id",
                {"book_id": book_id})
        else:
            result = self._get_role_annotations(book_id, user_id)
    
        book['characters'] = result.fetchall()
        return book
    
    def list_books(self):
        books = []
        result = self.db.session.execute("SELECT * FROM annotool.books")
        for book in result.fetchall():
            books.append(dict(book))
        return books
    
    def get_roles(self):
        return [
            "Protagonist",
            "Antagonist",
            "Guardian",
            "Contagonist",
            "Reason",
            "Emotion",
            "Sidekick",
            "Skeptic",
            "No role",
            "Not a character",
            "Unknown"
        ]
    
    def write_role_annotations(self, book_id, user_id, form_annotations):
        book = self.parse_characters(book_id)
        query = self.db.session.execute(
            "SELECT char_id FROM annotool.role_annotations WHERE user_id=:user_id",
            {"user_id": user_id}).fetchall()
        
        existing_annotations = []
        print(query)
        for x in query:
            existing_annotations.append(x[0])
        
        char_name_to_id = {}
        for character in book['characters']:
            char_name_to_id[character.name] = character.id

        inserts = []
        updates = []
        for key, value in form_annotations:
            if "role-" in key:
                char_id = char_name_to_id[key.split('-')[1]]
                if char_id in existing_annotations:
                    updates.append({
                        "user_id": user_id,
                        "char_id": char_id,
                        "role": value
                    })
                else:
                    inserts.append({
                        "user_id": user_id,
                        "char_id": char_id,
                        "role": value
                    })
        print(existing_annotations, inserts, updates)
        
        if len(inserts) > 0:
            sql = "INSERT INTO annotool.role_annotations (user_id, char_id, role) VALUES (:user_id, :char_id, :role)"
            self.db.session.execute(sql, inserts)
            self.db.session.commit()
        
        if len(updates) > 0:
            sql = "UPDATE annotool.role_annotations SET user_id=:user_id, role=:role WHERE char_id=:char_id"
            self.db.session.execute(sql, updates)
            self.db.session.commit()