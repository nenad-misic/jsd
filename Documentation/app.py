from flask import Flask, request, send_from_directory
app = Flask(__name__,  static_url_path='')

@app.route('/')
def hello_world():
    return send_from_directory('public', 'index.html')

@app.route('/public/<path:path>')
def send_js(path):
    return send_from_directory('public', path)

if __name__ == "__main__":
    app.run(debug=True, port=6325)
