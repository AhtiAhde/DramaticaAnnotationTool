from werkzeug.security import check_password_hash, generate_password_hash

class Auth():
    def __init__(self, db):
        self.db = db
    
    def register(self, email, password, session_id):
        # register new user
        hash_value = generate_password_hash(password)
        sql = "INSERT INTO users (email, password) VALUES (:email, :password)"
        self.db.session.execute(sql, {"email":email, "password":hash_value})
        self.db.session.commit()

        self.register_session(email, session_id)
        return email

    def register_session(self, email, session_id):
        sql = "UPDATE user_sessions SET owner=:owner WHERE id=:session_id"
        self.db.session.execute(sql, {"owner":email, "session_id":session_id})
        self.db.session.commit()

    def login(self, email, password, session_id):
        sql = "SELECT email, password FROM users WHERE email=:email"
        res = self.db.session.execute(sql, {"email":email})
        user = res.fetchone()    
        if not user:
            return False
        
        hash_value = user.password
        if not check_password_hash(hash_value, password):
            return False
        
        # post login, if session has changed add it
        sql = "SELECT owner FROM user_sessions WHERE id=:session_id"
        res = self.db.session.execute(sql, {"session_id": session_id})
        sess = res.fetchone()
        if not sess['owner']:
            print(email, session_id)
            self.register_session(email, session_id)
        elif sess['owner'] != email:
            # this should not happen but might be good idea to log for preventing epic session management failures
            pass

        return email