from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv

import uuid
import os
from os import getenv

import re

_RE_COMBINE_WHITESPACE = re.compile(r"\s+")

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@app.route("/")
def index():
    # User should get anonymous but persistent token
    # notice that session['user_id] is a reserved word in Flask
    if not "user_hash" in session:
        sql = "INSERT INTO annotool.users (id) VALUES (:id) RETURNING id"
        result = db.session.execute(sql, {"id":uuid.uuid4()})
        db.session.commit()
        session["user_hash"] = result.fetchone()[0]
    
    return render_template("index.html", message="index", user=session["user_hash"])

@app.route("/tasks/<int:b_id>/<int:p_id>")
def tasks():
    # Random task list, prioritized by the admins
    # Two modes, character role annotation (b_id) and character 
    # behavior annotation in paragraphs (p_id)
    # We will first implement the character role annotation
    # The resource list link gives a redirect to one task
    return "Taaskeja"

@app.route("/books", methods=["GET"])
def book():
    # GET
    # This route should take user to the book view
    # The view would include the character annotations
    # And also provide access to paragraphs, perhaps paginated view
    result = db.session.execute("SELECT * FROM annotool.books LIMIT 1")
    books = result.fetchall()
    # / Fix this later for single query
    result = db.session.execute("SELECT * FROM annotool.characters")
    
    print(type(books[0]))
    book = books[0]._asdict()
    book['characters'] = result.fetchall()

    # / fix

    return render_template("book.html", message="book view", book=book)

@app.route("/books", methods=["POST"])
def character_roles():
    # POST
    # Allows to add characters; this might be own resouce that is a
    # list object of suggested characters and their roles
    name = request.form["name"]
    role = request.form["role"]
    sql = "INSERT INTO annotool.characters (user_id, name, role) VALUES (:user_id, :name, :role)"
    db.session.execute(sql, {"user_id":session["user_hash"], "name":name, "role":role})
    db.session.commit()
    return redirect("/books", code=302)

@app.route("/admin/")
def admin():
    # GET
    # Import books and view configuration parameters for 
    # the prioritization and annotation cap
    file_list = os.listdir("static/books")
    result = db.session.execute("SELECT origin FROM annotool.books")
    book_res = result.fetchall()
    already_imported = []
    for book in book_res:
        already_imported.append(book[0])
    print(already_imported)
    import_files = []
    for book_file in file_list:
        if book_file in already_imported:
            continue
        import_files.append(book_file)
        if len(import_files) == 10:
            break
    print(import_files)
    import_list = []
    for import_file in import_files:
        paragraphs = []
        title = ""
        book_started = False
        print(import_file)
        with open("static/books/" + import_file, "r") as book_text:
            buffer = 0
            i = 0
            for line in book_text:
                i += 1
                if book_started:
                    buffer += len(line)
                    if len(line) == 1:
                        paragraphs.append(buffer)
                        buffer = 0
                if title == "" and "Title: " in line:
                    title = line[7:]
                if not book_started:
                    if "START OF THIS PROJECT GUTENBERG EBOOK" in line:
                        book_started = True
                    if "START OF THE PROJECT GUTENBERG EBOOK" in line:
                        book_started = True
        import_list.append((title, len(paragraphs), import_file))

    return render_template("admin.html", is_admin=session.get("is_admin"), import_list=import_list)
    # PUT 
    # change the parameters

@app.route("/admin/login", methods=["POST"])
def admin_login():
    print("Does this even work?")
    user = request.form["user"]
    pwd = request.form["pwd"]
    if user == getenv("ADMIN_USER") and pwd == getenv("ADMIN_PASSWORD"):
        print("Logged in")
        session["is_admin"] = True
    return redirect("/admin", code=302)

@app.route("/admin/books", methods=["POST"])
def admin_book():
    if not session.get("is_admin", False):
        return "Unauthorized"
    
    # GET
    # View of annotation counts per book and paragraphs

    # POST
    # Allows admin to submit new books and proposed list of characters
    book_id = request.form["book-id"]
    file_list = os.listdir("static/books")
    if book_id not in file_list:
        return "Invalid book id"
    
    paragraphs = []
    title = ""
    book_started = False
    with open("static/books/" + book_id, "r") as book_text:
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
            if title == "" and "Title: " in line:
                title = line[7:]
            if not book_started:
                if "START OF THIS PROJECT GUTENBERG EBOOK" in line:
                    book_started = True
                if "START OF THE PROJECT GUTENBERG EBOOK" in line:
                    book_started = True
    
    sql = "INSERT INTO annotool.books (title, origin) VALUES (:title, :origin) RETURNING id"
    book_res_id = db.session.execute(sql, {"title":title, "origin":book_id}).fetchone()[0]
    db.session.commit()

    values = []
    for i in range(len(paragraphs)):
        # Replace line breaks and other whitespace characters,
        # for some reason SQLAlchemy doesn't escape properly with multirow inserts
        paragraph = _RE_COMBINE_WHITESPACE = re.compile(r"\s+").sub(" ", paragraphs[i]).strip()
        values.append({
            "book_id": book_res_id, 
            "seq_num": i, 
            "content": paragraph
        })
    print(values)
    sql = "INSERT INTO annotool.paragraphs (book_id, seq_num, content) VALUES(:book_id, :seq_num, :content)"
    db.session.execute(sql, values)
    db.session.commit()

    return redirect("/books", code=302)
    # PUT 
    # change the book / paragraph priorities
    return "Admin book"


@app.route("/admin/users")
def admin_user():
    # GET / PUT
    # Allows admin to view and change the users reliability ratings
    return "Admin user"