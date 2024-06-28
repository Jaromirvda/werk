import json

from flask import render_template, request, url_for, redirect, flash, jsonify

from app.form.createGPU import CreateGPUForm
from app.form.searchForm import searchForm
from app.models.amd import AMD
from app.models.nvidia import Nvidia
from app.database.session import Session
from app.database.databaseConnection import get_db_connection

from app.database.json_updater import update_json_file

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


@app.route('/item/<int:id>', methods=['DELETE'])
def delete(id):
    gpu = Nvidia.query.filter_by(id=id, series='created series').first()
    if gpu:
        s.session.delete(gpu)
        s.session.commit()
        update_json_file('./app/database/data/nvidia.json', id)
        return jsonify({"message": "Nvidia GPU deleted successfully"}), 200

    gpu = AMD.query.filter_by(id=id, series='created series').first()
    if gpu:
        db.session.delete(gpu)
        db.session.commit()
        update_json_file('./app/database/data/amd.json', id)
        return jsonify({"message": "AMD GPU deleted successfully"}), 200

    return jsonify({"error": "GPU not found"}), 404



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
def createGPU():
    form = CreateGPUForm()
    if form.validate_on_submit():
        category = form.category.data
        if category == 'Nvidia':
            nvidia = Nvidia(name=form.name.data, release_date=form.release_date.data, vram=form.vram.data,
                            series='created series', picture=form.picture.data)
            s.add(nvidia)
            s.commit()

            return redirect(url_for('nvidia'))
        elif category == 'AMD':
            amd = AMD(name=form.name.data, release_date=form.release_date.data, vram=form.vram.data,
                      series='created series', picture=form.picture.data)
            s.add(amd)
            s.commit()

            return redirect(url_for('amd'))

    return render_template('create_gpu.html', form=form)


@app.route('/items', methods=['GET', 'POST'])
def items():

    nvidia = s.query(Nvidia).all()
    amd = s.query(AMD).all()
    return render_template('items.html', nvidia=nvidia, amd=amd)


@app.route('/item/<int:id>', methods=['PUT'])
def edit_gpu(id):
    form = CreateGPUForm()
    nvidia = s.query(Nvidia).filter_by(id=id).first()
    if nvidia.series == 'created series':
        gpu = nvidia
        form.name.data = gpu.name
        form.release_date.data = gpu.release_date
        form.vram.data = gpu.vram
        form.picture.data = gpu.picture
        form.category.data = 'Nvidia' if nvidia else 'AMD'

    elif amd.series == 'created series':
        gpu = amd
        form.name.data = gpu.name
        form.release_date.data = gpu.release_date
        form.vram.data = gpu.vram
        form.picture.data = gpu.picture
        form.category.data = 'Nvidia' if nvidia else 'AMD'


    else:
        flash('GPU not found')
        return redirect(url_for('home'))

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

        new_gpu = {
            'id': gpu.id,
            'name': gpu.name,
            'release_date': gpu.release_date,
            'vram': gpu.vram,
            'picture': gpu.picture
        }
        if nvidia:
            with open('./app/database/data/nvidia.json', 'w'):
                data = json.load(open('./app/database/data/nvidia.json'))
                data.append(new_gpu)
                jsonify('GPU has been updated!')
        else:
            with open('./app/database/data/amd.json', 'w'):
                data = json.load(open('./app/database/data/amd.json'))
                data.append(new_gpu)
                jsonify('GPU has been updated!')
        flash('GPU updated successfully', 'success')
        return redirect(url_for('nvidia' if nvidia else 'amd'))

    return render_template('edit_gpu.html', form=form, gpu=gpu)
