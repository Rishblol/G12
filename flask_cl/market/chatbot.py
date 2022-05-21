import time
import wolframalpha
import pyttsx3
import tkinter
import json
import random
import speech_recognition as sr
import datetime
import webbrowser
import os
import pyjokes
import time
import requests
import shutil
from clint.textui import progress
from urllib.request import urlopen
from newsapi import NewsApiClient
saved_locations = []
engine = pyttsx3.init('sapi5')# Microsoft speech application
voices = engine.getProperty('voices')
from market import routes

engine.setProperty('voice', voices[0].id)
gender = "Sir"
assname = "Jarvis"# will change UI name
engine.setProperty("rate", 175)
uname = "Advay"
def speak(audio):
    engine.say(audio)
    engine.runAndWait()
def Greet():
    hour = int(datetime.datetime.now().hour)
    if hour<=12 and hour>=0:
        k = "Good Morning " + gender 
        print(k)
        print("How Can I be of Service")
    elif hour>12 and hour<=5:
        k = "Good Afternoon " + gender 
        print(k)
        print("How Can I be of Service")
    else:
        k = "Good Evening " + gender 
        print(k)
        print("How Can I be of Service")
        
'''def username():
    print("Are you male or female")
    print("How should I address you?") #Will take from SQL database
    uname = takeCommand()
    uname.strip()
    intro = "Welcome "+uname
    #speak(intro)
    columns = shutil.get_terminal_size().columns
    print("Welcome ", uname.center(columns))'''

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Go ahead...")
        audio = r.listen(source, timeout=10)
    try:
        print("Loading..")
        query = r.recognize_google(audio, language ='en-in')
        print(f"{query}\n")
    except Exception as e:
        print(e)
        print("Sorry I couldn't get that")
        return None
    return query
if __name__ == '__main__':
    clear = lambda: os.system('cls')# WIll clear previous exceutions
    clear()
    Greet()
    if (uname)==0:
        pass
while True:
        query =input("Enter your question? ")
        if type(query) == str:
            query = query.lower()
            query = query.split()
        else:
            pass
        if "how" in query and "are" in query and "you" in query:
            print("I am doing well")
            print("How are you " + gender)
        elif "name" in query:
            if len(query)>5:
                pass
            elif "change" in query:
                if "my" in query:
                    print("Enter your name")
                    uname = takeCommand()
                else:
                    print("What would you like to call me")
                    assname = takeCommand()
            else:
                print("I am Just A Rather Very Intelligent System. But you can call me Jarvis")
        if 'youtube' in query:
            print("Here you go")
            webbrowser.open("youtube.com")
        elif 'mail' in query or 'email' in query or 'message' in query:
            try:
                print("What should I send?")
                content = takeCommand()
                print("Whom should I send it to?")
                to = input()

            except Exception as e:
                #print(e)
                print("Sorry, I'm unable to find this mail.")
        elif 'exit' in query or 'thank' in query or 'goodbye' in query or 'bye' in query:
            print("At your service " + gender)
            break
        elif 'joke' in query or 'funny' in query or 'laugh' in query:
            print(pyjokes.get_joke())
        elif "plus" in query or "times" in query or "minus" in query or "divided" in query or (("multiplied" in query or "divided" in query) and "by" in query) or 'calculate' in query:

            dellist = []
            for i in (query):
                if i =="jarvis":
                    query[i]==""
            
                    
            query = (" ").join(query)
            app_id = "LRJH5W-Q5KKEAQU73"
            client = wolframalpha.Client(app_id)
            #indx = query.lower().split().index('calculate')
            #query = query.split()[indx + 1:]
            res = client.query(query)
            answer = next(res.results).text
            print("The answer is " + answer)
            #speak("The answer is " + answer)
        elif "play" in query or "music" in query or "song" in query:
            for i in (query):
                if i=="play" or i=="music" or i=="song":
                    query.remove(i)
            query = ("+").join(query)
            query = str(query)
            search = "https://www.youtube.com/results?search_query=" + query
            print(search)
            webbrowser.open_new_tab(search)
        elif ("change" in query or "alter" in query) and ("voice" in query):#Will need to update in SQL database

            speak("Please choose a Voice from the following test audios")
            for voice in voices:
                engine.setProperty('voice', voice.id)
        
                engine.say('The quick brown fox jumped over the lazy dog.')
                engine.runAndWait()
            a = int(input("Choose 0 for the Male Voice and 1 for the Female Voice"))
            if a==0:
                engine.setProperty('voice', voices[0].id)
                speak('This is my new voice')
            else:
                engine.setProperty('voice', voices[1].id)
                speak("This is my new voice")
        elif 'news' in query or 'headlines' in query or 'headline' in query or 'new' in query:
            newsapi = NewsApiClient(api_key="93ffaac95aca44aea18546d9e6d5d448")
            subject =""
            
            #print("Please choose a topic or say news for a general overview")
            while True:
                subject = input("Enter a topic or just type 'news' for a general overview: ")
                if type(subject) == str:
                    subject.lower()
                    split_sub = subject.split()
                    subject = "".join(split_sub)
                    break
                else:
                    pass

            article_count = 0

            if subject =="news":
                while article_count<=5:
                    publisher=""
                    
                    reports = newsapi.get_top_headlines(q = "india", language = 'en', page_size=20)
                    articles = reports['articles']
                    for i in range(0, len(articles)):#5 articles at a time will be enough
                        for key, value in articles[i].items():
                            if key=="source":
                                publisher = articles[i][key]["name"]
                        
                        brief = articles[i]["content"]
                        link = articles[i]["url"]
                        if brief!=None:
                            

                            brief = brief.split("[")

                            brief= brief[0]
                            headline = "from "+publisher+" ,"+brief
                            print(brief)
                            print()
                            print(link)
                            #speak(headline)#
                            time.sleep(1)
                            print()
                            #print("Here's the link to find out more")
                            print()
                            article_count+=1
                            time.sleep(2)

                        else:                    
                            brief = articles[i]['title']
                            brief = str(brief)
                            headline = "from " + publisher + " ,"+brief
                            print(headline)
                            print()

                            article_count+=1
                            time.sleep(2)
                        if article_count==5:
                            print("Would you like to hear more?")
                            confirm = input("Type 1 for yes and type 0 for no")
                            if confirm==1:
                                article_count=0
                            else:
                                break                                        
            else:
                print("Here's the news about " + subject)
                print()
                link = "https://www.google.com/search?q=" + subject + "+news"
                webbrowser.open(link)

                    
                
                
                        
        elif "thank" in query or "thanks" in query:
            a = "At your service "+ gender#Just so he pronounces it clearly
            print(a)
            #speak(a)
        elif "time" in query or "date" in query or "when" in query:
            #print("K1")
            if "time" in query:
                if len(query)>=5:
                    query = ("+").join(query)
                    query = "https://www.google.com/search?q="+query
                    webbrowser.open(query)
                else:
                    tim = datetime.datetime.now()
                    current_time = tim.strftime("%H:%M:%S")
                    tim = "It is " + current_time
                    #speak(tim)
            elif "date" in query:
                if len(query)>=5:
                    query = ("+").join(query)
                    query = "https://www.google.com/search?q="+query
                    webbrowser.open(query)
                else:

                    date = datetime.datetime.now()
                    timestampStr = date.strftime("%d-%b-%Y (%H:%M:%S.%f)")
                    tim = "It is " + timestampStr
                    print(tim)
                    #speak(tim)
            
            else:
                query = ("+").join(query)
                query = "https://www.google.com/search?q="+query
                webbrowser.open(query)
        elif "where" in query or "location" in query or "which" in query or "city" in query or "country" in query or "state" in query: #FUTURE note want to add locations
            city = ""
            state = ""
            country=""
            if "am" in query or "are" in query:
                #speak("Analyzing")
                try:
                    IP = requests.get("https://api.ipify.org").text#Tracks IP address
                    print(IP)
                    url = "https://get.geojs.io/v1/ip/geo/" + IP+".json"
                    geo_requests = requests.get(url)
                    geo_data = geo_requests.json()
                    #print(geo_data)
                    city = geo_data['city']
                    state = geo_data['region']
                    country = geo_data['country']
                except Exception as e:
                    pass #speak("Sorry I'm not able to find our location")
                query_list = ["city", "state", "country", "i", "my"]
                #print(query)
                for i in query:

                    if i=="city":
                        
                        location = "We are in "+ city
                        #speak(location)
                        print(location)
                        break
                    elif i=="state" or i=="region":
                        location = "We are in "+ state
                        #speak(location)
                        print(location)
                        break
                    elif i=="country":
                        location = "We are in "+ country
                        #speak(location)
                        print(location)
                        break
                    elif i =="i" or i=="we":
                        location = "where+am+I"
                        url = 'https://google.nl/maps/place/' + location + '/&amp;'
                        webbrowser.get().open(url)
                        break
            #elif "save" in query or "favorite" in query:
                #print("You can save a location if you like")
                #speak("You can save a location if you like")

            else:
                print(query)
                query = "+".join(query)
                url = "https://www.google.com/search?q="+query
                webbrowser.get().open(url)

        elif query ==None:
            pass
            #print("nope")
        else:
            query = " ".join(query)
            try:
                print("Processing")
                app_id = "LRJH5W-Q5KKEAQU73"
                client = wolframalpha.Client(app_id)
                res = client.query(query)
                answer = next(res.results).text
                print(answer)
                speak(answer)
            except:
                
                url = "https://www.google.com/search?q="+query
                webbrowser.get().open(url)
