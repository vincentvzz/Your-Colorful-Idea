from flask import Flask, render_template, request
import logging
import urllib.parse, urllib.request, urllib.error, json

app = Flask(__name__)

RANDOM_API = "https://x-colors.herokuapp.com/api/random"

TRANSFER_API_BASE = "https://x-colors.herokuapp.com/api/"

data = {
    "random_color": [],
    "color_data_input": "",
    "color_data_output": "",
    "theme_color_series": [],
    "error": "",
    "server_error": ""
}

@app.route("/")
def homepage():
    data["error"] = ""
    data["server_error"] = ""
    return render_template('index.html', data=data)

@app.route("/random")
def random_handler():
    data["error"] = ""
    data["server_error"] = ""
    data["random_color"] = []
    random_count = request.args.get("rand_num")
    color_str = safe_get(RANDOM_API + "?number=" + str(random_count))
    if color_str is not None:
        color_data = json.loads(color_str)
        data["random_color"] = [color["hex"] for color in color_data]
    return render_template('index.html', data=data)

@app.route("/transfer")
def transfer_handler():
    data["error"] = ""
    data["server_error"] = ""
    input_type = request.args.get("input_type")
    output_type = request.args.get("output_type")
    data["color_data_input"] = request.args.get("input_data")

    if input_type == output_type:
        data["color_data_output"] = data["color_data_input"]
    else:
        request_url = TRANSFER_API_BASE + input_type + "2" + output_type + "?value=" + data["color_data_input"]
        output_str = safe_get(request_url)
        if output_str is None:
            data["error"] = "Invalid Input on color for transferring."


        else:
            output_data = json.loads(output_str)
            data["color_data_output"] = output_data[output_type]
    return render_template('index.html', data=data)

@app.route("/series")
def series_handler():
    data["error"] = ""
    data["server_error"] = ""
    input_red = request.args.get("input_red")
    input_green = request.args.get("input_green")
    input_blue = request.args.get("input_blue")

    if input_red == '' or input_green == '' or input_blue == '':
        data["error"] = "Don't enter empty value while getting a series of color!"
        return render_template('index.html', data=data)

    try:
        input_red = int(input_red)
        input_green = int(input_green)
        input_blue = int(input_blue)

        second_color_str = safe_get(RANDOM_API)
        if second_color_str is not None:
            second_color_data = json.loads(second_color_str)["rgb"][4:-1]
            color1 = [input_red, input_green, input_blue]
            color2 = second_color_data.split(", ")
            color2 = [int(num) for num in color2]
            data["theme_color_series"] = gen_theme_colors(color1, color2)
        return render_template('index.html', data=data)
    except ValueError:
        data["error"] = "Invalid Input"
        return render_template('index.html', data=data)


def safe_get(url):
    try:
        return urllib.request.urlopen(url).read().decode('utf-8')
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            data["server_error"] = "The server couldn't fulfill the request. Error code: " + str(e.code)
        elif hasattr(e, 'reason'):
            data["server_error"] = "We failed to reach a server. Reason: " + str(e.reason)
        return None

# two points; find a linear function that goes through them with in (255, 255, 255).
# find a series of points on that line, save them in data["theme_color_series"]
# color contains: [red, green, blue]
def gen_theme_colors(color1, color2, number=5):
    # find longest rgb difference between two colors
    diff = [abs(color1[i] - color2[i]) for i in range(3)]
    reference_color = diff.index(max(diff))
    split_unit = 255 / number
    first_ratio = color1[reference_color] / split_unit
    second_ratio = color2[reference_color] / split_unit
    # save each color points' ratio
    ratios = [first_ratio, second_ratio]
    smaller_ratio = min(ratios)
    bigger_ratio = max(ratios)
    # calculate how many points needed between these two colors
    points_between_num = min(round(abs(first_ratio - second_ratio) - 0.5), 3)
    interval = abs(first_ratio - second_ratio) / (points_between_num + 1)

    for i in range(points_between_num):
        ratios.append(smaller_ratio + interval * (i + 1))

    # while we need additional points smaller than the current-smallest ratio
    # or bigger than the current-largest ratio
    while len(ratios) < number:
        if smaller_ratio - interval >= 0:
            smaller_ratio -= interval
            ratios.append(smaller_ratio)
            if len(ratios) >= number:
                break
        if bigger_ratio + interval <= number:
            bigger_ratio += interval
            ratios.append(bigger_ratio)

    # convert ratio back into rgb values
    colors = []
    step_vector = [(diff[i] / abs(first_ratio - second_ratio)) for i in range(len(diff))]
    for each_ratio in ratios:
        ratio_diff = each_ratio - first_ratio
        print(ratio_diff)
        current_step = [round(ratio_diff * step_vector[i]) for i in range(len(step_vector))]
        cur_color = []
        for i in range(3):
            rgb_sum = color1[i] + current_step[i]
            rgb_sum = rgb_sum if rgb_sum >= 0 else 0
            rgb_sum = rgb_sum if rgb_sum <= 255 else 255
            cur_color.append(str(rgb_sum))
        colors.append("rgb(" + ', '.join(cur_color) + ")")
    return colors

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)