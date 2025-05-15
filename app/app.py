from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


# Add more routes here for additional functionalities

if __name__ == '__main__':
    app.run(debug=True)