from flask import render_template, request, url_for, redirect, flash, jsonify

from app.form.createGPU import CreateGPUForm
from app.form.searchForm import searchForm
from app.models.amd import AMD
from app.models.nvidia import Nvidia
from app.database.session import Session
from app.database.databaseConnection import get_db_connection

from app import app

s = Session()

# global variables
amd = s.query(AMD).filter_by(id=id).first()
nvidia = s.query(Nvidia).filter_by(id=id).first()

form1 = CreateGPUForm()
form2 = searchForm()


@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if form2.validate_on_submit():
        amd_results = s.query(AMD).filter(AMD.name.ilike(f'%{form2.search.data}%')).all()
        nvidia_results = s.query(Nvidia).filter(Nvidia.name.ilike(f'%{form2.search.data}%')).all()

        return render_template('search_results.html', amd_results=amd_results, nvidia_results=nvidia_results)

    return render_template('search.html', form=form2)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    return render_template('edit.html')


@app.route('/delete_gpu/<int:id>', methods=['GET', 'POST'])
def delete(id):
    gpu = s.query(Nvidia).filter_by(id=id).first()
    if gpu.series == 'created series':
        s.delete(gpu)
        s.commit()
        return redirect(url_for('nvidia'))
    else:
        gpu = s.query(AMD).filter_by(id=id).first()
        if gpu:
            s.delete(gpu)
            s.commit()
            return redirect(url_for('amd'))
        else:
            flash('GPU not found')
            return redirect(url_for('home'))


@app.route('/nvidia', methods=['GET'])
def nvidia():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch series and vram options
    cursor.execute("SELECT DISTINCT series FROM nvidia")
    series_options = [row['series'] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT vram FROM nvidia")
    vram_options = [row['vram'] for row in cursor.fetchall()]

    # Fetch filtered data
    series = request.args.get('series')
    vram = request.args.get('vram')

    query = "SELECT * FROM nvidia WHERE 1=1"
    params = []

    if series:
        query += " AND series = ?"
        params.append(series)

    if vram:
        query += " AND vram = ?"
        params.append(vram)

    cursor.execute(query, params)
    gpus = cursor.fetchall()

    conn.close()

    return render_template('nvidia.html', gpus=gpus, series_options=series_options, vram_options=vram_options)


@app.route('/amd', methods=['GET'])
def amd():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT series FROM amd")
    series_options = [row['series'] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT vram FROM amd")
    vram_options = [row['vram'] for row in cursor.fetchall()]

    series = request.args.get('series')
    vram = request.args.get('vram')

    query = "SELECT * FROM amd WHERE 1=1"
    params = []

    if series:
        query += " AND series = ?"
        params.append(series)

    if vram:
        query += " AND vram = ?"
        params.append(vram)

    cursor.execute(query, params)
    gpus = cursor.fetchall()

    conn.close()

    return render_template('amd.html', gpus=gpus, series_options=series_options, vram_options=vram_options)


@app.route('/create_gpu', methods=['GET', 'POST'])
def createGPU():
    if form1.validate_on_submit():
        category = form1.category.data
        if category == 'Nvidia':
            nvidia = Nvidia(form1.name.data, form1.release_date.data, form1.vram.data, 'created series', form1.picture.data)
            s.add(nvidia)
            s.commit()
            return redirect(url_for('nvidia'))
        elif category == 'AMD':
            amd = AMD(form1.name.data, form1.release_date.data, form1.vram.data, 'created series', form1.picture.data)
            s.add(amd)
            s.commit()
            return redirect(url_for('amd'))

    return render_template('create_gpu.html', form=form1)


@app.route('/edit_gpu/<int:id>', methods=['GET', 'PUT'])
def edit_gpu(id):
    nvidia(id)
    if nvidia.series != 'created series':
        amd(id)
        if amd:
            amd.name = form1.name.data
            amd.release_date = form1.release_date.data
            amd.vram = form1.vram.data
            amd.series = 'created series'
            amd.picture = form1.picture.data
    else:
        nvidia.name = form1.name.data
        nvidia.release_date = form1.release_date.data
        nvidia.vram = form1.vram.data
        nvidia.series = 'created series'
        nvidia.picture = form1.picture.data

    if nvidia and amd is None:
        return jsonify({'error': 'GPU not found'}), 404

    if form1.validate_on_submit():
        category = form1.category.data
        if category == 'Nvidia':
            nvidia.name = form1.name.data
            nvidia.release_date = form1.release_date.data
            nvidia.vram = form1.vram.data
            nvidia.series = 'created series'
            nvidia.picture = form1.picture.data
        elif category == 'AMD':
            amd(id)
            amd.name = form1.name.data
            amd.release_date = form1.release_date.data
            amd.vram = form1.vram.data
            amd.series = 'created series'
            amd.picture = form1.picture.data
        else:
            return jsonify({'error': 'AMD GPU not found'}), 404

        s.commit()
        return jsonify({'success': 'GPU updated successfully'})

    return jsonify({'error': 'Invalid data'}), 400

