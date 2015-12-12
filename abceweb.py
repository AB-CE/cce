from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Markup
import webbrowser
from os.path import isfile
import os
import pandas as pd
import pygal as pg

DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

inputs = []
simulation = None

def newest_subdirectory(directory='.'):
    directory = os.path.abspath(directory)
    all_subdirs = [os.path.join(directory, name)
                   for name in os.listdir(directory)
                   if os.path.isdir(os.path.join(directory, name))]
    return  max(all_subdirs, key=os.path.getmtime) + '/'

@app.route('/')
def show_entries():
    return render_template('show_entries.html', entries=inputs)

@app.route('/submitted_simulation', methods=['POST'])
def submitted_simulation():
    parameters = {}
    form = request.form.to_dict()
    for element in inputs:
        name = element['name']
        if element['gui'] == 'slider':
            if element['type'] == 'float' or element['type'] == float:
                parameters[name] = float(form[name])
            elif element['type'] == 'int' or element['type'] == int:
                parameters[name] = int(form[name])
        elif element['gui'] == 'switch':
            parameters[name] = name in form

    simulation(parameters)
    return render_template('forward_to_show_simulation.html')

@app.route('/show_simulation')
def show_simulation():
    output = []
    path = newest_subdirectory('./result')
    for filename in os.listdir(path):
        if filename[-4:] == '.csv':
            df = pd.read_csv(path + filename)

            if (filename.startswith('aggregate_')
                    or filename.endswith('_aggregate.csv')
                    or filename.endswith('_mean.csv')):
                for c in df.columns:
                    if c not in ['index', 'round']:
                        graph = pg.Line()
                        graph.add(c, df[c])
                        output.append({'idname': str(hash(filename + c))[0:12],
                                       'title': filename[:-4] + ' ' + c,
                                       'graph': graph.render(is_unicode=True)
                                       })

            elif filename.startswith('panel_'):
                print df['id']
                maxid = max(df['id']) + 1
                for c in df.columns:
                    if c not in ['index', 'round', 'id']:
                        graph = pg.Line()
                        for id in range(maxid):
                            print id
                            graph.add(str(id), df[c][df['id'] == id])
                        output.append({'idname': str(hash(filename + c))[0:12],
                                       'title': filename[:-4] + ' ' + c,
                                       'graph': graph.render(is_unicode=True)
                                       })
    return render_template('show_outcome.html', entries=output)



def generate(new_inputs, new_simulation):
    global inputs
    global simulation
    simulation = new_simulation
    for element in new_inputs:
        if element['gui'] == 'slider':
            if 'step' not in element:
                if element['type'] == 'int' or  element['type'] == int:
                    element['step'] = 1
                else:
                    element['step'] = (element['max'] - element['min']) / 100
            content = """<input class="mdl-slider mdl-js-slider" type="range"
                         min="{min}" max="{max}" value="{default}" name="{name}" step="{step}">
                         """.format(**element)
        elif element['gui'] == 'switch':
            content = """<label class="mdl-switch mdl-js-switch mdl-js-ripple-effect" for="{name}">
                         <input type="checkbox" id="{name}" name="{name}" value="True" class="mdl-switch__input">
                         <span class="mdl-switch__label"></span>
                         </label>""".format(**element)
        elif element['gui'] == 'menu-fixed':
            pass
        elif (element['gui'] == 'menu'
             or element['gui'] == 'menu-editable'):
            pass
        elif element['gui'] == 'text':
            content = element['text']
        elif element['gui'] == 'field':
            pass
        else:  # field
            raise SystemExit('gui gui not recognized')
        element['content'] = content
        inputs.append(element)


def run(open=True):
    """ runs the web interface that starts the ABCE simulation. If open=True,
    (default) it opens a new window in the web browser if false you need to
    manually go to  http://127.0.0.1:5000/"""
    if open:
        if inputs:
            webbrowser.open("http://127.0.0.1:5000/", new=1, autoraise=True)
        else:
            webbrowser.open("http://127.0.0.1:5000/show_simulation", new=1, autoraise=True)
    app.run(use_reloader=False)

# slider (slider-range)
# switch
# field
# menu (editable) (options)
# menu (fixed) (options)
# text


if __name__ == '__main__':
    app.run()
