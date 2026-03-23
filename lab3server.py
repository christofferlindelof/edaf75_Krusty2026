from bottle import get, post, run, request, response
import sqlite3
db = sqlite3.connect('movies.sqlite')


#Checks that service is running
@get('/ping')
def ping():
    return "pong"



#empties database and enters some theaters
@post('/reset')
def reset():
    c = db.cursor()
    sql_commands = open("schema.sql","r").read()
    c.executescript(sql_commands) #Emptying

    #inserting.
    c.execute("INSERT INTO theaters (name, capacity) VALUES ('Kino', 10)")
    c.execute("INSERT INTO theaters (name, capacity) VALUES ('Regal', 16)")
    c.execute("INSERT INTO theaters (name, capacity) VALUES ('Skandia', 100)")

    db.commit()

#post new user, using request body. 
@post('/users')
def postUser():
    inData = request.json
    
    #Extract values with get()
    username = inData.get('username')
    fullName = inData.get('fullName')
    pwd = inData.get('pwd')

    #Try adding to database
    try:
        c = db.cursor()
        c.execute("INSERT INTO customers (username, fullName, pwd) VALUES (?,?,?)", 
              (username, fullName, pwd)
              )
        db.commit()
        response.status = 201 #created successfully
        return "/users/" + username
    
    except: 
        response.status = 400 #post unsuccessfull
        return("")
    

#post new movie
@post('/movies')
def postMovie():
    inData = request.json
    #Extract data from post with get()
    imdbKey = inData.get('imdbKey')
    title = inData.get('title')
    productionYear = int(inData.get('year'))

    try: 
        c = db.cursor()
        c.execute("INSERT INTO movies (title, imdbKey, productionYear) VALUES (?, ?, ?)",
                  (title, imdbKey, productionYear))
        db.commit()
        response.status = 201
        return "/movies/" + imdbKey

    except:
        response.status = 400
        return("")
    
    #post new PERFORMANCE
@post('/performances')
def postPerformance():
    inData = request.json
    #Extract data from post with get()
    imdbKey = inData.get('imdbKey')
    theaterName = inData.get('theater')
    date = inData.get('date')
    startTime = inData.get('time')
    c = db.cursor()

    #hämtar capacity från teater
    c.execute("SELECT capacity FROM theaters WHERE name = ?",
              (theaterName,))
    t_result = c.fetchone()

    #kontrollera att filmen finns
    c.execute("SELECT 1 FROM movies WHERE imdbKey = ?",
              (imdbKey,))
    m_result = c.fetchone()

    if not t_result or not m_result:
        response.status = 400
        return "No such movie or theater"
    
    capacity = t_result[0]


    try: 
        c.execute('''INSERT INTO performances (imdbKey, theaterName, date, startTime, remainingSeats)  
                    VALUES (?, ?, ?, ?, ?) RETURNING performanceId''',
                  (imdbKey, theaterName, date, startTime, capacity))
        
        row = c.fetchone() #fångar upp returnerat performanceID - men rad? osäker på detta.
        performanceId = row[0]
        
        db.commit()
       
        response.status = 201
        return "/performances/" + performanceId

    except:
        response.status = 400
        return("No such movie or theater")
    
#return the movies
@get('/movies')
def getMovie():
    c = db.cursor()
    c.execute('''SELECT imdbKey, title, productionYear FROM movies''')
    movies = c.fetchall()

    movie_list = []

    for line in movies:
        imdb_key = line[0]
        title = line[1]
        year = line[2]

        d = {
            "imdbKey": imdb_key,
            "title": title,
            "year": year
        }

        movie_list.append(d)

    return {"data": movie_list}

@get('/movies/<imdb_key>')
def getMovieByImdbKey(imdb_key):
    c = db.cursor()
    c.execute("SELECT imdbKey, title, productionYear FROM movies WHERE imdbKey = ?",
              (imdb_key,))
    result = c.fetchone() 
    movie_list = []

    if not result: 
        return{"data": movie_list}


    imdb_key = result[0]
    title = result[1]
    year = result[2]
    
    d = {
            "imdbKey": imdb_key,
            "title": title,
            "year": year
        }
    movie_list.append(d)
    return {"data": movie_list}

@get('/performances')
def getPerformances():
    c = db.cursor()
    c.execute(
        '''SELECT performanceId, date, startTime, title, productionYear, theaterName, remainingSeats
            FROM performances p 
            JOIN movies m ON p.imdbKey = m.imdbKey''') #using
    result=c.fetchall()

    performance_list = []

    if not result: 
        return{"data": performance_list}


    for line in result:
        performanceId = line[0]
        date= line[1]
        startTime = line[2]
        title = line[3]
        year = line[4]
        theater = line[5]
        remainingSeats = line[6]

        d = {
            "performanceId": performanceId,
            "date": date,
            "startTime": startTime,
            "title": title,
            "year": year,
            "theater": theater,
            "remainingSeats": remainingSeats
        }

        performance_list.append(d)

    return {"data": performance_list}
@post('/tickets') #Try buy ticket.. Meaning: See if tickets available for performance. Create ticket. Decrease available seats. 
def buyTicket():
    inData = request.json
    username = inData.get('username')
    pwd = inData.get('pwd')
    performanceId = inData.get('performanceId')
    c = db.cursor()

    c.execute("SELECT fullName FROM customers WHERE username = ? AND pwd = ?",
              (username, pwd,))
    result = c.fetchone()
    if not result: 
        response.status = 401
        return("Wrong user credentials")
    

    try: 
        c.execute('''
                  UPDATE performances 
                  SET remainingSeats = remainingSeats-1
                  WHERE performanceId = ? AND remainingSeats > 0''',
                  (performanceId,))
        if c.rowcount == 0:
            response.status = 400
            return("No tickets left")
        #Om detta funka så skapar vi biljett

        c.execute('''
                  INSERT INTO tickets (username, startTime, date, theaterName) 
                  SELECT ?, startTime, date, theaterName
                  FROM performances 
                  WHERE performanceId = ?
                  RETURNING uuid''',
                  (username, performanceId))
        row = c.fetchone() 
        uuid = row[0]

        db.commit()
        response.status = 201
        return "/tickets/" + uuid
 



    except: 
        db.rollback() #backa om något kraschat i sqlen 
        response.status = 400
        return("Error")
    


@get('/users/<username>/tickets')
def getTicketsOfUsers(username):
    c = db.cursor()
    c.execute('''
              SELECT t.date, t.startTime, t.theaterName, m.title, m.productionYear, count(*) AS nbrOfTickets
              FROM tickets t
              JOIN performances p ON 
              t.date = p.date AND
              t.theaterName = p.theaterName AND
              t.startTime = p.startTime
              JOIN movies m ON p.imdbKey = m.imdbKey
              WHERE t.username = ?
              GROUP BY t.date, t.startTime, t.theaterName
              ''',
              (username,)) #title, productionYear från movies, joinar in dessa bara? nbrOfTickets, en count efter group?? 
    result=c.fetchall()
    ticket_list = []
    for line in result:
        date = line[0]
        startTime= line[1]
        theater = line[2]
        title = line[3]
        year = line[4]
        nbrOfTickets = line[5]

        d = {
            "date": date,
            "startTime": startTime,
            "theater": theater,
            "title": title,
            "year": year,
            "nbrOfTickets": nbrOfTickets,
        }

        ticket_list.append(d)

    return {"data": ticket_list}
    





#run server
run(host='localhost', port=7007)
