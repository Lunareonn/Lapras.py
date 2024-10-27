from jinja2 import Template


def generate_html(name, map, length, date, teams, red_team, red_score, blu_team, blu_score):
    template = Template('''
    <!DOCTYPE html>
    <html lang="en">
    <style>
        table, th, td {
            border: 1px solid black;
        }
    </style>
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>{{ name }}</h1>
        <h2>{{ map }} - {{ length }}</h2>
        <div id="player-list">
            <table id="players" class="table">
                <thead>
                    <tr>
                        <th>TEAM</th>
                        <th>Player</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>BLU</td>
                        <td>Greg</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </body>
    ''')
    html_content = template.render(name=name,
                                   map=map,
                                   length=length)
    with open('logs.html', 'w') as file:
        file.write(html_content)
