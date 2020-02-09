#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://xz2466:0566@34.74.165.156/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
  print (request.args)
  return render_template("mainpage.html")


@app.route('/search_p', methods=['POST'])
def search_player():
  q1 = "SELECT pi.player_nameid,ps.id,ps.name,ps.country,pi.role,pi.status,pi.birthday,pi.years_pro,pi.earnings,pi.followers"
  q2 = " FROM xz2466.player_info pi,xz2466.players ps"
  q3 = " WHERE pi.player_nameid = ps.player_nameid"
  query =  q1 + q2 + q3
  
  p_id = request.form['id']
  if (p_id != '') & injection_protect(p_id):
      t_q1 = " AND ps.id = '?'"
      query = query + t_q1.replace('?',p_id)
  
  p_name = request.form['name']
  if (p_name != '') & injection_protect(p_name):
      t_q1 = " AND ps.name like('%%name1%%')"
      query = query + t_q1.replace('name1',p_name)
  
  p_country = request.form['country']
  if (p_country != '') & injection_protect(p_country):
      t_q1 = " AND ps.country = '?'"
      query = query + t_q1.replace('?',p_country)
  
  p_role = request.form['role']
  if (p_role != '') & injection_protect(p_role):
      t_q1 = " AND pi.role like('%%role1%%')"
      query = query + t_q1.replace('role1',p_role)

  p_status = request.form['status']
  if (p_status != '') & injection_protect(p_status):
      t_q1 = " AND pi.status = '?'"
      query = query + t_q1.replace('?',p_status)
  
  p_age_f = request.form['age_from']
  p_age_t = request.form['age_to'] 
  if (p_age_f != '') & (p_age_t != '') & injection_protect(p_age_f) & injection_protect(p_age_t):
      y1 = 2019 - int(p_age_t)
      y2 = 2019 - int(p_age_f)
      t_q1 = " AND pi.birthday >= 'y1-1-1' AND pi.birthday <= 'y2-12-31'"
      t_q1 = t_q1.replace('y1',str(y1))
      query = query + t_q1.replace('y2',str(y2))
  
  p_yp_f = request.form['years_pro_from']
  p_yp_t = request.form['years_pro_to']
  if (p_yp_f != '') & (p_yp_t != '') & injection_protect(p_yp_f) & injection_protect(p_yp_t):
      y1 = 2019 - int(p_yp_t)
      y2 = 2019 - int(p_yp_f)
      t_q1 = " AND pi.years_pro >= y1 AND pi.years_pro <= y2"
      t_q1 = t_q1.replace('y1',str(y1))
      query = query + t_q1.replace('y2',str(y2))
  
  p_e_f = request.form['earnings_from']
  p_e_t = request.form['earnings_to']
  if (p_e_f != '') & (p_e_t != '') & injection_protect(p_e_f) & injection_protect(p_e_t):
      t_q1 = " AND pi.earnings >= 'e1' AND pi.earnings <= 'e2'"
      t_q1 = t_q1.replace('e1',p_e_f)
      query = query + t_q1.replace('e2',p_e_t)
      
  p_f_f = request.form['followers_from']
  p_f_t = request.form['followers_to']
  if (p_f_f != '') & (p_f_t != '') & injection_protect(p_f_f) & injection_protect(p_f_t):
      t_q1 = " AND pi.followers >= f1 AND pi.followers <= f2"
      t_q1 = t_q1.replace('f1',p_f_f)
      query = query + t_q1.replace('f2',p_f_t)
  
  players_s = g.conn.execute(query)
  
  query1 = query
  query1 = query1.replace(q1,"SELECT wf.*")
  query1 = query1.replace(q2," FROM xz2466.player_info pi,xz2466.players ps,xz2466.work_for wf")
  query1 = query1 + " AND wf.emp_nameid = pi.player_nameid"
  
  trans = g.conn.execute(query1)
    
  return render_template("players.html", players1 = players_s, trans = trans)

def injection_protect(query):
    blocked_words = ['select','*','insert','=',',',"'",'(',')','/']
    for word in blocked_words:
        if word in query:
            return False
    return True

@app.route('/search_teams_for_player', methods=['POST'])
def search_teams_for_player():
  q1 = "SELECT ps.player_nameid,ps.id,ts.*,wf.position,wf.since,wf.end"
  q2 = " FROM xz2466.players ps, xz2466.teams ts, xz2466.work_for wf"
  q3 = " WHERE ps.player_nameid = wf.emp_nameid AND wf.team_id = ts.team_id"
  query =  q1 + q2 + q3
  
  p_id = request.form['id']
  if (p_id != '') & injection_protect1(p_id):
      t_q1 = " AND ps.id = '?'"
      query = query + t_q1.replace('?',p_id)

  teams_for_player = g.conn.execute(query)
    
  return render_template("players.html", t_f_p = teams_for_player)

def injection_protect1(query):
    blocked_words = ['select','*','insert','=',',',"'",'(',')','/']
    for word in blocked_words:
        if word in query:
            return False
    return True

@app.route('/search_tournaments_for_player', methods=['POST'])
def search_tournaments_for_player():
  q1 = "SELECT ps.player_nameid,ps.id,ts.team_name,tour.*,p_i.result"
  q2 = " FROM xz2466.players ps, xz2466.teams ts, xz2466.tournaments tour, xz2466.participate_in p_i"
  q3 = " WHERE ps.player_nameid = p_i.emp_nameid AND ts.team_id = p_i.team_id AND tour.tournament_name = p_i.tournament_name"
  query =  q1 + q2 + q3
  
  p_id = request.form['id']
  if (p_id != '') & injection_protect2(p_id):
      t_q1 = " AND ps.id = '?'"
      query = query + t_q1.replace('?',p_id)

  tournaments_for_player = g.conn.execute(query)
    
  return render_template("players.html", tour_f_p = tournaments_for_player)

def injection_protect2(query):
    blocked_words = ['select','*','insert','=',',',"'",'(',')','/']
    for word in blocked_words:
        if word in query:
            return False
    return True

@app.route('/teams_search_team', methods=['POST'])
def search_team():
  q1 = "SELECT ts.*"
  q2 = " FROM xz2466.teams ts"
  q3 = " WHERE 1=1"
  query =  q1 + q2 + q3
  
  t_name = request.form['t_name']
  if (t_name != '') & injection_protect3(t_name):
      t_q1 = " AND ts.team_name = '?'"
      query = query + t_q1.replace('?',t_name)
  else:
      t_region = request.form['region']
      if (t_region != '') & injection_protect3(t_region):
          t_q1 = " AND ts.region = '?'"
          query = query + t_q1.replace('?',t_region)
     
      t_status = request.form['status']
      if (t_status != '') & injection_protect3(t_status):
          t_q1 = " AND ts.status = '?'"
          query = query + t_q1.replace('?',t_status)
      
      t_f_f = request.form['founded_time_f']
      t_f_t = request.form['founded_time_t'] 
      if (t_f_f != '') & (t_f_t != '') & injection_protect3(t_f_f) & injection_protect3(t_f_t):
          t_q1 = " AND ts.founded_time >= 'y1' AND ts.founded_time <= 'y2'"
          t_q1 = t_q1.replace('y1',t_f_f)
          query = query + t_q1.replace('y2',t_f_t)
          
      t_e_f = request.form['earnings_f']
      t_e_t = request.form['earnings_t']
      if (t_e_f != '') & (t_e_t != '') & injection_protect3(t_e_f) & injection_protect3(t_e_t):
          t_q1 = " AND ts.earnings >= 'e1' AND ts.earnings <= 'e2'"
          t_q1 = t_q1.replace('e1',t_e_f)
          query = query + t_q1.replace('e2',t_e_t)
  
  teams = g.conn.execute(query)
    
  return render_template("teams.html", teams = teams)

def injection_protect3(query):
    blocked_words = ['select','*','insert','=',',',"'",'(',')','/']
    for word in blocked_words:
        if word in query:
            return False
    return True

@app.route('/teams_search_emps_ps', methods=['POST'])
def search_emp_ps():
  q1 = "SELECT ts.team_name, wf.*, ps.*"
  q2 = " FROM xz2466.teams ts, xz2466.work_for wf, xz2466.players ps"
  q3 = " WHERE ts.team_id = wf.team_id AND wf.emp_nameid = ps.player_nameid"
  query =  q1 + q2 + q3
  
  t_name = request.form['t_name']
  if (t_name != '') & injection_protect4(t_name):
      t_q1 = " AND ts.team_name = '?'"
      query = query + t_q1.replace('?',t_name)
  
  w_f_f = request.form['wf_f']
  w_f_t = request.form['wf_t'] 
  if (w_f_f != '') & (w_f_t != '') & injection_protect3(w_f_f) & injection_protect3(w_f_t):
      t_q1 = " AND wf.since >= 'y1' AND wf.end <= 'y2'"
      t_q1 = t_q1.replace('y1',w_f_f)
      query = query + t_q1.replace('y2',w_f_t)  
  
  emp_players = g.conn.execute(query)
    
  return render_template("teams.html", emp_ps = emp_players)

def injection_protect4(query):
    blocked_words = ['select','*','insert','=',',',"'",'(',')','/']
    for word in blocked_words:
        if word in query:
            return False
    return True

@app.route('/teams_search_emps_ws', methods=['POST'])
def search_emp_ws():
  q1 = "SELECT ts.team_name, wf.*, ws.*"
  q2 = " FROM xz2466.teams ts, xz2466.work_for wf, xz2466.workers ws"
  q3 = " WHERE ts.team_id = wf.team_id AND wf.emp_nameid = ws.worker_nameid"
  query =  q1 + q2 + q3
  
  t_name = request.form['t_name']
  if (t_name != '') & injection_protect5(t_name):
      t_q1 = " AND ts.team_name = '?'"
      query = query + t_q1.replace('?',t_name)
  
  w_f_f = request.form['wf_f']
  w_f_t = request.form['wf_t'] 
  if (w_f_f != '') & (w_f_t != '') & injection_protect5(w_f_f) & injection_protect5(w_f_t):
      t_q1 = " AND wf.since >= 'y1' AND wf.end <= 'y2'"
      t_q1 = t_q1.replace('y1',w_f_f)
      query = query + t_q1.replace('y2',w_f_t)  
  
  emp_workers = g.conn.execute(query)
    
  return render_template("teams.html", emp_ws = emp_workers)

def injection_protect5(query):
    blocked_words = ['select','*','insert','=',',',"'",'(',')','/']
    for word in blocked_words:
        if word in query:
            return False
    return True

@app.route('/teams_search_tour', methods=['POST'])
def search_tour_for_team():
  q1 = "SELECT DISTINCT ts.team_name, p_i.result, tour.*"
  q2 = " FROM xz2466.teams ts, xz2466.participate_in p_i, xz2466.tournaments tour"
  q3 = " WHERE ts.team_id = p_i.team_id AND p_i.tournament_name = tour.tournament_name"
  query =  q1 + q2 + q3
  
  t_name = request.form['t_name']
  if (t_name != '') & injection_protect6(t_name):
      t_q1 = " AND ts.team_name = '?'"
      query = query + t_q1.replace('?',t_name)
  
  tours = g.conn.execute(query)
    
  return render_template("teams.html", tours = tours)

def injection_protect6(query):
    blocked_words = ['select','*','insert','=',',',"'",'(',')','/']
    for word in blocked_words:
        if word in query:
            return False
    return True

@app.route('/teams_search_spon', methods=['POST'])
def search_spon_for_team():
  q1 = "SELECT ts.team_name, t_s_b.*"
  q2 = " FROM xz2466.teams ts, xz2466.teams_sponsored_by t_s_b"
  q3 = " WHERE ts.team_id = t_s_b.team_id"
  query =  q1 + q2 + q3
  
  t_name = request.form['t_name']
  if (t_name != '') & injection_protect7(t_name):
      t_q1 = " AND ts.team_name = '?'"
      query = query + t_q1.replace('?',t_name)
  
  spons = g.conn.execute(query)
    
  return render_template("teams.html", spons = spons)

def injection_protect7(query):
    blocked_words = ['select','*','insert','=',"'",'(',')','/']
    for word in blocked_words:
        if word in query:
            return False
    return True

@app.route('/search_tour_for_org', methods=['POST'])
def search_tour_for_org():
  q1 = "SELECT t_o_b.organizer_name, tour.*"
  q2 = " FROM xz2466.tournaments tour, xz2466.tournaments_organized_by t_o_b"
  q3 = " WHERE t_o_b.tournament_name = tour.tournament_name"
  query =  q1 + q2 + q3
  
  org_name = request.form['org_name']
  if (org_name != '') & injection_protect7(org_name):
      t_q1 = " AND t_o_b.organizer_name = '?'"
      query = query + t_q1.replace('?',org_name)
  
  t_f_o = g.conn.execute(query)
    
  return render_template("organizers.html", t_f_o = t_f_o,organizers = g.conn.execute("SELECT * FROM xz2466.organizers"))

@app.route('/spon_search_ts', methods=['POST'])
def search_ts_for_spon():
  q1 = "SELECT t_s_b.sponsor, ts.*"
  q2 = " FROM xz2466.teams_sponsored_by t_s_b, xz2466.teams ts"
  q3 = " WHERE t_s_b.team_id = ts.team_id"
  query =  q1 + q2 + q3
  
  s_name = request.form['s_name']
  if (s_name != '') & injection_protect7(s_name):
      t_q1 = " AND t_s_b.sponsor = '?'"
      query = query + t_q1.replace('?',s_name)
  
  ts_spon = g.conn.execute(query)
    
  return render_template("sponsors.html", ts_spon = ts_spon, sponsors = g.conn.execute("SELECT * FROM xz2466.sponsors"))

@app.route('/spon_search_tour', methods=['POST'])
def search_tour_for_spon():
  q1 = "SELECT tour_s_b.sponsor_name, tour.*"
  q2 = " FROM xz2466.tournaments_sponsored_by tour_s_b, xz2466.tournaments tour"
  q3 = " WHERE tour_s_b.tournament_name = tour.tournament_name"
  query =  q1 + q2 + q3
  
  s_name = request.form['s_name']
  if (s_name != '') & injection_protect7(s_name):
      t_q1 = " AND tour_s_b.sponsor_name = '?'"
      query = query + t_q1.replace('?',s_name)
  
  tour_spon = g.conn.execute(query)
    
  return render_template("sponsors.html", tour_spon = tour_spon, sponsors = g.conn.execute("SELECT * FROM xz2466.sponsors"))

@app.route('/tour_search_tour', methods=['POST'])
def search_tour():
  q1 = "SELECT tour.*"
  q2 = " FROM xz2466.tournaments tour"
  q3 = " WHERE 1=1"
  query =  q1 + q2 + q3
  
  tour_name = request.form['tour_name']
  if (tour_name != '') & injection_protect7(tour_name):
      t_q1 = " AND tour.tournament_name = '?'"
      query = query + t_q1.replace('?',tour_name)
      tour = g.conn.execute(query)
  else:
      input_time = request.form['input_time']
      if (input_time != '') & injection_protect7(input_time):
          if ',' in input_time:
              temp = ''
              for i in input_time:
                  if i != ',':
                      temp += i
                  else:
                      break
              time1 = temp
              time2 = input_time.replace(temp+',','')
          
              t_q1 = " AND tour.dates like('%%time%%')"
              query = query + t_q1.replace('time',time1) + t_q1.replace('time',time2)
          else:
              t_q1 = " AND tour.dates like('%%time%%')"
              query = query + t_q1.replace('time',input_time)
      
      input_location = request.form['input_location']
      if (input_location != '') & injection_protect7(input_location):
          if ',' in input_location:
              temp = ''
              for i in input_location:
                  if i != ',':
                      temp += i
                  else:
                      break
              loc1 = temp
              loc2 = input_location.replace(temp+',','')
          
              t_q1 = " AND tour.city like('%%loc%%')"
              query = query + t_q1.replace('loc',loc1) + t_q1.replace('loc',loc2)
          else:
              t_q1 = " AND tour.city like('%%loc%%')"
              query = query + t_q1.replace('loc',input_location)
              
      prizepool_f = request.form['prizepool_f']
      prizepool_t = request.form['prizepool_t']
      if (prizepool_f != '') & (prizepool_t != '') & injection_protect3(prizepool_f) & injection_protect3(prizepool_t):
          t_q1 = " AND tour.prizepool >= 'p1' AND tour.prizepool <= 'p2'"
          t_q1 = t_q1.replace('p1',prizepool_f)
          query = query + t_q1.replace('p2',prizepool_t)
  
  tour = g.conn.execute(query)
  return render_template("tournaments.html", tour = tour)

@app.route('/tour_search_org', methods=['POST'])
def search_org_for_tour():
  q1 = "SELECT tour_o_b.organizer_name, tour.*"
  q2 = " FROM xz2466.tournaments_organized_by tour_o_b, xz2466.tournaments tour"
  q3 = " WHERE tour_o_b.tournament_name = tour.tournament_name"
  query =  q1 + q2 + q3
  
  tour_name = request.form['tour_name']
  if (tour_name != '') & injection_protect7(tour_name):
      t_q1 = " AND tour.tournament_name = '?'"
      query = query + t_q1.replace('?',tour_name)
  
  tour_org = g.conn.execute(query)
    
  return render_template("tournaments.html", tour_org = tour_org)

@app.route('/tour_search_spon', methods=['POST'])
def search_spon_for_tour():
  q1 = "SELECT tour_s_b.sponsor_name, tour.*"
  q2 = " FROM xz2466.tournaments_sponsored_by tour_s_b, xz2466.tournaments tour"
  q3 = " WHERE tour_s_b.tournament_name = tour.tournament_name"
  query =  q1 + q2 + q3
  
  tour_name = request.form['tour_name']
  if (tour_name != '') & injection_protect7(tour_name):
      t_q1 = " AND tour.tournament_name = '?'"
      query = query + t_q1.replace('?',tour_name)
  
  tour_spon = g.conn.execute(query)
    
  return render_template("tournaments.html", tour_spon = tour_spon)


@app.route('/players')
def playersWeb():
    return render_template("players.html")

@app.route('/home')
def homeWeb():
    return render_template("mainpage.html")

@app.route('/teams')
def teamWeb():
    return render_template("teams.html")

@app.route('/tournaments')
def tourWeb():
    return render_template("tournaments.html")

@app.route('/sponsors')
def sponsors():
    sponsors = g.conn.execute("SELECT * FROM xz2466.sponsors")
    return render_template("sponsors.html", sponsors = sponsors)

@app.route('/organizers')
def organizers():
    organizers = g.conn.execute("SELECT * FROM xz2466.organizers")
    return render_template("organizers.html", organizers = organizers)


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
