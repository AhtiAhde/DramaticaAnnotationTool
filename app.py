from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

import uuid

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///postgres"
db = SQLAlchemy(app)

@app.route("/")
def index():
    # User should get anonymous but persistent token
    return "Heipparallaa!"

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
    db.session.execute(sql, {"user_id":uuid.uuid4(), "name":name, "role":role})
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