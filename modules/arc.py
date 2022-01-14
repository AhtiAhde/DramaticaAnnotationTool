class Arc():
    def __init__(self, db):
        self.db = db
    
    def create(self, book_id, user_id, title, short_desc):
        sql = "INSERT INTO annotool.annotation_arc (user_id, book_id, title, short_desc) VALUES (:user_id, :book_id, :title, :short_desc)"
        self.db.session.execute(sql, 
            {
                "user_id": user_id, 
                "book_id": book_id, 
                "title": title, 
                "short_desc": short_desc
            }
        )
        self.db.session.commit()
    
    def read(self, book_id, user_id):
        sql = "SELECT id, title, short_desc FROM annotool.annotation_arc WHERE user_id=:user_id AND book_id=:book_id"
        return self.db.session.execute(
            sql,
            {
                "user_id": user_id,
                "book_id": book_id
            }
        )
        