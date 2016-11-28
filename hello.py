from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
 
app = Flask(__name__)

courses = [
  {
    'id': 'eecs343',
    'name': 'Operating System'
  },
  {
    'id': 'eecs395',
    'name': 'Kernel Development',
  }
]

def get_all_departments:
  departments = {}
  url = "http://www.northwestern.edu/class-descriptions/4650/index.html"
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'lxml')
   
  for li in soup.find_all('li'):
    name = li.a.get('href')
    fullname = li.a.get_text()
    if fullname != 'FSEMINAR' 
      departments[fullname] = name

  return departments

@app.route("/")
def get_all():
  return jsonify({'courses': courses})

@app.route("/subjects")
def get_all_subjects():
  

@app.route("/subject/<subject_name>")
def get_subject_courses():

if __name__ == "__main__":
  app.run()
