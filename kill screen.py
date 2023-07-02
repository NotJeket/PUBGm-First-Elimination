from dash import Dash, html, dcc
from dash.dependencies import Output, Input
import requests
import time
import os,signal

external_stylesheets = ['assets/style.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Define function to read data from API
def read_data_from_api(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        json_data = response.json()
        return json_data
    else:
        raise ValueError("Failed to retrieve data from API")

# Initialize data API URL
api_url_data = "http://127.0.0.1:5000/data1"

# Reset the kill_screen_displayed flag and timer when the app starts
kill_screen_displayed = False
start_time = None
player_name = ""
team_name = ""

app.layout = html.Div(
    [
        html.Div(id="team-info-container"),
        dcc.Interval(
            id='interval-component',
            interval=2 * 1000,  # update every 2 seconds
            n_intervals=0
        )
    ],
    className="app-container"
)

def get_font_size(name):
    name_length = len(name)
    if name_length <= 5:
        return "60px"
    elif name_length <= 10:
        return "40px"
    else:
        return "30px"

def get_kill_screen():
    logo_file_path = f"assets/logo/{team_name}.png"
    if os.path.isfile(logo_file_path):
        team_logo = html.Img(src=logo_file_path, className="team-logo")
    else:
        team_logo = html.Div(f"No logo found for {team_name}")

    player_name_style = {
        "font-size": get_font_size(player_name),
        "font-weight": "bold",
        "color": "white",
        "text-shadow": "1px 1px 2px black",
    }

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            team_logo,
                            html.Div(player_name, className="player-name", style=player_name_style),
                        ],
                        className="team-info-row",
                    ),
                ],
                className="background",
                style={
                    'background-image': 'url("/assets/test.png")',
                }
            ),
        ],
        className="animated-div",
    )


@app.callback(
    Output("team-info-container", "children"),
    Input("interval-component", "n_intervals")
)
def update_team_info(n):
    global kill_screen_displayed, start_time, player_name, team_name

    json_data = read_data_from_api(api_url_data)
    total_player_list = json_data.get("allinfo", {}).get("TotalPlayerList", [])

    for player_info in total_player_list:
        if player_info.get("killNum") == 1 and not kill_screen_displayed:
            player_name = player_info.get("playerName", "")
            team_name = player_info.get("teamName", "")
            kill_screen_displayed = True
            start_time = time.time()
            return get_kill_screen()

    if kill_screen_displayed:
        elapsed_time = time.time() - start_time
        if kill_screen_displayed:
            elapsed_time = time.time() - start_time
            if elapsed_time < 10:  # Display the kill screen for 10 seconds
                return get_kill_screen()
            elif elapsed_time < 15:  # Keep the kill screen visible but prepare to close the app
                return get_kill_screen()
            elif elapsed_time >= 15:  # After 15 seconds, close the app
                os.kill(os.getpid(), signal.SIGINT)

    return html.Div(className="team-info-hidden")


if __name__ == "__main__":
    app.run_server(debug=False, port=8057, host="127.0.0.1")