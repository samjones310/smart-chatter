"""APP init script"""
import os
import base64
import datetime
from flask import Flask, jsonify, request , render_template , Response
from flask_restful import reqparse, abort, Api, Resource
from flaskr.db import DbConnector
import uuid
import urllib.request
from time import gmtime, strftime
from bs4 import BeautifulSoup
import re
import requests
import cv2
import face_recognition
import pickle
from tweepy import OAuthHandler, API, Stream
import csv
import pandas as pd
import sys
from flaskr.functions.gettw import tw_main
from flaskr.functions.getm import tm_main
import urllib

APP = Flask(__name__)
API = Api(APP)
APP.config.from_envvar("SETTINGS")
FLASK_ENV = os.environ.get("FLASK_ENV", default=None)
APP.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

#Health check endpoint.
@APP.route('/health_check')
def health_check():
    """Health check end point"""
    return "Server is live", 200

#Start Page.
@APP.route('/')
def index():
    return render_template('index.html')

#Calendar
@APP.route('/calendar')
def calendar():
    sid=request.args.get('sid')
    mongo_connection = DbConnector.get_connection()
    title="title"
    date= datetime.datetime.now()
    star=str(datetime.datetime(date.year,date.month,date.day)).split(' ')
    start="start"
    end="end"
    url="url"
    x=mongo_connection.db.students_subject.find({'username':sid})
    li,k=[],[]
    for i in x:
        li.append(i['access_code'])
    x=mongo_connection.db.tasks.find({'access_code':{'$in':li}})
    for i in x:
        k.append({title:i['desc'],start:str(i['st_time']),end:str(i['end_time']),url:'calendar?sid='+i['taskid']})
    return render_template('calendar.html',name=star[0],li=k)

#face_login
@APP.route("/face_login_php")
def face_login_php():
    mongo_connection = DbConnector.get_connection()
    data = pickle.loads(open('C://Users//Sam Jones//Desktop//Chatbot_Project//flaskr//functions//mithula_encodings.pickle',"rb").read())
    filename=request.args.get('img_name')
    image = cv2.imread('C://xampp//htdocs//Chatbot//'+filename)
    rgb = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb,model="cnn")
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []
    for encoding in encodings:
	# attempt to match each face in the input image to our known encodings
        matches = face_recognition.compare_faces(data["encodings"],encoding,tolerance=0.4)
        name = "Unknown"
        # check to see if we have found a match
        if True in matches:
		# find the indexes of all matched faces then initialize a dictionary to count the total number of times each face
		# was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            # loop over the matched indexes and maintain a count for each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1
            name = max(counts, key=counts.get)
        names.append(name)
        print(names)
    cv2.destroyAllWindows()
    if len(names)==1:
        if names[0]=='Unknown':
            return render_template("index.html",noresp=1)
        sub,li,cale=[],[],[]
        name=names[0]
        date= datetime.datetime.now()
        start=datetime.datetime(date.year,date.month,date.day,date.hour,date.minute,0)
        end=start+datetime.timedelta(days=1)
        y=mongo_connection.db.students_subject.find({'username':name})
        for i in y:
            sub.append(i['access_code'])
        z=mongo_connection.db.tasks.find({'access_code':{'$in':sub},'status':"Not Done",'st_time':{'$gte':start}}).sort([('st_time',-1)])
        for i in z:
            li.append([i['st_time'],i['name'],i['type'],i['desc']])
        b=mongo_connection.db.tasks.find({'$or':[{'st_time':{'$gte':start,'$lt':end}},{'end_time':{'$lt':start,'$gte':end}},{'$and':[{'st_time':{'$lt':start}},{'end_time':{'$gte':end}}]}],'access_code':{'$in':sub}})
        for i in b:
            cale.append([i['st_time'],i['name'],i['type'],i['end_time'],i['desc']])
        return render_template('chat_voice.html',userid=names[0],li=li,notilen=len(li),cale=cale,callen=len(cale))
    return render_template("index.html",noresp=3)

#Login.
@APP.route('/login')
def login():
    name= request.args.get('username')
    password= request.args.get('password')
    mongo_connection = DbConnector.get_connection()
    x,li,sub,cale=[],[],[],[]
    x=mongo_connection.db.login_credentials.find_one({'name':name,'password':password})
    if x!=None:
        y=mongo_connection.db.login_details.find_one({'name':name})
        if y['face']=='Yes':
            y=mongo_connection.db.login_images.find_one({'name':name})
            img_name=y['img_name']
        else:
            img_name="logo.PNG"
        date= datetime.datetime.now()
        start=datetime.datetime(date.year,date.month,date.day,date.hour,date.minute,0)
        end=start+datetime.timedelta(days=1)
        y=mongo_connection.db.students_subject.find({'username':name})
        for i in y:
            sub.append(i['access_code'])
        z=mongo_connection.db.tasks.find({'access_code':{'$in':sub},'status':"Not Done",'st_time':{'$gte':start}}).sort([('st_time',-1)])
        for i in z:
            li.append([i['st_time'],i['name'],i['type'],i['desc']])
        b=mongo_connection.db.tasks.find({'$or':[{'st_time':{'$gte':start,'$lt':end}},{'end_time':{'$lt':start,'$gte':end}},{'$and':[{'st_time':{'$lt':start}},{'end_time':{'$gte':end}}]}],'access_code':{'$in':sub}})
        for i in b:
            cale.append([i['st_time'],i['name'],i['type'],i['end_time'],i['desc']])
        return render_template('chat_voice.html',userid=x['name'],li=li,notilen=len(li),cale=cale,callen=len(cale),img_name=img_name)
    return render_template('index.html',noresp=2)


@APP.route('/notifcation_read')
def notifcation_read():
    mongo_connection = DbConnector.get_connection()
    name=request.args.get('username')
    date=datetime.datetime.now()
    start = datetime.datetime(date.year,date.month,date.day)
    end = start+datetime.timedelta(days=1)
    cale,li,sub=[],[],[]
    y=mongo_connection.db.students_subject.find({'regno':name})
    for i in y:
        sub.append(i['subject'])
    mongo_connection.db.tasks.update_many({'name':{'$in':sub},"notified":'No','status':"Not Done",'st_time':{'$gte':start }},{"$set":{"notified":"Yes"}})
    z=mongo_connection.db.tasks.find({'name':{'$in':sub},"notified":'No','status':"Not Done",'st_time':{'$gte':start }}).sort([( 'st_time', -1)])
    for i in z:
        li.append([i['st_time'],i['name'],i['type'],i['desc']])
    b=mongo_connection.db.tasks.find({'st_time':{'$lte':end,'$gte':start},'name':{'$in':sub}})
    for i in b:
        cale.append([i['st_time'],i['name'],i['type'],i['end_time'],i['desc']])
    return render_template('chat_voice.html',userid=name,li=li,notilen=len(li),cale=cale,callen=len(cale))

#Sign Up.
@APP.route('/signup')
def signup():
    uid=str(uuid.uuid1())
    mongo_connection = DbConnector.get_connection()
    x,org=[],[]
    x=mongo_connection.db.organisation.find()
    for i in x:
        org.append(i['name'])
    return render_template('signup.html',uid=uid,organisation=org)

#Sign Up.
@APP.route('/signup_val')
def signup_val():
    uid= request.args.get('uid')
    name= request.args.get('name')
    email= request.args.get('email')
    password= request.args.get('password')
    repass= request.args.get('repass')
    dob= request.args.get('dob')
    organi= request.args.get('organisation')
    mongo_connection = DbConnector.get_connection()
    if mongo_connection.db.login_details.find({'id':uid}).count()==0 and mongo_connection.db.login_details.find({'name':name}).count()==0:
        li={'id':uid,'name':name,'organisation':organi,'email':email,'face':'No'}
        mongo_connection.db.login_details.insert(li)
        li={'id':uid,'name':name,'password':password}
        mongo_connection.db.login_credentials.insert(li)
        return render_template('index.html')
    uid=str(uuid.uuid1())
    mongo_connection = DbConnector.get_connection()
    x,org=[],[]
    x=mongo_connection.db.organisation.find()
    for i in x:
        org.append(i['name'])
    return render_template('signup.html',uid=uid,organisation=org)
    
#Sign Up with face.
@APP.route('/signup_face')
def signup_face():
    uid=str(uuid.uuid1())
    mongo_connection = DbConnector.get_connection()
    x,org=[],[]
    x=mongo_connection.db.organisation.find()
    for i in x:
        org.append(i['name'])
    return render_template('signup_face.html',uid=uid,organisation=org,f=1)

#Sign Up with face.
@APP.route('/signup_face_temp')
def signup_face_temp():
    img_name= request.args.get('img_name')
    uid= request.args.get('uid')
    name= request.args.get('name')
    email= request.args.get('email')
    password= request.args.get('password')
    repass= request.args.get('repass')
    dob= request.args.get('dob')
    organi= request.args.get('org')
    mongo_connection = DbConnector.get_connection()
    if mongo_connection.db.login_details.find({'id':uid,'name':name}).count()==0 and mongo_connection.db.login_details.find({'name':name}).count()==0:
        li={'id':uid,'name':name,'organisation':organi,'email':email,'face':'Progress'}
        mongo_connection.db.login_details.insert(li)
        li={'id':uid,'name':name,'password':password}
        mongo_connection.db.login_credentials.insert(li)
    else:
        li={'name':name,'organisation':organi,'email':email,'face':'Progress'}
        mongo_connection.db.login_details.update({ "id":uid},{"$set":li})
        li={'name':name,'password':password}
        mongo_connection.db.login_credentials.update({ "id":uid},{"$set":li})
    x,org,img=[],[],[]
    mongo_connection.db.login_images.insert({'uid':uid,'username':name,'img_name':img_name})
    x=mongo_connection.db.login_images.find({'uid':uid})
    for i in x:
        img.append(i['img_name'])
    x=mongo_connection.db.organisation.find()
    for i in x:
        org.append(i['name'])
    return render_template('signup_face.html',f=0,len=len(img),img=img,uid=uid,name=name,email=email,password=password,repassword=repass,today_date=dob,organi=organi,organisation=org)

#Sign Up with face.
@APP.route('/signup_face_val')
def signup_face_val():
    uid = request.args.get('id')
    mongo_connection = DbConnector.get_connection()
    if mongo_connection.db.login_details.find({'id':uid}).count()==1:
        return render_template('index.html')
    mongo_connection = DbConnector.get_connection()
    x,org=[],[]
    x=mongo_connection.db.organisation.find()
    for i in x:
        org.append(i['name'])
    return render_template('signup_face.html',uid=uid,organisation=org,f=1)

#Main Request from Chatbot
@APP.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    msg=userText.split('$')
    mongo_connection = DbConnector.get_connection()
    if msg[0]=='addtask':
        x=mongo_connection.db.login_designation.find_one({'username':msg[1]})
        if x['designation']=='Professor':
            return 'Hi you can add your task.$add_task?pid='+msg[1]
        return 'Not Authroized to add tasks.'
    if msg[0]=='viewtask':
        return 'Hi you can view your task.$get_task?sid='+msg[1]
    if msg[0][0]=='!':
        print(msg[0])
        return 'Hi you can view your deals.$deals?prod='+msg[0][1:]
    if msg[0][0]=='#':
        print(msg[0])
        return 'Hi you can view your deals.$gettweets?hash='+msg[0][1:]
    else:
        return msg[0]

#Dashboard for professor.
@APP.route("/professor_dashboard")
def professor_dashboard():
    pid = request.args.get('pid')
    mongo_connection = DbConnector.get_connection()
    x=mongo_connection.db.tasks.find({'pid':pid})
    li=[]
    for i in x:
        li.append([i['taskid'],i['name'],i['st_time'],i['end_time'],i['status'],i['subject_code'],i['access_code'],str(str(i['semester'])+'/'+str(i['year']))])
    return render_template("professor_dashboard.html",li=li,pid=pid,len=len(li))

#Professor Add task.
@APP.route("/add_task")
def add_task():
    mongo_connection = DbConnector.get_connection()
    pid = request.args.get('pid')
    x=mongo_connection.db.login_designation.find_one({'username':pid})
    name=x['name']
    org=[]
    x=mongo_connection.db.staff_subject.find({'username':pid})
    for i in x:
        opt=i['subject']+'('+i['subject_code']+')'+' for '+i['dept']
        org.append([i['access_code'],opt])
    return render_template("add_task.html",pid=pid,organisation=org,name=name)

#Professor Add task HTML.
@APP.route("/add_task_html",methods=["GET"])
def add_task_html():
    pid = request.args.get('pid')
    access_code = request.args.get('code')
    start_time = request.args.get('start_time')
    start_time = datetime.datetime.strptime(start_time, "%m/%d/%Y %I:%M %p")
    end_time = request.args.get('end_time')
    end_time= datetime.datetime.strptime(end_time, "%m/%d/%Y %I:%M %p")
    typ = request.args.get('type')
    desc = request.args.get('desc')
    rec_time = request.args.get('rec_time')
    rec_time=rec_time.split('-')
    rec_min=rec_time[0]
    rec_max=rec_time[1]
    mongo_connection = DbConnector.get_connection()
    taskid=str(uuid.uuid1())
    x=mongo_connection.db.staff_subject.find_one({'access_code':access_code})
    subject=x['subject']
    subject_code=x['subject_code']
    year=x['st_year']
    sem=x['semester']
    mongo_connection.db.tasks.insert({'taskid':taskid,'pid':pid,'name':subject,'subject_code':subject_code,'st_time':start_time,'end_time':end_time,'type':typ,
    'desc':desc,'status':'Not Done','access_code':access_code,'year':year,'semester':sem,'rec_min':rec_min,'rec_max':rec_max})
    mongo_connection = DbConnector.get_connection()
    x=mongo_connection.db.tasks.find({'pid':pid})
    li=[]
    for i in x:
        li.append([i['taskid'],i['name'],i['st_time'],i['end_time'],i['status'],i['subject_code'],i['access_code'],str(str(i['semester'])+'/'+str(i['year']))])
    return render_template("professor_dashboard.html",li=li,pid=pid,len=len(li))

#Professor Update task.
@APP.route("/change_status",methods=["GET"])
def change_status():
    tid = request.args.get('tid')
    mongo_connection = DbConnector.get_connection()
    x=mongo_connection.db.tasks.find_one({'taskid':tid})
    pid=x['pid']
    name=x['name']
    access_code=x['access_code']
    st_time=x['st_time']
    end_time=x['end_time']
    typ=x['type']
    status=x['status']
    desc=x['desc']
    x=mongo_connection.db.staff_subject.find({'username':pid})
    temp,org=[],[]
    for i in x:
        if i['access_code']==access_code:
            temp=i['subject']+'('+i['subject_code']+')'+' for '+i['dept']
            acc_code=i['access_code']
        else:
            opt=i['subject']+'('+i['subject_code']+')'+' for '+i['dept']
            org.append([i['access_code'],opt])
    return render_template("edit_task.html",pid=pid,tid=tid,type=typ,name=name,status=status,st_time=st_time,end_time=end_time,temp=temp,acc_code=acc_code,organisation=org)
    
#Professor Update task HTML.
@APP.route("/change_status_html",methods=["GET"])
def change_status_html():
    mongo_connection = DbConnector.get_connection()
    pid = request.args.get('pid')
    access_code = request.args.get('code')
    start_time = request.args.get('start_time')
    start_time = datetime.datetime.strptime(start_time, "%m/%d/%Y %I:%M %p")
    end_time = request.args.get('end_time')
    end_time= datetime.datetime.strptime(end_time, "%m/%d/%Y %I:%M %p")
    typ = request.args.get('type')
    desc = request.args.get('desc')
    tid = request.args.get('tid')
    status = request.args.get('status')
    x=mongo_connection.db.staff_subject.find_one({'access_code':access_code})
    subject=x['subject']
    subject_code=x['subject_code']
    year=x['st_year']
    sem=x['semester']
    mongo_connection.db.tasks.update({'taskid':tid},{"$set":{"name":subject,"subject_code":subject_code,"end_time":end_time,"st_time":start_time,"type":typ,"desc":desc,"status":status,'access_code':access_code,"year":year,"semester":sem}})
    x=mongo_connection.db.tasks.find({'pid':pid})
    li=[]
    for i in x:
        li.append([i['taskid'],i['name'],i['st_time'],i['end_time'],i['status'],i['subject_code'],i['access_code'],str(str(i['semester'])+'/'+str(i['year']))])
    return render_template("professor_dashboard.html",li=li,pid=pid,len=len(li))

#Professor Delete task HTML.
@APP.route("/delete_task",methods=["GET"])
def delete_status():
    tid=request.args.get('tid')
    pid=request.args.get('pid')
    mongo_connection = DbConnector.get_connection()
    mongo_connection.db.tasks.remove({'taskid':tid})
    x=mongo_connection.db.tasks.find({'pid':pid})
    li=[]
    for i in x:
        li.append([i['taskid'],i['name'],i['st_time'],i['end_time'],i['status'],i['subject_code'],i['access_code'],str(str(i['semester'])+'/'+str(i['year']))])
    return render_template("professor_dashboard.html",li=li,pid=pid,len=len(li))

#Students get task.
@APP.route("/get_task")
def get_task():
    sid=request.args.get('sid')
    mongo_connection = DbConnector.get_connection()
    x=mongo_connection.db.students_subject.find({'username':sid})
    li=[]
    for i in x:
        li.append(i['access_code'])
    x=mongo_connection.db.tasks.find({'access_code':{'$in':li}})
    li=[]
    for i in x:
        li.append([i['taskid'],i['name'],i['st_time'],i['end_time'],i['status']])
    return render_template("get_tasks.html",sid=sid,li=li,len=len(li)) 

#Product Deals
@APP.route("/deals")
def deals():
    prod=request.args.get('prod')
    product=re.sub(' ','+',prod)
    link = "https://www.flipkart.com/search?q="
    link=link+product
    link1=link
    page=urllib.request.urlopen(link)
    soup = BeautifulSoup(page,'html.parser')
    res=[['S.NO','Name','Price','Ratings']]
    for i in range (5):
        sno=i+1
        name=soup.find_all(class_="_3wU53n")[i].get_text()
        price=soup.find_all(class_="_1vC4OE")[i].get_text()
        price=price[:]
        rating=soup.find_all(class_="hGSR34")[i].get_text()
        res.append([sno,name,price,rating])
    print(res)
    link="https://www.amazon.in/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords="+product
    #headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64;     x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate",     "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
    r = requests.get(link, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    #a-size-mini a-spacing-none a-color-base s-line-clamp-2
    #a-offscreen
    name=soup.findAll(class_="a-size-mini a-spacing-none a-color-base s-line-clamp-2")
    price=soup.findAll(class_="a-size-base a-link-normal s-no-hover a-text-normal")
    ratings=soup.findAll(class_="a-row a-size-small")
    r_ratings=[]
    j=0
    n=5
    while len(r_ratings)!=int(n):
        te=ratings[j].get_text()
        te=re.sub('\n','',te)
        if len(te)!=0:
            r_ratings.append(te)
        j=j+1
    r_sno,r_name,r_price=[],[],[]
    result=[]
    for i in range (int(n)):
        r_sno.append(i+1)
        t_name=name[i].get_text()
        t_name=t_name.split(',')
        t_name[0]=re.sub('\n','',t_name[0])
        r_name.append(t_name[0])
        t_price=price[i].get_text()
        s_price=t_price.split(t_price[1])
        t_price=t_price[1]+s_price[1]
        r_price.append(t_price)
        result.append([r_sno[i],r_name[i],r_price[i],r_ratings[i]])
    print(result)
    link3 = "https://www.snapdeal.com/search?keyword="+product
    page=urllib.request.urlopen(link3)
    soup = BeautifulSoup(page,'html.parser')
    sno,name,price,rating=[],[],[],[]
    res3=[]
    for i in range (5):
        sno.append(i+1)
        name.append(soup.find_all(class_="product-title")[i].get_text())
        price.append(soup.find_all(class_="lfloat product-price")[i].get_text())
        rating.append(soup.find_all(class_="product-rating-count")[i].get_text())
        res3.append([name[i],price[i],rating[i]])
    return render_template("deals.html",li=res,li1=result,li2=res3,len=len(res),len1=len(result),product=prod,link1=link1,link=link,link3=link3)

@APP.route('/twitter')
def twitter():
	return render_template('newindex.html')

@APP.route('/gettweets', methods=['GET'])
def gettweets():
        result=tw_main()
        li=result.split(' ')
        print(li)
        return render_template('newindex.html',hast=1,positive=int(li[0]),negative=int(li[2]),neutral=int(li[1]),pos=float(li[3]),neu=float(li[4]),neg=float(li[5]),tagname=str(li[6]))

@APP.route('/getmedia', methods=['GET'])
def getmedia():
        tm_main()
        return render_template('newindex.html',hast=0)