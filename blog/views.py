from flask import render_template, request, redirect, url_for, flash
from flask.ext.login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash

from . import app
from .database import session, Entry, User

PAGINATE_BY = 10


@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
    #zero-indexed page
    page_index = page-1

    count = session.query(Entry).count()
    
    
    if request.args.get('limit') != None and request.args.get('limit').isdigit():
        page_limit = int(request.args.get('limit')) 
        if page_limit == 0:
            page_limit = PAGINATE_BY
        elif page_limit > 100:
            page_limit = 100
    else:   
        page_limit = PAGINATE_BY
    
    start = page_index * page_limit
    end = start + page_limit
    
    total_pages = (count-1) // page_limit + 1
    has_next = page_index < total_pages-1
    has_prev = page_index > 0
    
    
    
    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]
    
    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )

@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")

@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for('entries', page = 1))
    
@app.route("/entry/<int:id>")
def go_to_entry(id):
    
    entry = session.query(Entry).filter(Entry.id == id).first()
    
    return render_template("go_to_entry.html", entry = entry)
    
@app.route("/entry/edit/<int:id>", methods=["GET"])
@login_required
def edit_entry_get(id):
    
    entry = session.query(Entry).filter(Entry.id == id).first()
    
    if current_user.id == entry.author.id:
        return render_template("edit_entry.html", entry = entry)
    
    else:
        flash("You are not authorized to modify that post.", "danger")
        return redirect(url_for("entries"))
    
@app.route("/entry/edit/<int:id>", methods=["POST"])
@login_required
def edit_entry_post(id):
    
    entry = session.query(Entry).filter(Entry.id == id).first()
    if current_user.id == entry.author.id:
        entry.title = request.form["title"]
        entry.content=request.form["content"]
        session.commit()
        return redirect(url_for('go_to_entry', id = id))
    
    else:
        flash("You are not authorized to modify that post.", "danger")
        return redirect(url_for("entries"))

@app.route("/entry/delete/<int:id>", methods=["GET"])
@login_required
def delete_entry_get(id):
    
    entry = session.query(Entry).filter(Entry.id == id).first()
    
    return render_template('delete_entry.html', entry = entry)
    
@app.route("/entry/delete/<int:id>", methods=["POST"])
@login_required
def delete_entry(id):
    
    entry = session.query(Entry).filter(Entry.id == id).first()
    session.delete(entry)
    session.commit()
    
    return redirect(url_for('entries'))


@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email = email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))
    
    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))
    
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("entries"))
