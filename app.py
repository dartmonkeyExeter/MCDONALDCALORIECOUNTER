from flask import Flask, request, render_template, redirect, url_for, jsonify
import pandas as pd
import os

app = Flask(__name__)

mcdonalds_items = pd.read_csv('mcdonalds_dataset.csv')
# drop duplicate rows
mcdonalds_items = mcdonalds_items.drop_duplicates(subset='product_name')

image_exts = ['.jpg', '.jpeg', '.png', '.webp', '.jfif']

@app.route('/')
def index():
    item_names = mcdonalds_items['product_name'].values
    file_names = []

    file_found = False

    for name in item_names:
        for ext in image_exts:
            if os.path.exists(f'static/images/{name}{ext}'):
                file_names.append(f'{name}{ext}')
                file_found = True
                break
        if not file_found:
            file_names.append('default.webp')
        file_found = False
        
    return render_template('index.html', items=item_names, images=file_names)

@app.route('/results', methods=['POST', 'GET'])
def result():
    return render_template('results.html', data=mcdonalds_items)


if __name__ == "__main__":
    app.run(debug=True)