from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
def index():
    news = {'новость1': 'petya@example.com',
                 'новость2': 'vasya@example.com',
                 'новость3': 'katya@example.com'}
    return render_template('index.html', news=news)

if __name__ == '__main__':
    app.run()
    
