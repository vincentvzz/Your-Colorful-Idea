from flask import Flask, render_template, request
import logging
import urllib.parse, urllib.request, urllib.error, json

def safe_get(url):
    try:
        return urllib.request.urlopen(url).read().decode('utf-8')
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print("The server couldn't fulfill the request.")
            print("Error code: ", e.code)
        elif hasattr(e, 'reason'):
            print("We failed to reach a server")
            print("Reason: ", e.reason)
        return None

app = Flask(__name__)

RANDOM_API = "https://x-colors.herokuapp.com/api/random"

data = {
    "color_1": "#FFFFFF",
    "color_2": "#FFFFFF",
    "color_3": "#FFFFFF",
    "color_4": "#FFFFFF",
    "color_5": "#FFFFFF",
    "random_color": ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
    "color_from": ""
}

@app.route("/")
def homepage():
    return render_template('index.html', data=data)

@app.route("/random")
def random_handler():
    random_count = request.args.get("rand_num")
    for i in range(int(random_count)):
        color_str = safe_get(RANDOM_API)
        if color_str is not None:
            color_data = json.loads(color_str)
            data["random_color"][i] = color_data["hex"]
    return render_template('index.html', data=data)




if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)

