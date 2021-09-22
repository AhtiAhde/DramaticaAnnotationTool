from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv

import uuid
import os
from os import getenv

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
    # View configuration parameters for the prioritization and annotation cap

    # PUT 
    # change the parameters
    return "Admin"

@app.route("/admin/books")
def admin_book():
    # GET
    # View of annotation counts per book and paragraphs

    # POST
    # Allows admin to submit new books and proposed list of characters

    # PUT 
    # change the book / paragraph priorities
    return "Admin book"


@app.route("/admin/users")
def admin_user():
    # GET / PUT
    # Allows admin to view and change the users reliability ratings
    return "Admin user"