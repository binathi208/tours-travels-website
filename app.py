from flask import Flask, render_template, request, redirect
import mysql.connector
import os
import time

app = Flask(__name__)

# MySQL connection
db = mysql.connector.connect(
    host=os.getenv("MYSQLHOST"),
    user=os.getenv("MYSQLUSER"),
    password=os.getenv("MYSQLPASSWORD"),
    database=os.getenv("MYSQLDATABASE"),
    port=int(os.getenv("MYSQLPORT", 3306))
)

cursor = db.cursor()

# ---------------- HOME PAGE ----------------
@app.route("/")
def home():
    db.reconnect()   # 👈 ADD THIS

    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM destinations WHERE type='domestic'")
    domestic = cur.fetchall()

    cur.execute("SELECT * FROM destinations WHERE type='international'")
    international = cur.fetchall()

    return render_template(
        "index.html",
        domestic=domestic,
        international=international
    )
# ---------------- CONTACT / ENQUIRY PAGE ----------------
@app.route("/contact", methods=["GET", "POST"])
def contact():
    destination = request.args.get("destination", "")

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        destination = request.form["destination"]
        message = request.form["message"]

        cursor.execute(
            "INSERT INTO enquiries (name, phone, message) VALUES (%s, %s, %s)",
            (name, phone, f"{destination} - {message}")
        )
        db.commit()

        return "<h2 style='text-align:center;'>✅ Enquiry submitted successfully!</h2>"

    return render_template("contact.html", destination=destination)


# ---------------- BOOKING PAGE ----------------
@app.route("/booking", methods=["GET", "POST"])
def booking():
    destination = request.args.get("destination", "")

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form.get("email", "")
        destination = request.form["destination"]
        travel_date = request.form["travel_date"]
        adults = request.form["adults"]
        children = request.form["children"]
        message = request.form["message"]

        cursor.execute(
            """
            INSERT INTO bookings 
            (name, phone, email, destination, travel_date, adults, children, message)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (name, phone, email, destination, travel_date, adults, children, message)
        )
        db.commit()

        return "<h2 style='text-align:center;'>✅ Booking submitted successfully!</h2>"

    return render_template("booking.html", destination=destination)


# ---------------- RUN APP ----------------

@app.route("/domestic")
def domestic():
    return render_template("domestic.html")


@app.route("/international")
def international():
    return render_template("international.html")

@app.route("/car-rentals")
def car_rentals():
    return "<h2>Car Rentals Page (Coming Soon)</h2>"


@app.route("/itinerary/<place>")
def itinerary(place):
    return render_template("itinerary.html", place=place)

@app.route("/admin")
def admin():
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM destinations")
    data = cur.fetchall()

    return render_template("admin.html", data=data)
@app.route("/add_destination", methods=["GET", "POST"])
def add_destination():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        days = request.form["days"]
        itinerary = request.form["itinerary"]
        type = request.form["type"]

        # ✅ SAFE IMAGE HANDLING
        image_file = request.files.get("image")

        if image_file and image_file.filename != "":
            filename = str(int(time.time())) + "_" + image_file.filename
            image_path = os.path.join("static/images", filename)
            image_file.save(image_path)
        else:
            filename = "default.jpg"

        cur = db.cursor()
        cur.execute(
    """
    INSERT INTO destinations
    (name, description, image, type, days, itinerary)
    VALUES (%s, %s, %s, %s, %s, %s)
    """,
    (name, description, filename, type, days, itinerary)
    )
        db.commit()

        return redirect("/admin")

    return render_template("add_destination.html")
@app.route("/delete/<int:id>")
def delete(id):
    cur = db.cursor()
    cur.execute("DELETE FROM destinations WHERE id=%s", (id,))
    db.commit()

    return redirect("/admin")
if __name__ == "__main__":
    app.run(debug=True)


    