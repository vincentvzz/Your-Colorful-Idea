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

TRANSFER_API_BASE = "https://x-colors.herokuapp.com/api/"

data = {
    "random_color": [],
    "color_data_input": "",
    "color_data_output": ""
}

@app.route("/")
def homepage():
    return render_template('index.html', data=data)

@app.route("/random")
def random_handler():
    data["random_color"] = []
    random_count = request.args.get("rand_num")
    color_str = safe_get(RANDOM_API + "?number=" + str(random_count))
    if color_str is not None:
        color_data = json.loads(color_str)
        data["random_color"] = [color["hex"] for color in color_data]
    return render_template('index.html', data=data)

@app.route("/transfer")
def transfer_handler():
    input_type = request.args.get("input_type")
    output_type = request.args.get("output_type")
    data["color_data_input"] = request.args.get("input_data")

    if input_type == output_type:
        data["color_data_output"] = data["color_data_input"]
    else:
        request_url = TRANSFER_API_BASE + input_type + "2" + output_type + "?value=" + data["color_data_input"]
        output_str = safe_get(request_url)
        output_data = json.loads(output_str)
        if "error" in output_data.keys():
            data["color_data_output"] = "Please enter the correct format of color."
        else:
            data["color_data_output"] = output_data[output_type]
    return render_template('index.html', data=data)

def

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)

