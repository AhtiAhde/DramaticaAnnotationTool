class Mice():
    def __init__(self, db):
        self.db = db
    
    def create_from_arc(self, arc_id, mice_type, annotation_note, is_start_event, commit=True):
        sql = "INSERT INTO annotool.meta_mice (arc_id, mice_type, annotation_note, is_start_event) VALUES (:arc_id, :mice_type, :annotation_note, :is_start_event)"
        self.db.session.execute(sql, 
            {
                "arc_id": arc_id, 
                "mice_type": mice_type, 
                "annotation_note": annotation_note, 
                "is_start_event": is_start_event
            }
        )
        if commit:
            self.db.session.commit()
    
    def read_from_arc(self, arc_id, commit=True):
        sql = "SELECT * FROM annotool.meta_mice WHERE arc_id=:arc_id"
        return self.db.session.execute(
            sql, 
            {
                "arc_id": arc_id, 
            }
        ).fetchall()

    def read_from_arc_list(self, arc_id_list, commit=True):
        sql = "SELECT * FROM annotool.meta_mice WHERE arc_id IN :arc_id_list"
        return self.db.session.execute(
            sql, 
            {
                "arc_id_list": tuple(arc_id_list), 
            }
        ).fetchall()
    
    def update_mice_type(self, new_mice, commit=True):
        sql = "UPDATE annotool.meta_mice SET mice_type=:mice_type WHERE id=:id"
        self.db.session.execute(sql, new_mice)
        if commit:
            self.db.session.commit()
        
    def update_annotation_note(self, new_mice, commit=True):
        sql = "UPDATE annotool.meta_mice SET annotation_note=:annotation_note WHERE id=:id"
        self.db.session.execute(sql, new_mice)
        if commit:
            self.db.session.commit()