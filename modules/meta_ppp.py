class PPP():
    def __init__(self, db):
        self.db = db
    
    def create_from_arc(self, arc_id, phase, annotation_note, commit=True):
        sql = "INSERT INTO meta_ppp (arc_id, phase, annotation_note) VALUES (:arc_id, :phase, :annotation_note)"
        self.db.session.execute(sql, 
            {
                "arc_id": arc_id, 
                "phase": phase, 
                "annotation_note": annotation_note
            }
        )
        if commit:
            self.db.session.commit()
    
    def read_from_arc(self, arc_id, commit=True):
        sql = "SELECT * FROM meta_ppp WHERE arc_id=:arc_id"
        return self.db.session.execute(
            sql, 
            {
                "arc_id": arc_id, 
            }
        ).fetchall()

    def read_from_arc_list(self, arc_id_list, commit=True):
        sql = "SELECT * FROM meta_ppp WHERE arc_id IN :arc_id_list"
        return self.db.session.execute(
            sql, 
            {
                "arc_id_list": tuple(arc_id_list), 
            }
        ).fetchall()
    
    def update_note(self, new_ppp, commit=True):
        sql = "UPDATE meta_ppp SET annotation_note=:annotation_note WHERE id=:id"
        self.db.session.execute(sql, new_ppp)
        if commit:
            self.db.session.commit()
    