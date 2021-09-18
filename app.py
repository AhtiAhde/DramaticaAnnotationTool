from flask import Flask
from flask import render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    # User should get anonymous but persistent token
    return "Heipparallaa!"

@app.route("/task/<int:b_id>/<int:p_id>")
def tasks():
    # Random task list, prioritized by the admins
    # Two modes, character role annotation (b_id) and character 
    # behavior annotation in paragraphs (p_id)
    # We will first implement the character role annotation
    # The resource list link gives a redirect to one task
    return "Taaskeja"

@app.route("/book", methods=["GET"])
def book():
    # GET
    # This route should take user to the book view
    # The view would include the character annotations
    # And also provide access to paragraphs, perhaps paginated view
    book = {
        "id": 1,
        "name": "example",
        "characters": [
            {
                "name": "Jack",
                "role": "protagonist"
            },
            {
                "name": "Santa",
                "role": None
            }
        ]
    }
    return render_template("book.html", message="book view", book=book)

@app.route("/book", methods=["POST"])
def character_roles():
    # POST
    # Allows to add characters; this might be own resouce that is a
    # list object of suggested characters and their roles
    book = {
        "id": 1,
        "name": "example",
        "characters": [
            {
                "name": "Jack",
                "role": "protagonist"
            },
            {
                "name": "Santa",
                "role": request.form["role"]
            }
        ]
    }
    return render_template("book.html", message="book view", book=book)

@app.route("/admin/")
def admin():
    # GET
    # View configuration parameters for the prioritization and annotation cap

    # PUT 
    # change the parameters
    return "Admin"

@app.route("/admin/book")
def admin_book():
    # GET
    # View of annotation counts per book and paragraphs

    # POST
    # Allows admin to submit new books and proposed list of characters

    # PUT 
    # change the book / paragraph priorities
    return "Admin book"


@app.route("/admin/user")
def admin_user():
    # GET / PUT
    # Allows admin to view and change the users reliability ratings
    return "Admin user"