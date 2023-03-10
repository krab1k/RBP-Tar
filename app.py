from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlite3

app = Flask(__name__)


def get_data_values():
    def chromosome_key(chromosome: str) -> int:
        chrtype = chromosome[3:]
        match chrtype:
            case 'X':
                return 98
            case 'Y':
                return 89
            case _:
                return int(chrtype)


    connection = sqlite3.connect('genes.db')
    cur = connection.cursor()

    values = {}

    cur.execute('SELECT DISTINCT strand FROM genes')
    values['strand'] = [x[0] for x in cur.fetchall()]

    cur.execute('SELECT DISTINCT chromosome FROM genes')
    values['chromosome'] = [x[0] for x in cur.fetchall()]

    cur.execute('SELECT DISTINCT protein_name FROM genes')
    values['protein_name'] = [x[0] for x in cur.fetchall()]

    values['strand'].sort()
    values['protein_name'].sort()
    values['chromosome'].sort(key=chromosome_key)

    values['strand'].insert(0, '')
    values['protein_name'].insert(0, '')
    values['chromosome'].insert(0, '')

    return values


data_values = get_data_values()


@app.route('/get_results')
def get_results():
    parameters = request.args
    connection = sqlite3.connect('genes.db')
    cur = connection.cursor()

    conditions = []
    strand = parameters['strand']
    if strand:
        conditions.append(f'strand = "{strand}"')
    protein_name = parameters['protein_name']
    if protein_name:
        conditions.append(f'protein_name = "{protein_name}"')
    chromosome = parameters['chromosome']
    if chromosome:
        conditions.append(f'chromosome = "{chromosome}"')
    start_min = parameters['start_min']
    start_max = parameters['start_max']
    end_min = parameters['end_min']
    end_max = parameters['end_max']

    if start_min:
        conditions.append(f'start >= {start_min}')
    if start_max:
        conditions.append(f'start <= {start_max}')
    if end_min:
        conditions.append(f'end >= {end_min}')
    if end_max:
        conditions.append(f'end <= {end_max}')

    cond = ' AND '.join(conditions)

    where = 'WHERE' if cond else ''

    sql_statement = f'SELECT * FROM genes {where} {cond} LIMIT 10000'
    cur.execute(sql_statement)

    data = cur.fetchall()
    return jsonify({'data': [list(item) for item in data]})


@app.route('/')
def search():
    return render_template('search.html', values=data_values)


@app.route('/download_all')
def download_all():
    return send_from_directory('static', 'rbp_encode_eclip.csv.gz', as_attachment=True)


if __name__ == '__main__':
    app.run()
