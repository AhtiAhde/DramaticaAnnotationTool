from modules.meta_mice import Mice
from modules.meta_ppp import PPP
from modules.meta_dramatica import Dramatica

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
        
        ppp = PPP(self.db)
        ppps = ppp.read_from_arc_list(ids)
        
        dramatica = Dramatica(self.db)
        dramaticas = dramatica.read_pp_from_arc_list(ids)
        
        # parse the final constructs
        ret = []
        for arc in arc_list:
            arc_view = {
                "id": arc.id,
                "title": arc.title,
                "short_desc": arc.short_desc
            }
            
            for mice_instance in mices:
                if mice_instance.arc_id == arc.id:
                    arc_view['mice_type'] = mice_instance.mice_type
                    if mice_instance.is_start_event:
                        arc_view['mice_start'] = mice_instance.annotation_note
                    else:
                        arc_view['mice_end'] = mice_instance.annotation_note
            
            progress_list = []
            for ppp_instance in ppps:
                if ppp_instance.arc_id == arc.id:
                    if ppp_instance.phase == "promise":
                        arc_view['promise'] = ppp_instance.annotation_note
                    if ppp_instance.phase == "payoff":
                        arc_view['payoff'] = ppp_instance.annotation_note
                    if ppp_instance.phase == "progress":
                        progress_list.append(ppp_instance)
            arc_view['progresses'] = progress_list
            
            for dramatica_instance in dramaticas:
                if dramatica_instance.arc_id == arc.id:
                    arc_view['dramatica_pp'] = dramatica_instance.plot_point
                    arc_view['dramatica_pp_theme'] = dramatica_instance.theme
                    arc_view['dramatica_pp_note'] = dramatica_instance.annotation_note
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
                continue
            if existing_annotation['is_start_event'] == 0:
                end_mice = dict(existing_annotation)
                continue
        
        mice_type = form_data['mice']
        start_note = form_data['start-event']
        end_note = form_data['end-event']
        
        if start_mice and end_mice:
            if start_mice['mice_type'] != end_mice['mice_type']:
                print("mice types mismatch", start_mice['id'], end_mice['id'], arc_id)
            if mice_type != start_mice['mice_type']:
                start_mice['mice_type'] = mice_type
                end_mice['mice_type'] = mice_type
                # TODO: try if these row objects could be directly used for updating
                mice.update_mice_type(start_mice, False)
                mice.update_mice_type(end_mice, False)
            if start_mice['annotation_note'] != start_note:
                start_mice['annotation_note'] = start_note
                mice.update_annotation_note(start_mice, False)
            if end_mice['annotation_note'] != end_note:
                end_mice['annotation_note'] = end_note
                mice.update_annotation_note(end_mice, False)
        else:
            mice.create_from_arc(arc_id, mice_type, start_note, True, False)
            mice.create_from_arc(arc_id, mice_type, end_note, False, False)
        
        # handle Promises Progresses and Payoffs
        ppp = PPP(self.db)
        promise = None
        payoff = None
        progresses = []
        
        for existing_ppp in ppp.read_from_arc(arc_id):
            if existing_ppp['phase'] == 'promise':
                promise = dict(existing_ppp)
                continue
            if existing_ppp['phase'] == 'payoff':
                payoff = dict(existing_ppp)
                continue
            if existing_ppp['phase'] == 'progress':
                progresses.append(dict(existing_ppp))
        
        if form_data['promise']:
            if promise and promise['annotation_note'] != form_data['promise']:
                promise['annotation_note'] = form_data['promise']
                ppp.update_note(promise, False)
            elif not promise:
                ppp.create_from_arc(arc_id, 'promise', form_data['promise'], False)
                        
        if form_data['payoff']:
            if payoff and payoff['annotation_note'] != form_data['payoff']:
                payoff['annotation_note'] = form_data['payoff']
                ppp.update_note(payoff, False)
            elif not payoff:
                ppp.create_from_arc(arc_id, 'payoff', form_data['payoff'], False)
        
        
        if form_data['new-progress'] != "":
            ppp.create_from_arc(arc_id, 'progress', form_data['new-progress'], False)
        
        # handle Dramatica
        dramatica = Dramatica(self.db)
        promise = None
        payoff = None
        progresses = []
        
        existing_dramatica_pp = dramatica.read_pp_from_arc(arc_id)
        
        if len(existing_annotation) == 1:
            existing_annotation = dict(existing_annotation[0])
            if existing_dramatica_pp['plot_point'] != form_data['dramatica-pp']:
                existing_dramatica_pp['plot_point'] = form_data['dramatica-pp']
            if existing_dramatica_pp['theme'] != form_data['dramatica-pp-theme']:
                existing_dramatica_pp['theme'] = form_data['dramatica-pp-theme']
            if existing_dramatica_pp['annotaion_note'] != form_data['dramatica-pp-note']:
                existing_dramatica_pp['annotation_note'] = form_data['dramatica-pp-note']
            dramatica.update_pp(existing_dramatica_pp, False)
        elif form_data['dramatica-pp'] != 'unknown' or form_data['dramatica-pp-theme'] != 'unknown':
            dramatica.create_pp_from_arc(
                arc_id,
                form_data['dramatica-pp'],
                form_data['dramatica-pp-theme'],
                form_data['dramatica-pp-note']
            )
            
            
        
        self.db.session.commit()

        