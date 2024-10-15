from flask import Flask, render_template, request, redirect, url_for, jsonify
import pyaudio
import speech_recognition as sr
from imdb import IMDb
import textwrap
import asyncio
import pyttsx3
import time

app = Flask(__name__)
ia = IMDb()

def recognize_speech():
    recognizer = sr.Recognizer()
    start_time = time.time()
    
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    
    input_duration = (time.time() - start_time)  # in seconds
    print(f"Said to enter movie name in {input_duration:.2f} s")

    while True:
        try:
            movie_name = recognizer.recognize_google(audio)
            print(f"User said {movie_name}")
            return movie_name
        except sr.UnknownValueError:
            print("Not sure what you said, please try again.")
            return None
        except sr.RequestError:
            print("Please check your internet connection or try again in some time.")
            return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/search', methods=['POST'])
async def search():
    start_time = time.time()
    movie_name = await asyncio.to_thread(recognize_speech)
    
    if movie_name:
        search_start_time = time.time()
        items = ia.search_movie(movie_name)[:10]
        search_duration = time.time() - search_start_time
        print(f"Searched for movie '{movie_name}' in {search_duration:.2f} s")
        
        movies = []
        for movie in items:
            movie_id = movie.movieID
            details_start_time = time.time()
            movie_details = ia.get_movie(movie_id)
            details_duration = time.time() - details_start_time
            
            title = movie_details.get('title')
            poster_url = movie_details.get('cover url', 'No poster available')
            movies.append({'title': title, 'id': movie_id, 'poster': poster_url})

            print(f"Fetched details for '{title}' in {details_duration:.2f} s")
        
        total_duration = time.time() - start_time
        print(f"Total time for search: {total_duration:.2f} s")
        
        return render_template('index.html', movies=movies, heard_movie=movie_name)
    
    return redirect(url_for('index'))

@app.route('/speak', methods=['POST'])
def speak():
    start_time = time.time()
    data = request.get_json()
    summary = data.get('text')

    # Initialize the text-to-speech engine
    engine = pyttsx3.init()
    engine.say(summary)
    engine.runAndWait()

    speak_duration = time.time() - start_time
    print(f"Speaking duration: {speak_duration:.2f} s")
    
    return jsonify(success=True)

@app.route("/movie/<int:movie_id>")
def movie(movie_id):
    start_time = time.time()
    selected_movie = ia.get_movie(movie_id)
    poster_url = selected_movie.get("cover url", "No poster available")
    summary = selected_movie.get("plot", ["No summary available"])[0]
    formatted_summary = textwrap.fill(summary, width=70)

    movie_duration = time.time() - start_time
    print(f"Fetched movie details in {movie_duration:.2f} s")
    
    return render_template("movie.html", title=selected_movie["title"], poster=poster_url, summary=formatted_summary)

if __name__ == "__main__":
    app.run(debug=True)
