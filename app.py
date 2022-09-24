from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv

import uuid
import os
from os import getenv

from modules.book_importer import BookImporter
from modules.book import Book
from modules.arc import Arc
from modules.auth import Auth

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
    if not "user_hash" in session:
        sql = "INSERT INTO user_sessions (id) VALUES (:id) RETURNING id"
        result = db.session.execute(sql, {"id":uuid.uuid4()})
        db.session.commit()
        session["user_hash"] = result.fetchone()[0]
    
    return render_template("index.html", message="index", user=session["user_hash"], email=session.get("email", False))

@app.route("/tasks/<int:b_id>", methods=["GET"])
@app.route("/tasks/<int:b_id>/<int:p_id>", methods=["GET"])
@app.route("/tasks/<int:b_id>/<int:p_id>/<int:arc_id>", methods=["GET"])
def tasks(b_id, p_id=-1, arc_id=-1):
    # Random task list, prioritized by the admins
    # Two modes, character role annotation (b_id) and character 
    # behavior annotation in paragraphs (p_id)
    # We will first implement the character role annotation
    # The resource list link gives a redirect to one task
    book_obj = Book(db)
    arc_obj = Arc(db)
    
    if p_id == -1:
        p_id = book_obj.get_random_paragraph(b_id)
        return redirect("/tasks/" + str(b_id) + "/" + str(p_id), code=302)
    
    paragraph = book_obj.get_paragraph(b_id, p_id).content
    
    arcs = []
    arc = None
    if arc_id == -1:
        arcs = arc_obj.read_for_tasks(b_id, session['user_hash'])
    else:
        arc = arc_obj.read_arc_for_tasks(arc_id)
    
    print(arc)
    return render_template(
        "task.html", 
        message="Tasks", 
        user=session["user_hash"],
        b_id=b_id,
        p_id=p_id,
        arcs=arcs,
        arc=arc,
        paragraph=paragraph)

@app.route("/tasks/<int:b_id>/<int:p_id>/arc", methods=['POST'])
def task_arc_redicrect(b_id, p_id=-1):
    return redirect("/tasks/" + str(b_id) + "/" + str(p_id) + "/" + request.form['arc-selected'])

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
        book = book_obj.parse_book(book_id, session['user_hash'])
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

@app.route("/books/<int:book_id>/add_arc", methods=["POST"])
def add_arc(book_id):
    title = request.form['title']
    short_desc = request.form['short_desc']

    arc = Arc(db)
    arc.create(
        book_id,
        session['user_hash'],
        title,
        short_desc)
    
    return redirect("/books/" + str(book_id), code=302)


@app.route("/books/<int:book_id>/modify_arc/<int:arc_id>", methods=["POST"])
def modify_arc(book_id, arc_id):
    arc = Arc(db)
    arc.update_annotations(
        book_id,
        session['user_hash'],
        arc_id, 
        request.form
    )
    
    return redirect("/books/" + str(book_id), code=302)


@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html", 
        message="register user",
        email = request.args.get("email", default="", type=str),
        pwd_mismatch = request.args.get("pwd_mismatch", default="0", type=str)
    )

@app.route("/register", methods=["POST"])
def register_user():
    email = request.form["email"] # add email validator later
    password = request.form["password"]
    
    # Check is password and confirm password match
    confirm = request.form["confirm-password"]
    if password != confirm:
        return redirect("/register?email=" + str(email) + "&pwd_mismatch=1", code=302)

    auth = Auth(db)
    email = auth.register(email, password, session["user_hash"])
    
    if not email:
        # decide later what to do
        return render_template("register.html", message="register user failed",)

    session['email'] = email

    return redirect("/", code=302)

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"] # add email validator later
    password = request.form["password"]

    auth = Auth(db)
    email = auth.login(email, password, session["user_hash"])
    if not email:
        return render_template("index.html", message="Welcome back", invalid_auth="1")
    
    session['email'] = email

    return redirect("/", code=302)


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user_hash")
    session.pop("email")

    return redirect("/", code=302)

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