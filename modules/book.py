from random import randrange

class Book():
    def __init__(self, db):
        self.db = db

    ### General Helpers ###
    
    def _get_role_annotations(self, book_id, user_id):
        # Using COALESCE here to accomodate the default value will lead to tricky
        # insert or update problems else where adding cyclomatic code complexity a lot
        return self.db.session.execute('''
            SELECT 
                annotool.characters.id, 
                annotool.characters.name, 
                annotool.role_annotations.role
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
        
    # Used by book struct constructed by parse_characters
    def _get_roles(self):
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

    ### Used by @app.route("/books", methods=["GET"]) with book id ### 
    def parse_characters(self, book_id, user_id):
        book = {}
        result = self.db.session.execute(
            "SELECT * FROM annotool.books WHERE id=:book_id LIMIT 1",
            {"book_id": book_id})
        books = result.fetchall()
        book = dict(books[0])
        
        result = self._get_role_annotations(book_id, user_id)    
        book['characters'] = result.fetchall()
        book['roles'] = self._get_roles()
        return book
    
    # Used by @app.route("/books", methods=["GET"]) when book id is not set
    # I would prefer more RESTful router, that would allow not overloading
    # the router but Flask is Flask...
    def list_books(self):
        books = []
        result = self.db.session.execute("SELECT * FROM annotool.books")
        for book in result.fetchall():
            books.append(dict(book))
        return books
    
    ### Used by @app.route("/books", methods=["POST"]) ###
    
    def write_role_annotations(self, book_id, user_id, form_annotations):
        # book is a container for characters
        book = self.parse_characters(book_id, user_id)
        
        # using this to map character names to ids and checking if annotation exists
        char_name_to_id = {}
        for character in book['characters']:
            char_name_to_id[character.name] = (character.id, character.role)

        # we need to choose whether we insert or update; a bit clumsy
        inserts = []
        updates = []
        for key, value in form_annotations:
            if "role-" in key:
                char_id, char_role = char_name_to_id[key.split('-')[1]]
                if char_role:
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

        # persistance operations; we could also use soft updates and store all as inserts
        if len(inserts) > 0:
            sql = "INSERT INTO annotool.role_annotations (user_id, char_id, role) VALUES (:user_id, :char_id, :role)"
            self.db.session.execute(sql, inserts)
            self.db.session.commit()
        
        if len(updates) > 0:
            sql = "UPDATE annotool.role_annotations SET user_id=:user_id, role=:role WHERE char_id=:char_id"
            self.db.session.execute(sql, updates)
            self.db.session.commit()
    
    ### Used by @app.route("/tasks/<int:b_id>", methods=["GET"]) ###
    
    def get_random_paragraph(self, book_id):
        max_p = self.db.session.execute(
            "SELECT MAX(id) FROM annotool.paragraphs WHERE book_id=:book_id",
            {"book_id": book_id}
            ).fetchall()
        return randrange(1, max_p[0][0])
    
    ### Used by @app.route("/tasks/<int:b_id>/<int:p_id>", methods=["GET"]) ###
    
    def get_paragraph(self, book_id, paragraph_id):
        return self.db.session.execute(
            "SELECT * FROM annotool.paragraphs WHERE book_id=:book_id AND id=:paragraph_id",
            {"book_id": book_id, "paragraph_id": paragraph_id}
            ).fetchone()