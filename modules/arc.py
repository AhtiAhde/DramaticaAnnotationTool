from modules.meta_mice import Mice

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
        arcs = self.db.session.execute(
            sql,
            {
                "user_id": user_id,
                "book_id": book_id
            }
        )
        
        ids = []
        arc_list = []
        for arc in arcs:
            arc_list.append(arc)
            ids.append(arc.id)
        
        if len(ids) == 0:
            return {}
        mice = Mice(self.db)
        mices = mice.read_from_arc_list(ids)
        
        # parse the final constructs
        ret = []
        for arc in arc_list:
            arc_view = {
                "id": arc.id,
                "title": arc.title,
                "short_desc": arc.short_desc
            }
            for mice in mices:
                if mice.arc_id == arc.id:
                    arc_view['mice_type'] = mice.mice_type
                    if mice.is_start_event:
                        arc_view['mice_start'] = mice.annotation_note
                    else:
                        arc_view['mice_end'] = mice.annotation_note
            ret.append(arc_view)
        return ret

    def update_annotations(self, book_id, user_id, arc_id, form_data):
        # check authorization
        sql = "SELECT * FROM annotool.annotation_arc WHERE user_id=:user_id AND book_id=:book_id AND id=:arc_id"
        result = self.db.session.execute(
            sql,
            {
                "user_id": user_id,
                "book_id": book_id,
                "arc_id": arc_id
            }
        ).fetchall()
        
        if len(result) != 1:
            print("Unoauthorized user", user_id, book_id, arc_id)
        
        # mice annotations
        mice = Mice(self.db)
        start_mice = None
        end_mice = None
        for existing_annotation in mice.read_from_arc(arc_id):
            if existing_annotation['is_start_event'] == 1:
                start_mice = dict(existing_annotation)
            if existing_annotation['is_start_event'] == 0:
                end_mice = dict(existing_annotation)
        
        # do updates instead of creating
        mice_type = form_data['mice']
        start_note = form_data['start-event']
        end_note = form_data['end-event']
        
        print(start_mice, end_mice)
        if start_mice and end_mice:
            print("Here?")
            if start_mice['mice_type'] != end_mice['mice_type']:
                print("mice types mismatch", start_mice['id'], end_mice['id'], arc_id)
            if mice_type != start_mice['mice_type']:
                start_mice['mice_type'] = mice_type
                end_mice['mice_type'] = mice_type
                # TODO: try if these row objects could be directly used for updating
                mice.update_mice_type(start_mice)
                mice.update_mice_type(end_mice)
            if start_mice['annotation_note'] != start_note:
                start_mice['annotation_note'] = start_note
                mice.update_annotation_note(start_mice)
            if end_mice['annotation_note'] != end_note:
                end_mice['annotation_note'] = end_note
                mice.update_annotation_note(end_mice)
        else:
            mice.create_from_arc(arc_id, mice_type, start_note, True)
            mice.create_from_arc(arc_id, mice_type, end_note, False)
        
        