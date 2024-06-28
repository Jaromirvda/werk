import json

from flask import render_template, request, url_for, redirect, flash, jsonify
from werkzeug.debug import console

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
        with open('./app/database/data/nvidia.json', 'w') as file:
            data = json.load(file)
        for gpu in data['gpus']:
            if gpu['id'] == id and gpu['series'] == 'created series':
                data['gpus'].remove(gpu)
                with open('nvidia.json', 'w') as file:
                    json.dump(data, file)
        return redirect(url_for('nvidia'))


    else:
        gpu = s.query(AMD).filter_by(id=id).first()
        if gpu:
            s.delete(gpu)
            s.commit()
            with open('./app/database/data/amd.json', 'r') as file:
                data = json.load(file)
            for gpu in data['gpus']:
                if gpu['id'] == id and gpu['series'] == 'created series':
                    data['gpus'].remove(gpu)
                    with open('amd.json', 'w') as file:
                        json.dump(data, file)

            flash('GPU deleted successfully')

            return redirect(url_for('amd'))
        else:
            flash('GPU not found')
            return redirect(url_for('home'))


@app.route('/nvidia', methods=['GET'])
def nvidia():
    conn = get_db_connection()
    cursor = conn.cursor()


    cursor.execute("SELECT DISTINCT series FROM nvidia")
    series_options = [row['series'] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT vram FROM nvidia")
    vram_options = [row['vram'] for row in cursor.fetchall()]


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
@app.route('/create_gpu', methods=['GET', 'POST'])
def createGPU():
    form = CreateGPUForm()
    if form.validate_on_submit():
        category = form.category.data
        if category == 'Nvidia':
            nvidia = Nvidia(name=form.name.data, release_date=form.release_date.data, vram=form.vram.data,
                            series='created series', picture=form.picture.data)
            s.add(nvidia)
            s.commit()
            # Retrieve the ID after commit
            gpu_id = nvidia.id

            # Update the JSON file
            file_path = './app/database/data/nvidia.json'
            with open(file_path, 'r') as file:
                data = json.load(file)

            new_gpu = {
                'id': gpu_id,
                'name': form.name.data,
                'release_date': form.release_date.data,
                'vram': form.vram.data,
                'series': 'created series',
                'picture': form.picture.data
            }
            data['gpus'].append(new_gpu)

            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)

            return redirect(url_for('nvidia'))
        elif category == 'AMD':
            amd = AMD(name=form.name.data, release_date=form.release_date.data, vram=form.vram.data,
                      series='created series', picture=form.picture.data)
            s.add(amd)
            s.commit()

            gpu_id = amd.id


            file_path = './app/database/data/amd.json'
            with open(file_path, 'r') as file:
                data = json.load(file)

            new_gpu = {
                'id': gpu_id,
                'name': form.name.data,
                'release_date': form.release_date.data,
                'vram': form.vram.data,
                'series': 'created series',
                'picture': form.picture.data
            }
            data['gpus'].append(new_gpu)

            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)

            return redirect(url_for('amd'))

    return render_template('create_gpu.html', form=form)


@app.route('/edit_gpu/<int:id>', methods=['GET', 'POST'])
def edit_gpu(id):
    form = CreateGPUForm()

    # Fetch the GPU record
    nvidia = s.query(Nvidia).filter_by(id=id).first()
    amd = s.query(AMD).filter_by(id=id).first()

    gpu = nvidia if nvidia.series == 'created series' else amd
    print(gpu)

    if not gpu:
        flash('GPU not found', 'error')
        return redirect(url_for('nvidia'))

    if request.method == 'GET':
        form.name.data = gpu.name
        form.release_date.data = gpu.release_date
        form.vram.data = gpu.vram
        form.picture.data = gpu.picture
        form.category.data = 'Nvidia' if nvidia else 'AMD'

    if form.validate_on_submit():
        if nvidia:
            nvidia.name = form.name.data
            nvidia.release_date = form.release_date.data
            nvidia.vram = form.vram.data
            nvidia.picture = form.picture.data
        elif amd:
            amd.name = form.name.data
            amd.release_date = form.release_date.data
            amd.vram = form.vram.data
            amd.picture = form.picture.data

        s.commit()

        # Update JSON file
        if nvidia:
            file_path = './app/database/data/nvidia.json'
        else:
            file_path = './app/database/data/amd.json'

        with open(file_path, 'r') as file:
            data = json.load(file)

        for gpu_data in data['gpus']:
            if gpu_data['id'] == id:
                gpu_data['name'] = form.name.data
                gpu_data['release_date'] = form.release_date.data
                gpu_data['vram'] = form.vram.data
                gpu_data['picture'] = form.picture.data
                break

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

        flash('GPU updated successfully', 'success')
        return redirect(url_for('nvidia' if nvidia else 'amd'))

    return render_template('edit_gpu.html', form=form, gpu=gpu)
