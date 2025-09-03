from flask import Flask, request, render_template, send_file

app = Flask(__name__)

# routes (end points)
@app.route("/")
def index():
    return render_template('index.html')


# python main
if __name__ == "__main__":
    app.run(debug=True)