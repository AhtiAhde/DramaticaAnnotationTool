from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv

import uuid
import os
from os import getenv

import re

from modules.book_importer import BookImporter

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

master_mode = False
if getenv("MASTER_MODE") == "enabled":
    master_mode = True

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
    book_id = int(request.args.get("book_id", -1))
    book = False
    books = False
    if book_id > -1:
        print(session['user_hash'])
        book = {}
        result = db.session.execute(
            "SELECT * FROM annotool.books WHERE id=:book_id LIMIT 1",
            {"book_id": book_id})
        books = result.fetchall()

        result = db.session.execute('''
            SELECT annotool.characters.name, COALESCE(annotool.role_annotations.role, 'Unknown') AS role 
                FROM annotool.characters 
            LEFT JOIN annotool.role_annotations 
                ON (annotool.characters.id=annotool.role_annotations.char_id 
                    AND annotool.role_annotations.user_id=:user_id)
            WHERE 
                annotool.characters.book_id=:book_id''',
            {
                "book_id": book_id, 
                "user_id": session['user_hash']
            })
    
        book = dict(books[0])
        book['characters'] = result.fetchall()
        for character in book['characters']:
            print(character)
    else:
        books = []
        result = db.session.execute("SELECT * FROM annotool.books")
        for book in result.fetchall():
            books.append(dict(book))

    # / fix
    roles = [
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
    return render_template("book.html", 
        message="book view", 
        books=books, 
        book=book, 
        roles=roles
    )

@app.route("/books", methods=["POST"])
def character_roles():
    # POST
    # Allows to add characters; this might be own resouce that is a
    # list object of suggested characters and their roles
    book_id = request.form["id"]

    book = {}
    result = db.session.execute(
        "SELECT * FROM annotool.books WHERE id=:book_id LIMIT 1",
        {"book_id": book_id})
    books = result.fetchall()
    # / Fix this later for single query
    result = db.session.execute(
        "SELECT * FROM annotool.characters WHERE book_id=:book_id",
        {"book_id": book_id})

    book = dict(books[0])
    book['characters'] = result.fetchall()

    char_name_to_id = {}
    for character in book['characters']:
        char_name_to_id[character.name] = character.id

    annotations = []
    for key, value in request.form.items():
        if "role-" in key:
            annotations.append({
                "user_id": session["user_hash"],
                "char_id": char_name_to_id[key.split('-')[1]],
                "role": value
            })

    
    sql = "INSERT INTO annotool.role_annotations (user_id, char_id, role) VALUES (:user_id, :char_id, :role)"
    db.session.execute(sql, annotations)
    db.session.commit()
    return redirect("/books", code=302)

@app.route("/admin/login", methods=["POST"])
def admin_login():
    user = request.form["user"]
    pwd = request.form["pwd"]
    if user == getenv("ADMIN_USER") and pwd == getenv("ADMIN_PASSWORD"):
        print("Logged in")
        session["is_admin"] = True
    return redirect("/admin", code=302)

@app.route("/admin/")
def admin():
    # GET
    # Import books and view configuration parameters for 
    # the prioritization and annotation cap

    book_importer = BookImporter(db, master_mode)
    
    return render_template(
        "admin.html", 
        is_admin=session.get("is_admin", False), 
        import_list=book_importer.parse_book_import_list())
    # PUT 
    # change the parameters

@app.route("/admin/books", methods=["POST"])
def admin_book():
    if not session.get("is_admin", False):
        return "Unauthorized"
    # GET
    # View of annotation counts per book and paragraphs

    # POST
    # Allows admin to submit new books and proposed list of characters
    book_importer = BookImporter(db, master_mode)
    book_res_id = book_importer.import_book(request.form["book-id"])
    if book_res_id < 0:
        return "Invalid book id"

    return redirect("/books?book_id=" + str(book_res_id), code=302)


@app.route("/admin/users")
def admin_user():
    # GET / PUT
    # Allows admin to view and change the users reliability ratings
    return "Admin user"