import bcrypt
from flask import render_template, request, url_for, redirect, flash, session

from app.form.createGPU import CreateGPUForm
from app.form.searchForm import searchForm
from app.models.amd import AMD
from app.models.nvidia import Nvidia
from app.database.session import Session
from app.database.databaseConnection import get_db_connection

from app import app

s = Session()


@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = searchForm()
    if form.validate_on_submit():
        amd_results = s.query(AMD).filter(AMD.name.ilike(f'%{form.search.data}%')).all()
        nvidia_results = s.query(Nvidia).filter(Nvidia.name.ilike(f'%{form.search.data}%')).all()

        return render_template('search_results.html', amd_results=amd_results, nvidia_results=nvidia_results)

    return render_template('search.html', form=form)

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
    form = CreateGPUForm()
    if form.validate_on_submit():
        category = form.category.data
        if category == 'Nvidia':
            nvidia = Nvidia(form.name.data, form.release_date.data, form.vram.data, 'created series', form.picture.data)
            s.add(nvidia)
            s.commit()
            return redirect(url_for('nvidia'))
        elif category == 'AMD':
            amd = AMD(form.name.data, form.release_date.data, form.vram.data, 'created series', form.picture.data)
            s.add(amd)
            s.commit()
            return redirect(url_for('amd'))

    return render_template('create_gpu.html', form=form)

@app.route('/edit_gpu/<int:id>', methods=['GET', 'POST'])
def edit_gpu(id):
    form = CreateGPUForm()
    gpu = s.query(Nvidia).filter_by(id=id).first()
    if gpu.series != 'created series':
        gpu = s.query(AMD).filter_by(id=id).first()

    if request.method == 'GET':
        if gpu:
            form.name.data = gpu.name
            form.release_date.data = gpu.release_date
            form.vram.data = gpu.vram
            form.picture.data = gpu.picture
        else:
            flash('GPU not found', 'error')
            return redirect(url_for('nvidia'))

    if form.validate_on_submit():
        category = form.category.data
        if category == 'Nvidia':
            gpu.name = form.name.data
            gpu.release_date = form.release_date.data
            gpu.vram = form.vram.data
            gpu.series = 'created series'
            gpu.picture = form.picture.data
            s.commit()
            return redirect(url_for('nvidia'))
        elif category == 'AMD':
            gpu = s.query(AMD).filter_by(id=id).first()
            if amd:
                gpu.name = form.name.data
                gpu.release_date = form.release_date.data
                gpu.vram = form.vram.data
                gpu.series = 'created series'
                gpu.picture = form.picture.data
                s.commit()
                return redirect(url_for('amd'))
            else:
                flash('AMD GPU not found', 'error')
                return redirect(url_for('amd'))

    return render_template('edit_gpu.html', form=form, gpu=gpu)
