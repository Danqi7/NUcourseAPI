from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
import threading
import Queue
from multiprocessing.dummy import Pool as ThreadPool
import time

app = Flask(__name__)

root_url = "http://www.northwestern.edu/class-descriptions/4650/"

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


'''
format: list of department dict
{
  "name": "School of Communication",
  "symbol": "Soc"
}
'''
def get_all_departments():
  departments = []
  department = {}
  url = "http://www.northwestern.edu/class-descriptions/4650/index.html"
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'lxml')

  for li in soup.find_all('li'):
    #name in format MEAS/index.html
    name = li.a.get('href')
    index = 0
    for i, c in enumerate(name):
      if c == '/':
        index = i
    name = name[:index]
    fullname = li.a.get_text()
    if fullname != 'FSEMINAR':
      department = department.copy()
      department['name'] = fullname
      department['symbol'] = name
      departments.append(department)

  return departments

'''
format: list of subject dict
{
  "name": "Electrical Enginnering & Computer Science",
  "symbol": "EECS"
}
'''
def get_all_subjects():
  subjects = []
  subject = {}
  departments = get_all_departments()

  for dep in departments:
    #contruct the department url
    dep_url = root_url + dep['symbol'] + '/index.html'

    #crawl each department's url to get the subjects
    r = requests.get(dep_url)
    soup = BeautifulSoup(r.text, 'lxml')

    for li in soup.find_all('li'):
      name = li.a.get('href')
      index = 0
      for i, c in enumerate(name):
        if c == '/':
          index = i
      name = name[:index]
      fullname = li.a.get_text()
      for i,c in enumerate(fullname):
        if c == '-':
          index = i + 2
      fullname = fullname[index:]

      subject = subject.copy()
      subject['symbol'] = name
      subject['name'] = fullname
      subject['department'] = dep['symbol']
      subjects.append(subject)

  return subjects

q = Queue.Queue()

'''
input subject: 'EECS'
return all the courses for input subject
format: list of course dict
{
  "name": "Introduction to Computer Science"
  "symbol": "EECS 110"
  "subject": "EECS",
  "department": "MEAS",
  "instructor": "Sara",
  "meeting_days": "MoWeTr",
  "start_time": "11:00",
  "end_time": "11:50"
}
'''
def get_subject_courses(subject):
  input_subj = {}
  subjects = get_all_subjects()
  for subj in subjects:
    if subj['symbol'] == subject:
      input_subj = subj.copy()

  course = {}
  courses = []
  #crawl the subject link to get all the courses
  subject_url = root_url + input_subj['department'] + '/' + input_subj['symbol'] + '/index.html'
  r = requests.get(subject_url)
  soup = BeautifulSoup(r.text, 'lxml')

  pool = ThreadPool(13)
  worker_array = []
  for li in soup.find_all('li'):
      worker_array.append((li,input_subj))
    # crawl_course_url(li, input_subj, courses)
    # course = course.copy()
    # t = threading.Thread(target=crawl_course_url_worker, args=(li, input_subj, courses))
    # t.daemon = True
    # t.start()
    # result = crawl_course_url(li, input_subj)
    # if result != None:
    #   course = result
    #   courses.append(course)
    # name = li.a.get_text()
    # index1 = 0
    # index2 = 0
    # cnt = 0
    # for i, c in enumerate(name):
    #   if c == '-':
    #     cnt += 1
    #     if cnt == 2:
    #       index1 = i - 1;
    #       index2 = i + 2;
    #
    # course = dict(course)
    # course['name'] = name[index2:]
    # course['symbol'] = input_subj['symbol'] + ' ' + name[:index1]
    # course['subject'] = input_subj['symbol']
    # course['department'] = input_subj['department']
    #
    # #crawl the course url
    # course_url = root_url + input_subj['department'] + '/' + input_subj['symbol'] + '/' + name[:index1] + '/index.html'
    # result = crawl_course_url(course, course_url)
    # if result != None:
    #   course = result
    #   courses.append(course)
    # res = requests.get(course_url)
    # course_sp = BeautifulSoup(res.text, 'lxml')
    #
    # for li in course_sp.find_all('li'):
    #   cnt = 0
    #   i1 = 0
    #
    #   text = li.a.get_text()
    #   '''
    #   "Fundamentals of Computer Programming -
    #    Sara Hodges Owsley -
    #    MoWeFr 11:00AM - 11:50AM"
    #   '''
    #   for i, c in enumerate(text):
    #     if c == '-':
    #       cnt += 1
    #       if cnt == 1:
    #         i1 = i + 2
    #       if cnt == 2:
    #         course['instructor'] = text[i1:i-1]
    #         course['time'] = text[i+2:]
    #
    # #trim the text
    # instructor = course['instructor']
    # time = course['time']
    #
    # for i, c in enumerate(instructor):
    #   if not c.isspace():
    #     course['instructor'] = instructor[i:]
    #     break
    #
    # for i, c in enumerate(time):
    #   if not c.isspace():
    #     course['time'] = time[i:]
    #     break
    #
    # #construct meeting_days and convert time to 24 hours format
    # #"MoWeFr 11:00AM - 11:50AM"
    # time = course['time']
    # for i, c in enumerate(time):
    #   if c.isspace():
    #     course['meeting_days'] = time[:i]
    #     time = time[i+1:]
    #     break
    # #construct start_time and end_time
    # for i, c in enumerate(time):
    #   if c.isspace():
    #     course['start_time'] = time[:i]
    #     course['end_time'] = time[i+3:]
    #     break
    #
    # #strip AM and PM and converted to 24 hours format
    # start_time = course['start_time']
    # end_time = course['end_time']
    #
    # #only scrape courses that are nicely formatted
    # if cnt == 3:
    #   course['start_time'] = get_formatted_time(start_time)
    #   course['end_time'] = get_formatted_time(end_time)
    #
    #   courses.append(course)
  print 'done!'
  t1 = time.time()
  courses = pool.map(crawl_course_url, worker_array)
  pool.close()
  pool.join()
  t2 = time.time()
  print t2-t1
  return courses

'''
convert '3:30PM' to '15:30'
        '9:00AM' to '09:00'
'''
def get_formatted_time(time):
  index1 = 0
  for i, c in enumerate(time):
    if c == ':':
      index1 = i
    if c.isalpha():
      if c.upper() == 'P' and time[:index1] != '12':
        hour = int(str(time[:index1])) + 12
        return str(hour) + time[index1:i]

  if index1 != 2:
    return '0' + time[:index1] + time[index1:-2]

  return time[:-2]
def crawl_course_url_worker(li, input_subj, courses):
  courses.append(crawl_course_url(li, input_subj))

#crawl individual course link
def crawl_course_url((li, input_subj)):
  # print input_subj
  course = {}
  name = li.a.get_text()
  index1 = 0
  index2 = 0
  cnt = 0
  for i, c in enumerate(name):
    if c == '-':
      cnt += 1
      if cnt == 2:
        index1 = i - 1;
        index2 = i + 2;

  course['name'] = name[index2:]
  course['symbol'] = input_subj['symbol'] + ' ' + name[:index1]
  course['subject'] = input_subj['symbol']
  course['department'] = input_subj['department']

  #crawl the course url
  course_url = root_url + input_subj['department'] + '/' + input_subj['symbol'] + '/' + name[:index1] + '/index.html'
  res = requests.get(course_url)
  course_sp = BeautifulSoup(res.text, 'lxml')

  for li in course_sp.find_all('li'):
    cnt = 0
    i1 = 0

    text = li.a.get_text()
    '''
    "Fundamentals of Computer Programming -
     Sara Hodges Owsley -
     MoWeFr 11:00AM - 11:50AM"
    '''
    for i, c in enumerate(text):
      if c == '-':
        cnt += 1
        if cnt == 1:
          i1 = i + 2
        if cnt == 2:
          course['instructor'] = text[i1:i-1]
          course['time'] = text[i+2:]

  if cnt != 3:
    return

  #trim the text
  instructor = course['instructor']
  time = course['time']

  for i, c in enumerate(instructor):
    if not c.isspace():
      course['instructor'] = instructor[i:]
      break

  for i, c in enumerate(time):
    if not c.isspace():
      course['time'] = time[i:]
      break

  #construct meeting_days and convert time to 24 hours format
  #"MoWeFr 11:00AM - 11:50AM"
  time = course['time']
  for i, c in enumerate(time):
    if c.isspace():
      course['meeting_days'] = time[:i]
      time = time[i+1:]
      break
  #construct start_time and end_time
  for i, c in enumerate(time):
    if c.isspace():
      course['start_time'] = time[:i]
      course['end_time'] = time[i+3:]
      break

  #strip AM and PM and converted to 24 hours format
  start_time = course['start_time']
  end_time = course['end_time']

  #only scrape courses that are nicely formatted
  if cnt == 3:
    course['start_time'] = get_formatted_time(start_time)
    course['end_time'] = get_formatted_time(end_time)
    # courses.append(course)
    # return
    return course

@app.route("/")
def get_all():
  #departments = get_all_departments()
  #subjects = get_all_subjects()
  courses = get_subject_courses('EECS')
  return jsonify(courses)
  #return jsonify({'subjects': subjects, 'departments': departments, 'eecs': courses})
  #return jsonify({'departments': departments})


#@app.route("/subjects")
#def get_all_subjects():


#@app.route("/subject/<subject_name>")
#def get_subject_courses():

if __name__ == "__main__":
  app.run()
