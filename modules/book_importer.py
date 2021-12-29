import os
import re

class BookImporter():
    def __init__(self, db, master_mode=False):
        self.db = db
        
        self.file_list = []
        self.already_imported = []
        self.import_files = []
        self.import_list = []
        if master_mode:
            self.file_list = os.listdir("static/books")

    ### General Helpers ###
    
    def _parse_book_content(self, import_file):
        paragraphs = []
        title = ""
        book_started = False
        with open("static/books/" + import_file, "r") as book_text:
            buffer = ""
            i = 0
            for line in book_text:
                i += 1
                if book_started:
                    buffer += line
                    # We assume that only paragraphs longer than 15 are meaningful
                    if len(line) == 1:
                        paragraphs.append(buffer)
                        buffer = ""
                # These ought to be strategy a pattern, that will handle
                # multiple types of books; books released under different
                # licenses follow different patterns; most follow this
                if title == "" and "Title: " in line:
                    title = line[7:]
                if not book_started:
                    if "START OF THIS PROJECT GUTENBERG EBOOK" in line:
                        book_started = True
                    if "START OF THE PROJECT GUTENBERG EBOOK" in line:
                        book_started = True
        
        return paragraphs, title

    ### Admin view, list importable books ###

    def _fetch_imported_books(self):
        result = self.db.session.execute("SELECT origin FROM annotool.books")
        book_res = result.fetchall()
        for book in book_res:
            self.already_imported.append(book[0])
    
    # Not the most elegant pagination, but that will do for now...
    # Heroku hobby tier prevents using more than 5 books anyway...
    def _paginate_import_list(self, page=0, page_size=10):
        n = page * page_size
        for book_file in self.file_list:
            if book_file in self.already_imported:
                continue
            if n > 0:
                n -= 1
                continue

            self.import_files.append(book_file)
            if len(self.import_files) == 10:
                break
    
    def parse_book_import_list(self, page=0, page_size=10):
        self._fetch_imported_books()
        self._paginate_import_list(page, page_size)
        
        for import_file in self.import_files:
            paragraphs, title = self._parse_book_content(import_file)
            self.import_list.append((title, len(paragraphs), import_file))
            # we might not want to list length of paragraphs in production environment
            # though this section is not visible on production environment
            # as production is not run as master_mode; there will be empty list only
            # also, admin will be the only user
        
        return self.import_list
    
    ### Admin view, import book ###
    
    def import_book(self, import_file):
        if import_file not in self.file_list:
            return -1
        
        paragraphs, title = self._parse_book_content(import_file)
        
        sql = "INSERT INTO annotool.books (title, origin) VALUES (:title, :origin) RETURNING id"
        book_res_id = self.db.session.execute(sql, {"title":title, "origin":import_file}).fetchone()[0]
        self.db.session.commit()

        values = []
        for i in range(len(paragraphs)):
            # Replace line breaks and other whitespace characters,
            # for some reason SQLAlchemy doesn't escape properly with multirow inserts
            paragraph = re.compile(r"\s+").sub(" ", paragraphs[i]).strip()
            values.append({
                "book_id": book_res_id, 
                "seq_num": i, 
                "content": paragraph
            })
        print(values)
        sql = "INSERT INTO annotool.paragraphs (book_id, seq_num, content) VALUES(:book_id, :seq_num, :content)"
        self.db.session.execute(sql, values)
        self.db.session.commit()

        stream = os.popen("./admin_tools/extract-characters.sh static/books/" + import_file)
        characters = []
        
        for character in stream.readlines():
            characters.append({"book_id": book_res_id, "name": character.strip()})
        
        print(characters)
        sql = "INSERT INTO annotool.characters (book_id, name) VALUES(:book_id, :name)"
        self.db.session.execute(sql, characters)
        self.db.session.commit()
        
        return book_res_id