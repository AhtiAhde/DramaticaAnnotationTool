class Dramatica():
    def __init__(self, db):
        self.db = db
    
    def create_pp_from_arc(self, arc_id, plot_point, theme, annotation_note, commit=True):
        sql = "INSERT INTO annotool.meta_dramatica_pp (arc_id, plot_point, theme, annotation_note) VALUES (:arc_id, :plot_point, :theme, :annotation_note)"
        self.db.session.execute(sql, 
            {
                "arc_id": arc_id, 
                "plot_point": plot_point,
                "theme": theme, 
                "annotation_note": annotation_note
            }
        )
        if commit:
            self.db.session.commit()
    
    def read_pp_from_arc(self, arc_id, commit=True):
        sql = "SELECT * FROM annotool.meta_dramatica_pp WHERE arc_id=:arc_id"
        return self.db.session.execute(
            sql, 
            {
                "arc_id": arc_id, 
            }
        ).fetchall()

    def read_pp_from_arc_list(self, arc_id_list, commit=True):
        sql = "SELECT * FROM annotool.meta_dramatica_pp WHERE arc_id IN :arc_id_list"
        return self.db.session.execute(
            sql, 
            {
                "arc_id_list": tuple(arc_id_list), 
            }
        ).fetchall()
    
    def update_pp(self, new_pp, commit=True):
        sql = "UPDATE annotool.meta_dramatica_pp SET plot_point=:plot_point, theme=:theme, annotation_note=:annotation_note WHERE id=:id"
        self.db.session.execute(sql, new_pp)
        if commit:
            self.db.session.commit()
    
    def get_elements(self):
        return {
            "protagonist": ["knowledge", "actuality", "proven", "effect"
                            "consider", "pursuit", "certainty", "proaction"],
            "antagonist": ["thought", "perception", "unproven", "cause",
                           "recosider", "avoid", "potentiality", "reaction"],
            "guardian": ["equity", "projection", "expectation", "ending",
                         "conscience", "help", "reduction", "evaluation"],
            "contagonist": ["inequity", "speculation", "determination", "unending",
                            "temptation", "hinder", "production", "re-evaluation"],
            "reason": ["ability", "aware", "theory", "trust",
                       "logic", "control", "probability", "inaction"],
            "emotion": ["desire", "self-aware", "hunch", "test",
                        "feeling", "uncontrolled", "possibility", "protection"],
            "sidekick": ["order", "inertia", "accurate", "result",
                         "faith", "support", "deduction", "acceptance"],
            "skeptic": ["chaos", "change", "non-accurate", "process",
                        "disbelief", "oppose", "induction", "non-acceptance"]
        }
    