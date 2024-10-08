from flask import Flask, request, render_template, jsonify, session
import pandas as pd
import os, json

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = "your_secret_key"

# Load and process the McDonald's dataset
mcdonalds_items = pd.read_csv("mcdonalds_dataset.csv")
mcdonalds_items = mcdonalds_items.drop_duplicates(subset="product_name")

# File extensions to look for images
image_exts = [".jpg", ".jpeg", ".png", ".webp", ".jfif"]


@app.route("/")
def index():
    item_names = mcdonalds_items["product_name"].values
    file_names = []
    session["user_order"] = []

    file_found = False
    for name in item_names:
        for ext in image_exts:
            if os.path.exists(f"static/images/{name}{ext}"):
                file_names.append(f"{name}{ext}")
                file_found = True
                break
        if not file_found:
            file_names.append("default.webp")
        file_found = False

    return render_template(
        "index.html", items=item_names, images=file_names, data=mcdonalds_items
    )


@app.route("/results", methods=["POST"])
def results():
    # Get JSON data from the POST request
    user_list = request.get_json()

    # Store the user order in the session
    session["user_order"] = user_list

    # Return a success message
    return jsonify({"message": "Order received"})


@app.route("/results_page")
def results_page():
    # Retrieve the order from the session
    user_order = session.get("user_order", [])
    order_unique = list(set(user_order))
    unique_count = []
    unique_total_kcals = []
    unique_individual_kcals = []
    unique_total_price = []
    unique_individual_price = []

    total_count = len(user_order)

    cals = 0
    proteins = 0.0
    carbs = 0.0
    fat = 0.0
    salt = 0.0
    saturates = 0.0
    sugars = 0.0
    price = 0.0

    for item in order_unique:
        unique_count.append(user_order.count(item))
        unique_total_kcals.append(
            int(
                str(
                    mcdonalds_items[mcdonalds_items["product_name"] == item][
                        "product_calories"
                    ].values[0]
                ).split(": ")[1]
            )
            * user_order.count(item)
        )
        unique_individual_kcals.append(
            int(
                str(
                    mcdonalds_items[mcdonalds_items["product_name"] == item][
                        "product_calories"
                    ].values[0]
                ).split(": ")[1]
            )
        )
        try:
            temp_total = float(
                str(
                    mcdonalds_items[mcdonalds_items["product_name"] == item][
                        "product_price"
                    ].values[0]
                ).split("£")[1]
            ) * user_order.count(item)
        except IndexError:  # this happens when the price is as so "99P"
            temp_total = (
                float(
                    str(
                        mcdonalds_items[mcdonalds_items["product_name"] == item][
                            "product_price"
                        ].values[0]
                    ).split("P")[0]
                )
                * user_order.count(item)
                / 100
            )
        unique_total_price.append(f"£{temp_total:.2f}")
        unique_individual_price.append(
            mcdonalds_items[mcdonalds_items["product_name"] == item][
                "product_price"
            ].values[0]
        )

        print(
            int(
                str(
                    mcdonalds_items[mcdonalds_items["product_name"] == item][
                        "product_calories"
                    ].values[0]
                ).split(": ")[1]
            )
            * user_order.count(item)
        )

        cals += float(
            str(
                mcdonalds_items[mcdonalds_items["product_name"] == item][
                    "product_calories"
                ].values[0]
            )
            .split(": ")[1]
            .strip()
        ) * user_order.count(item)

        proteins += float(
            mcdonalds_items[mcdonalds_items["product_name"] == item]["Protein"].values[
                0
            ]
        ) * user_order.count(item)
        carbs += float(
            mcdonalds_items[mcdonalds_items["product_name"] == item]["Carbs"].values[0]
        ) * user_order.count(item)
        fat += float(
            mcdonalds_items[mcdonalds_items["product_name"] == item]["Fat"].values[0]
        ) * user_order.count(item)
        salt += float(
            mcdonalds_items[mcdonalds_items["product_name"] == item]["Salt"].values[0]
        ) * user_order.count(item)
        saturates += float(
            mcdonalds_items[mcdonalds_items["product_name"] == item][
                "Saturates"
            ].values[0]
        ) * user_order.count(item)
        sugars += float(
            mcdonalds_items[mcdonalds_items["product_name"] == item]["Sugars"].values[0]
        ) * user_order.count(item)

        try:
            price += float(
                str(
                    mcdonalds_items[mcdonalds_items["product_name"] == item][
                        "product_price"
                    ].values[0]
                ).split("£")[1]
            ) * user_order.count(item)
        except IndexError:  # this happens when the price is as so "99P"
            price += (
                float(
                    str(
                        mcdonalds_items[mcdonalds_items["product_name"] == item][
                            "product_price"
                        ].values[0]
                    ).split("P")[0]
                )
                * user_order.count(item)
                / 100
            )

    price = f"£{price:.2f}"

    return render_template(
        "results.html",
        order=order_unique,
        count=unique_count,
        total_kcals=unique_total_kcals,
        individual_kcals=unique_individual_kcals,
        individual_prices=unique_individual_price,
        total_prices=unique_total_price,
        cals=cals,
        protein=proteins,
        carbs=carbs,
        fat=fat,
        salt=salt,
        saturates=saturates,
        sugar=sugars,
        tot_count=total_count,
        price=price,
    )


if __name__ == "__main__":
    app.run(debug=True)
