import csv
import os
import ast

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    c=0
    count=0
    f=open("RAW_recipes.csv")
    reader = csv.reader(f)
    for name,id, minutes, contributor,submitted,tags,nutriton, n_steps,steps, description,ingredients, n_ingredients in reader:
        steps=steps[1:-1].split('\', \'')
        ingredients=ingredients[2:-2].split('\', \'' or '\',\'' or '\' , \'')
        if c!=0:
            db.execute("INSERT INTO recipe values (:id,:name,:minutes,:n_steps,:description,:n_ingredients)",{"id": int(id),"name":name,"minutes":int(minutes),"n_steps":int(n_steps),"description":description,"n_ingredients":int(n_ingredients)})
            for i in range(len(ingredients)):
                db.execute("insert into recipe_ingredient values (:id, :ingredient)",{"id":int(id),"ingredient":ingredients[i]})
            for j in range(len(steps)):
                db.execute("insert into recipe_steps values (:id,:step,:description)",{"id":int(id),"step":j,"description":steps[j]})
            print("Listo")
        c+=1
        if count==500:
            break
        count+=1
    db.commit()

if __name__ == "__main__":
    main()
