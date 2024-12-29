from flask import Flask, flash, redirect, render_template, request, session
from cs50 import SQL
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import threading
import time
from tkinter import messagebox


app = Flask(__name__)


# Configuring session 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#configuring database with cs50 library
db = SQL("sqlite:///app.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#welcome page route
@app.route("/")
def index():
    return render_template("index.html")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user") is None:
            flash('You need to log in first.', 'warning')
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def err(message, page):
    return render_template(page, err_message=message)


def timer(stopTime, operation):
    def wait_and_execute():
        try:
            
            stop_time = datetime.strptime(stopTime, '%Y-%m-%dT%H:%M')

           
            while datetime.now() < stop_time:
                time.sleep(1)

            
            operation()
        except Exception as e:
            print(f"Error in timer thread: {e}")

   
    thread = threading.Thread(target=wait_and_execute, daemon=True)
    thread.start()


def timer2(startTime, operation):
    def wait_and_execute():
        try:
            
            start_time = datetime.strptime(startTime, '%Y-%m-%dT%H:%M')

            while datetime.now() < start_time:
                time.sleep(1)
           
            operation()
        except Exception as e:
            print(f"Error in timer thread: {e}")

   
    thread = threading.Thread(target=wait_and_execute, daemon=True)
    thread.start()


@app.route("/login", methods=["GET", "POST"])
def login():
    """view login page"""
    if request.method == "GET":
        # Forget any user_id
        session.clear()
        return render_template("login.html")
    
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email == "" or password == "":
            return err("input fields", "login.html")
        
        user = db.execute("SELECT * FROM users WHERE email IN (?)", email)

        if len(user) != 1 or not check_password_hash(user[0]["passwordHash"], password):
            return err("incorrect email or password", "login.html")
        
        else:
            session["user"] = user[0]["Id"]

            if user[0]["acctType"] == "admin":
                return redirect("/a_panel")

            return redirect("/s_panel")
        


@app.route("/m_login", methods=["GET", "POST"])
def loginM():
    """view login page"""
    if request.method == "GET":
        # Forget any user_id
        session.clear()
        return render_template("loginM.html")
    
    elif request.method == "POST":
        matric = request.form.get("matricNo")
        password = request.form.get("password")

        if matric == "" or password == "":
            return err("input fields", "loginM.html")
        
        user = db.execute("SELECT * FROM users WHERE matric IN (?)", matric)

        if len(user) != 1 or not check_password_hash(user[0]["passwordHash"], password):
            return err("incorrect email or password", "loginM.html")
        
        else:
            session["user"] = user[0]["Id"]

            return redirect("/s_panel")

    

@app.route("/s_signup", methods=["GET", "POST"])
def signUpS():
    if request.method == "GET":
        return render_template("signupS.html")
    elif request.method == "POST":
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        email = request.form.get("email")
        matricNo = request.form.get("matricNo")
        college = request.form.get("college")
        level = request.form.get("level")
        password = request.form.get("password")
        passwordConf = request.form.get("passwordConf")

        if firstName == "" or lastName == "" or email == "" or matricNo == "" or college == "" or level == "" or password == "" or passwordConf == "":
            return err("fill all required fields", "signupS.html")
    
        users = db.execute("SELECT * FROM users WHERE email IN (?) OR matric IN (?)", email, matricNo)

        if len(users) != 0:
            return err("account already exists", "signupS.html")
        elif password != passwordConf:
            return err("confirm password correctly", "signupS.html")
        else:
            password = generate_password_hash(password)

            db.execute("INSERT INTO users (firstName, lastName, email, passwordHash, acctType, matric, college, level) VALUES(?,?,?,?,?,?,?,?)", firstName, lastName, email, password, "student", matricNo, college, level)
            return redirect("/login")
        
    




@app.route("/a_signup", methods=["GET", "POST"])
def signUpA():
    if request.method == "GET":
        return render_template("signupA.html")
    elif request.method == "POST":
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        email = request.form.get("email")
        office = request.form.get("office")
        password = request.form.get("password")
        passwordConf = request.form.get("passwordConf")

        if firstName == "" or lastName == "" or email == "" or office == "" or password == "" or passwordConf == "":
            return err("fill all required fields", "signupA.html")

        users = db.execute("SELECT * FROM users WHERE email IN (?)", email)

        if len(users) != 0:
            return err("account already exists", "signupA.html")
        elif password != passwordConf:
            return err("confirm password correctly", "signupA.html")
        else:
            password = generate_password_hash(password)

            db.execute("INSERT INTO users (firstName, lastName, email, passwordHash, acctType, office) VALUES(?,?,?,?,?,?)", firstName, lastName, email, password, "admin", office)
            return redirect("/login")



@app.route("/s_panel", methods=["GET", "POST"])
@login_required
def panelS():
    user = db.execute("SELECT * FROM Users WHERE Id IN (?)", session["user"])
    if user[0]["acctType"] == "admin":
        return redirect("/login")
    if request.method == "GET":
        election = db.execute("SELECT * FROM Election WHERE state = (?)", "ongoing")
        return render_template("panelS.html", user = user, election = election)


@app.route("/a_panel", methods=["GET", "POST"])
@login_required
def panelA():
    user = db.execute("SELECT * FROM Users WHERE Id IN (?)", session["user"])
    if user[0]["acctType"] != "admin":
        return redirect("/login")
    if request.method == "GET":
        election = db.execute("SELECT * FROM Election WHERE state = (?)", "ongoing")
        return render_template("panelA.html", user = user, election = election)
    

@app.route("/s_navigation", methods=["GET", "POST"])
@login_required
def navigationS():
    user = db.execute("SELECT * FROM Users WHERE Id IN (?)", session["user"])
    if user[0]["acctType"] == "admin":
        return redirect("/login")
    if request.method == "GET":
        return render_template("navigationS.html")
    
@app.route("/a_navigation", methods=["GET", "POST"])
@login_required
def navigationA():
    user = db.execute("SELECT * FROM Users WHERE Id IN (?)", session["user"])
    if user[0]["acctType"] != "admin":
        return redirect("/login")
    if request.method == "GET":
        return render_template("navigationA.html")
    
@app.route("/startElec", methods=["GET", "POST"])
@login_required
def startElec():
    if request.method == "GET":
        election = db.execute("SELECT * FROM Election WHERE state IN (?)", "new")

        return render_template("startElec.html", election=election)
    elif request.method == "POST":
        currentTime = datetime.now().strftime('%Y-%m-%dT%H:%M')

        post = request.form.get("post")
        start = request.form.get("start")
        end = request.form.get("end")

        if post == "" or start == "" or end == "" :
            return err("fill all required fields", "startElec.html")
        elif start < currentTime or end < currentTime or start > end:
            return err("Input valid time", "startElec.html")
        
        users = db.execute("SELECT * FROM Election WHERE post IN (?)", post)

        election = db.execute("SELECT * FROM Election WHERE state IN (?)", "new")
        
        if len(users) != 0:
            err_message = "post already exist"
            return render_template("startElec.html", election=election, err_message=err_message)

        
        

        db.execute("INSERT INTO Election (post, startTime, endTime, state) VALUES(?, ?, ?, ?)", post, start, end, "new")


        election = db.execute("SELECT * FROM Election WHERE state IN (?)", "new")

        def handleStart():
            return redirect("/beginElec")

        timer2(start, handleStart)

        return render_template("startElec.html", election=election)
    



@app.route("/beginElec", methods=["GET", "POST"])
@login_required
def beginElec():
    if request.method == "GET":
        id = request.args.get("id")

        existingElec = db.execute("SELECT * FROM Election WHERE state = ? AND Id = ?", "ongoing", int(id))

        if len(existingElec) > 0:
            flash("You have already entered this contest.", "info")
            return redirect("/startElec")
        
        db.execute("UPDATE Election SET state = (?) WHERE Id = (?)", "ongoing", int(id))

        election = db.execute("SELECT * FROM Election WHERE state = (?) AND Id = (?)", "ongoing", int(id))

        def ended():
            db.execute("UPDATE Election SET state = (?) WHERE Id = (?)", "ended", int(id))

            election = db.execute("SELECT * from Election WHERE Id = (?)", int(id))
            if int(election[0]["contestants"]) == 0:
                db.execute("DELETE FROM Election WHERE Id = (?)", int(id))

        timer(election[0]["endTime"], ended)

        election = db.execute("SELECT * FROM Election WHERE state IN (?)", "new")

        return render_template("startElec.html", election=election)

        

@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    if request.method == "GET":
        user = db.execute("SELECT * FROM Users WHERE Id IN (?)", session["user"])
        if user[0]["acctType"] == "admin":
            return redirect("/login")
        
        candidate = db.execute("SELECT * FROM Candidates WHERE user IN (?)", session["user"])
        election = db.execute("SELECT * FROM Election WHERE state IN (?)", "new")

        contestedIds = {row['election'] for row in candidate}
        return render_template("post.html", election=election, candidate=candidate, contestedIds=contestedIds)
    

@app.route("/contest", methods=["GET", "POST"])
@login_required
def contest():
    if request.method == "GET":
        elecId = request.args.get("elecId")

        election = db.execute("SELECT * FROM Election WHERE Id IN (?)", elecId)

        if len(election) == 0:
            flash("NO open posts", "error") 
            return redirect("/post")

        election = election[0]

        existingCandidate = db.execute("SELECT * FROM Candidates WHERE user IN (?) AND election IN (?)", session["user"], elecId)

        if len(existingCandidate) > 0:
            flash("You have already entered this contest.", "info")
            return redirect("/post")

        db.execute("UPDATE Election SET contestants = (?) WHERE Id IN (?)", election["contestants"] + 1, elecId)

        db.execute("INSERT INTO Candidates (user, state, election) VALUES(?, ?, ?)", session["user"], "active", elecId)

        candidate = db.execute("SELECT * FROM Candidates WHERE user IN (?)", session["user"])
        election = db.execute("SELECT * FROM Election WHERE state IN (?)", "new")

        contestedIds = {row['election'] for row in candidate}

        return render_template("post.html", election=election, contestedIds=contestedIds)


@app.route("/activeElecS", methods=["GET", "POST"])
@login_required
def activeElecS():
    user = db.execute("SELECT * FROM Users WHERE Id IN (?)", session["user"])
    if user[0]["acctType"] == "admin":
        return redirect("/login")

    if request.method == "GET":

        election = db.execute("SELECT * FROM Election WHERE state = (?)", "ongoing")

        candidates = db.execute("SELECT * FROM Candidates")

        users = db.execute("SELECT * FROM Users")
        
        elecCand = []

        for election_row in election:
            election_id = election_row['Id']  

            associated_candidates = []

            for candidate_row in candidates:

                for user in users:
        
                    if candidate_row['election'] == election_id:  
                        if user["Id"] == candidate_row['user']:

                            associated_candidates.append({'candidateRow':candidate_row,  'user': user})  

           
            elecCand.append({'election': election_row, 'candidates': associated_candidates})

        votes = election = db.execute("SELECT * FROM Votes WHERE user IN (?)", session["user"])


        return render_template("activeElecS.html", elecCand = elecCand, vote = votes)



    
    if request.method == "POST":

        elecId = request.form.get("elecId")
        candId = request.form.get("candId")

        votes = db.execute("SELECT * FROM Votes Where election = (?) AND user = (?)", elecId, candId)

        if len(votes) == 0:

            elecId = request.form.get("elecId")
            candId = request.form.get("candId")

            votes = db.execute("SELECT * FROM Votes WHERE user IN (?) AND election IN (?)", session["user"], elecId)

            if len(votes) != 0:

                return render_template("activeElecS.html", elecCand = elecCand, voted = True)
            else: 
                voteCount = db.execute("SELECT votes FROM Candidates WHERE user = (?) AND election IN (?)", candId, elecId)
                db.execute("INSERT INTO Votes (user, election) VALUES(?, ?)", session["user"], elecId)
                db.execute("UPDATE Candidates SET votes = (?) WHERE user IN (?) AND election IN (?)",voteCount[0]['votes'] + 1 , candId, elecId)

                election = db.execute("SELECT * FROM Election WHERE state = (?)", "ongoing")

                candidates = db.execute("SELECT * FROM Candidates")
                users = db.execute("SELECT * FROM Users")

                elecCand = []
                for election_row in election:
                    election_id = election_row['Id']  
                    associated_candidates = []
                    for candidate_row in candidates:
                        for user in users:
                        
                            if candidate_row['election'] == election_id:  
                                if user["Id"] == candidate_row['user']:
                                    associated_candidates.append({'candidateRow':candidate_row,  'user': user})  

                    elecCand.append({'election': election_row, 'candidates': associated_candidates})

                return render_template("activeElecS.html", elecCand = elecCand, user= user, voted = True)

        else:
            voteCount = db.execute("SELECT votes FROM Candidates WHERE user = (?) AND election IN (?)", candId, elecId)

            db.execute("DELETE FROM Votes WHERE election IN (?) AND user IN (?)", elecId, session["user"])
            db.execute("UPDATE Candidates SET votes = (?) WHERE user IN (?) AND election IN (?)",voteCount[0]['votes'] - 1 , candId, elecId)
            election = db.execute("SELECT * FROM Election WHERE state = (?)", "ongoing")
            candidates = db.execute("SELECT * FROM Candidates")
            users = db.execute("SELECT * FROM Users")

            elecCand = []
            for election_row in election:
                election_id = election_row['Id']  
                associated_candidates = []
                for candidate_row in candidates:
                    for user in users:
                    
                        if candidate_row['election'] == election_id:  
                            if user["Id"] == candidate_row['user']:
                                associated_candidates.append({'candidateRow':candidate_row,  'user': user})  
                elecCand.append({'election': election_row, 'candidates': associated_candidates})

            return render_template("activeElecS.html", elecCand = elecCand, user= user, voted = False)


@app.route("/activeElecA", methods=["GET", "POST"])
@login_required
def activeElecA():
    user = db.execute("SELECT * FROM Users WHERE Id IN (?)", session["user"])
    if user[0]["acctType"] != "admin":
        return redirect("/login")

    if request.method == "GET":

        election = db.execute("SELECT * FROM Election WHERE state = (?)", "ongoing")

        candidates = db.execute("SELECT * FROM Candidates")

        users = db.execute("SELECT * FROM Users")
        
        elecCand = []

        for election_row in election:
            election_id = election_row['Id']  

            associated_candidates = []

            for candidate_row in candidates:

                for user in users:
        
                    if candidate_row['election'] == election_id:  
                        if user["Id"] == candidate_row['user']:

                            associated_candidates.append({'candidateRow':candidate_row,  'user': user})  

           
            elecCand.append({'election': election_row, 'candidates': associated_candidates})

        votes = election = db.execute("SELECT * FROM Votes WHERE user IN (?)", session["user"])


        return render_template("activeElecA.html", elecCand = elecCand, vote = votes)



    
    if request.method == "POST":

        elecId = request.form.get("elecId")
        candId = request.form.get("candId")

        db.execute("DELETE FROM Candidates WHERE user IN (?) AND election IN (?)", candId, elecId)

        

        return redirect("/activeElecA")


@app.route("/resultS", methods=["GET", "POST"])
@login_required
def resultS():
    user = db.execute("SELECT * FROM Users WHERE Id IN (?)", session["user"])
    if user[0]["acctType"] == "admin":
        return redirect("/login")
    try:
        
        endedElections = db.execute("SELECT Id, post FROM Election WHERE state = ?", "ended")
       
        election_top_candidates = []

        for election in endedElections:
            election_id = election["Id"]
            election_post = election["post"]

           
            top_candidate = db.execute("""
                SELECT C.Id AS candidate_id, C.user AS user_id, C.votes 
                FROM Candidates C 
                WHERE C.election = ? 
                ORDER BY C.votes DESC 
                LIMIT 1
            """, election_id)

            if top_candidate:
                top_candidate = top_candidate[0]
                user_id = top_candidate["user_id"]

               
                user_details = db.execute("""
                    SELECT firstName, lastName, email, matric, college, office, level 
                    FROM Users 
                    WHERE Id = ?
                """, user_id)

                if user_details:
                    user_details = user_details[0]
                    election_top_candidates.append({
                        "election_id": election_id,
                        "election_post": election_post,
                        "candidate_id": top_candidate["candidate_id"],
                        "user_id": top_candidate["user_id"],
                        "votes": top_candidate["votes"],
                        "user_details": {
                            "firstName": user_details["firstName"],
                            "lastName": user_details["lastName"],
                            "email": user_details["email"],
                            "matric": user_details["matric"],
                            "college": user_details["college"],
                            "office": user_details["office"],
                            "level": user_details["level"],
                        }
                    })
       
        return render_template("resultS.html", election_top_candidates=election_top_candidates)

    except Exception as e:
        print(f"Error in result route: {e}")
        return redirect("/login")


@app.route("/resultA", methods=["GET", "POST"])
@login_required
def resultA():

    if request.method == "GET":
        user = db.execute("SELECT * FROM Users WHERE Id IN (?)", session["user"])
        if user[0]["acctType"] != "admin":
            return redirect("/login")
        try:
        
            endedElections = db.execute("SELECT Id, post FROM Election WHERE state = ?", "ended")

            election_top_candidates = []

            for election in endedElections:
                election_id = election["Id"]
                election_post = election["post"]


                top_candidate = db.execute("""
                    SELECT C.Id AS candidate_id, C.user AS user_id, C.votes 
                    FROM Candidates C 
                    WHERE C.election = ? 
                    ORDER BY C.votes DESC 
                    LIMIT 1
                """, election_id)

                if top_candidate:
                    top_candidate = top_candidate[0]
                    user_id = top_candidate["user_id"]


                    user_details = db.execute("""
                        SELECT firstName, lastName, email, matric, college, office, level 
                        FROM Users 
                        WHERE Id = ?
                    """, user_id)

                    if user_details:
                        user_details = user_details[0]
                        election_top_candidates.append({
                            "election_id": election_id,
                            "election_post": election_post,
                            "candidate_id": top_candidate["candidate_id"],
                            "user_id": top_candidate["user_id"],
                            "votes": top_candidate["votes"],
                            "user_details": {
                                "firstName": user_details["firstName"],
                                "lastName": user_details["lastName"],
                                "email": user_details["email"],
                                "matric": user_details["matric"],
                                "college": user_details["college"],
                                "office": user_details["office"],
                                "level": user_details["level"],
                            }
                        })

            return render_template("resultA.html", election_top_candidates=election_top_candidates)

        except Exception as e:
            print(f"Error in result route: {e}")
            return redirect("/login")


    if request.method == "POST":

        elecId = request.form.get("elecId")

        db.execute("DELETE FROM Candidates WHERE election IN (?)", elecId)
        db.execute("DELETE FROM Votes WHERE election IN (?)", elecId)
        db.execute("DELETE FROM Election WHERE Id IN (?)", elecId)
        return redirect("/startElec")



@app.route("/users", methods=["GET", "POST"])
@login_required
def users():

    admin = db.execute("SELECT * FROM Users WHERE acctType IN (?)", "admin")
    students = db.execute("SELECT * FROM Users WHERE acctType IN (?)", "student")
    return render_template("users.html", admin=admin, students=students)


@app.route("/acctS", methods=["GET", "POST"])
@login_required
def acctS():
    user = db.execute("SELECT * FROM Users WHERE Id IN (?)", session["user"])
    if user[0]["acctType"] == "admin":
        return redirect("/login")
    if request.method == "GET":
        user = db.execute("SELECT * FROM Users WHERE Id IN (?)", session["user"])

        return render_template("acctS.html", user=user)

    elif request.method == "POST":
        db.execute("DELETE FROM Votes WHERE user IN (?)", session["user"])
        db.execute("DELETE FROM Candidates WHERE user IN (?)", session["user"])
        db.execute("DELETE FROM Users WHERE Id IN (?)", session["user"])

        return redirect("/")



@app.route("/acctA", methods=["GET", "POST"])
@login_required
def acctA():
    user = db.execute("SELECT * FROM Users WHERE Id IN (?)", session["user"])
    if user[0]["acctType"] != "admin":
        return redirect("/login")
    if request.method == "GET":
        user = db.execute("SELECT * FROM Users WHERE Id IN (?)", session["user"])

        return render_template("acctA.html", user=user)

    elif request.method == "POST":
        db.execute("DELETE FROM Votes WHERE user IN (?)", session["user"])
        db.execute("DELETE FROM Candidates WHERE user IN (?)", session["user"])
        db.execute("DELETE FROM Users WHERE Id IN (?)", session["user"])

        return redirect("/")

if __name__ == "__main__":
    app.run(debug=False)