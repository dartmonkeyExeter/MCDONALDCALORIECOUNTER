from flask import Flask, request, render_template, jsonify, session
import pandas as pd
import os, json

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = 'your_secret_key'

# Load and process the McDonald's dataset
mcdonalds_items = pd.read_csv('mcdonalds_dataset.csv')
mcdonalds_items = mcdonalds_items.drop_duplicates(subset='product_name')

# File extensions to look for images
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
        
    return render_template('index.html', items=item_names, images=file_names, data=mcdonalds_items)

@app.route('/results', methods=['POST'])
def results():
    # Get JSON data from the POST request
    user_list = request.get_json()

    # Store the user order in the session
    session['user_order'] = user_list

    # Return a success message
    return jsonify({"message": "Order received"})

@app.route('/results_page')
def results_page():
    # Retrieve the order from the session
    user_order = session.get('user_order', [])

    total_cals = 0
    for item in user_order:
        total_cals += float(
            str(
                mcdonalds_items[mcdonalds_items['product_name'] == item]['product_calories'].values[0]
                ).split(": ")[1])

    return render_template('results.html', order=user_order, data=mcdonalds_items, total_calories=total_cals)

if __name__ == "__main__":
    app.run(debug=True)
