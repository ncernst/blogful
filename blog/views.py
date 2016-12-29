from flask import render_template, request, redirect, url_for

from . import app
from .database import session, Entry

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
def add_entry_get():
    return render_template("add_entry.html")

@app.route("/entry/add", methods=["POST"])
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
    )
    session.add(entry)
    session.commit()
    return redirect(url_for('entries', page = 1))
    
@app.route("/entry/<int:id>")
def go_to_entry(id):
    
    entry = session.query(Entry).filter(Entry.id == id).first()
    
    return render_template("go_to_entry.html", entry = entry)
    
@app.route("/entry/edit/<int:id>", methods=["GET"])
def edit_entry_get(id):
    
    entry = session.query(Entry).filter(Entry.id == id).first()
    return render_template("edit_entry.html", entry = entry)
    
@app.route("/entry/edit/<int:id>", methods=["POST"])
def edit_entry_post(id):
    
    entry = session.query(Entry).filter(Entry.id == id).first()
    
    entry.title = request.form["title"]
    entry.content=request.form["content"]

    session.commit()
    
    return redirect(url_for('go_to_entry', id = id))

@app.route("/entry/delete/<int:id>", methods=["GET"])
def delete_entry_get(id):
    
    entry = session.query(Entry).filter(Entry.id == id).first()
    
    return render_template('delete_entry.html', entry = entry)
    
@app.route("/entry/delete/<int:id>", methods=["POST"])
def delete_entry(id):
    
    entry = session.query(Entry).filter(Entry.id == id).first()
    session.delete(entry)
    session.commit()
    
    return redirect(url_for('entries'))
    
