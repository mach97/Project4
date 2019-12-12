from flask import Flask, render_template,request,session,jsonify,redirect,url_for
from flask_session import Session
import requests
import os
from required import login_required
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


app = Flask(__name__)

app.config["SESSION_PERMANENT"]= False
app.config["SESSION_TYPE"]="filesystem"
Session(app)



#print(res.json())

@app.route("/")
@login_required
def index():
        return render_template("books.html")

@app.route("/signin")
def index1():
    if not session.get('logged_in'):
        return render_template("signin.html")
    else:
        return render_template("books.html")



@app.route("/main",methods=["POST","GET"])
def signin():
    if request.method=="POST":
        uname = request.form.get("uname")
        name = request.form.get("name")
        lname = request.form.get("lname")
        email = request.form.get("inputEmail")
        password = request.form.get("inputPassword")
        bdate = request.form.get("bdate")

        if db.execute("SELECT username FROM usuario WHERE username=:user",{"user":uname}).rowcount != 0:
            return render_template("error.html", message="Username already exists")
        elif db.execute("SELECT username FROM usuario WHERE email=:user",{"user":email}).rowcount != 0:
            return render_template("error.html", message="Email already exists")
        db.execute("INSERT INTO usuario VALUES (:uname,:name,:lname,:email,:bdate,:password)",{"uname":uname,"name":name,"lname":lname,"email":email,"bdate":bdate,"password":password})
        db.commit()
        return redirect("/")
    else:
        return render_template("signin.html")

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method=="POST":
        print("aaaaaaaaaaaaaaa")
        uname = request.form.get("uname")
        password = request.form.get("Password")

        if db.execute("SELECT * FROM usuario where username = :uname and password=:password",{"uname":uname,"password":password}).rowcount != 0:
            session['logged_in']=True
            session['user']=uname
            print(session['user'])
            return redirect("/")
        else:
            return render_template("error.html",message="Username or Password incorrect")
    else:
        return render_template("index.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/search",methods=["POST","GET"])
@login_required
def search():
    text = '%'+request.form.get("search")+'%'
    recipes = db.execute("SELECT * FROM recipe WHERE (lower(name) LIKE :name)", {"name":text}).fetchall()
    return render_template("search.html", recipes=recipes, search=text)

@app.route("/details/<string:id>",methods=["GET","POST"])
@login_required
def details(id):
    id, name, minutes, n_steps, description, n_ingredients = db.execute("SELECT id, INITCAP(name), minutes, n_steps, description, n_ingredients FROM recipe WHERE id = :id", {"id": id}).fetchone()
    ingredients = db.execute("SELECT INITCAP(ingredient) as ingredient from recipe_ingredient where id=:id",{"id":id}).fetchall()
    steps = db.execute("SELECT description from recipe_steps where id=:id",{"id":id}).fetchall()

    description=description.capitalize()

    if request.method=="GET":
        if not session.get('logged_in'):
            return render_template("index.html")
        else:
            return render_template("details.html",name=name, description=description,minutes=minutes,ingredients=ingredients,steps=steps)
    else:
        if not session.get('logged_in'):
            render_template("index.html")
        else:
            return render_template("details.html",name=name, description=description, minutes=minutes,ingredients=ingredients,steps=steps)

@app.route("/insert",methods=["GET","POST"])
@login_required
def insert():
    if request.method=="GET":
        return render_template("insert.html")
    else:
        id=db.execute("SELECT max(id) as id from recipe").fetchone()
        id=id.id+1
        print(id)
        name=request.form.get("name")
        description=request.form.get("description")
        minutes=request.form.get("minutes")
        ningredients=request.form.get("ningredients")
        ing=[]
        nsteps=request.form.get("nsteps")
        step=[]
        ing.append(request.form.get("1"))
        ing.append(request.form.get("2"))
        ing.append(request.form.get("3"))
        ing.append(request.form.get("4"))
        ing.append(request.form.get("5"))
        step.append(request.form.get("6"))
        step.append(request.form.get("7"))
        step.append(request.form.get("8"))
        step.append(request.form.get("9"))
        step.append(request.form.get("10"))
        print(ing)
        print(step)

        db.execute("INSERT into recipe values(:id,:name,:minutes,:n_steps,:description,:n_ingredients)",{"id":id,"name":name,"minutes":minutes,"n_steps":nsteps,"description":description,"n_ingredients":ningredients})
        for i in range(int(ningredients)):
            db.execute("INSERT INTO recipe_ingredient values (:id,:ingredient)",{"id":id,"ingredient":ing[i]})
        for i in range(int(nsteps)):
            db.execute("INSERT INTO recipe_steps values (:id,:step,:description)",{"id":id,"step":i,"description":step[i]})

        db.commit()

        return redirect(url_for('index'))
