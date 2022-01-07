from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv

import uuid
import os
from os import getenv

from modules.book_importer import BookImporter
from modules.book import Book

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

@app.route("/tasks/<int:b_id>", methods=["GET"])
@app.route("/tasks/<int:b_id>/<int:p_id>", methods=["GET"])
def tasks(b_id, p_id=-1):
    # Random task list, prioritized by the admins
    # Two modes, character role annotation (b_id) and character 
    # behavior annotation in paragraphs (p_id)
    # We will first implement the character role annotation
    # The resource list link gives a redirect to one task
    book_obj = Book(db)

    if p_id == -1:
        p_id = book_obj.get_random_paragraph(b_id)
        return redirect("/tasks/" + str(b_id) + "/" + str(p_id), code=302)
    
    paragraph = book_obj.get_paragraph(b_id, p_id).content
    return render_template(
        "task.html", 
        message="Tasks", 
        user=session["user_hash"],
        b_id=b_id,
        p_id=p_id,
        paragraph=paragraph)
    

@app.route("/books", methods=["GET"])
@app.route("/books/<int:book_id>", methods=["GET"])
def book(book_id=-1):
    # GET
    # This route should take user to the book view
    # The view would include the character annotations
    # And also provide access to paragraphs, perhaps paginated view
    book = False
    books = False
    roles = []
    book_obj = Book(db)
    if book_id > -1:
        # Notice that the unannotated characters are cast to 'Unknown' role
        # at Jinja template 
        book = book_obj.parse_characters(book_id, session['user_hash'])
        roles = book['roles']
    else:
        books = book_obj.list_books()
    
    return render_template("book.html", 
        message="book view", 
        books=books, 
        book=book, 
        roles=roles
    )

@app.route("/books/<int:book_id>", methods=["POST"])
def character_roles(book_id):
    # POST
    # Allows to add characters; this might be own resouce that is a
    # list object of suggested characters and their roles
    book = Book(db)
    book.write_role_annotations(
        book_id, 
        session["user_hash"], 
        request.form.items()
    )
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