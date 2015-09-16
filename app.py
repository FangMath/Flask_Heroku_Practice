from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
import numpy as np
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.plotting import figure, show, output_file, vplot
from bokeh.models import Range1d
from bokeh.embed import components
from jinja2 import Template
import webbrowser
import os
import six

app = Flask(__name__)

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        ticker = request.form['ticker']
        Clo = request.form.getlist('if_clo')
        Adj = request.form.getlist('if_adj')
        Vol = request.form.getlist('if_vol')

        r = requests.get('https://www.quandl.com/api/v1/datasets/WIKI/' + ticker + '.json')
        rjson = r.json();
        data = rjson['data'];
        column_names = rjson['column_names'];
        df = pd.DataFrame(data, columns=column_names);
        df.head()

        output_file("templates/graph.html", title="stocks.py example")
        p1 = figure(x_axis_type = "datetime")

        if Clo:
            p1.line(np.array(df['Date'], 'M64'), df['Close'], color='blue', legend=ticker+': Close')

        if Adj:
            p1.line(np.array(df['Date'], 'M64'), df['Adj. Close'], color='orange', legend=ticker+': Adj. Close')

        if Vol:
            p1.line(np.array(df['Date'], 'M64'), df['Volume'], color='green', legend=ticker+': Volume')

        p1.title = "Data from Quandle WIKI set"
        p1.grid.grid_line_alpha=0.3
        p1.xaxis.axis_label = 'Date'
        p1.yaxis.axis_label = 'Price'

        window_size = 30
        window = np.ones(window_size)/float(window_size)

        plots = {'Red': p1}
        script, div = components(plots)

        template = Template('''<!DOCTYPE html>
        <html lang="en">
            <head>
            <meta charset="utf-8">
            <title>Bokeh Scatter Plots</title>
            <style> div{float: left;} </style>
            <link rel="stylesheet" href="http://cdn.pydata.org/bokeh/release/bokeh-0.9.0.min.css" type="text/css" />
            <script type="text/javascript" src="http://cdn.pydata.org/bokeh/release/bokeh-0.9.0.min.js"></script>
            {{ script }}
            </head>
            <body>
            {% for key in div.keys() %}
            {{ div[key] }}
            {% endfor %}
            </body>
            </html>
            ''')

        html_file = 'templates/graph.html'
        with open(html_file, 'w') as textfile:
            textfile.write(template.render(script=script, div=div))
            url = 'file:{}'.format(six.moves.urllib.request.pathname2url(os.path.abspath(html_file)))

        return render_template('graph.html')


@app.route('/')
def main():
  return redirect('/index')

if __name__ == '__main__':
  app.run(port=33507, debug=True, host='0.0.0.0')
