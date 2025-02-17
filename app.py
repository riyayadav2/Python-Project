from flask import Flask, render_template, request, redirect, url_for,flash,jsonify
import psycopg2,secrets,requests,pandas as pd,csv,os
import bcrypt

app = Flask(__name__)
app.secret_key = "cde2274a198dd28a15c5cf4120b5c345b10df592729900747ea4d286d8627dec"
firstname ="Hello"

# Route to render the HTML registration page
@app.route('/')
def home():
    return render_template('login.html')

# Route to handle the form submission
@app.route('/save', methods=['POST'])
def register():
    # Get form data
    username = request.form.get('user_name')
    firstname = request.form.get('first_name')
    lastname = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')

    # Print or process the form data
    print(f"Username: {username}, Email: {email}, Password: {password}, Firstname: {firstname},Lastname: {lastname}")

    conn=psycopg2.connect(database="project",user="postgres",
        password="Hello@123",host="localhost",port="5432")
    cur=conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS person(
        id SERIAL PRIMARY KEY,
        firstname TEXT NOT NULL,
        lastname TEXT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        email TEXT NOT NULL
    );
    """)
    cur.execute("SELECT * FROM person WHERE username = %s", (username,))
    existing_user = cur.fetchone()
    print(f'existing_user: {existing_user}')
    if existing_user is not None:
            flash("Username already exists!")
            return redirect(url_for('registration'))
    else:
        cur.execute("INSERT INTO person (firstname, lastname, username, password, email) VALUES (%s, %s, %s, %s, %s)",
                (firstname, lastname, username, password, email)) 
    conn.commit()
    cur=conn.cursor()
    flash("Registration successful! You can now log in.", "success")
    return redirect(url_for('registration'))
    conn.commit()
    cur.close()
    conn.close()

db_config = {
    "dbname": "project",         # Replace with your database name
    "user": "postgres",          # Replace with your PostgreSQL username
    "password": "Hello@123",  # Replace with your PostgreSQL password
    "host": "localhost",
    "port": "5432"                 # Default PostgreSQL port
}

@app.route('/index')
def index():
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    return render_template('welcome.html',firstname=firstname)

@app.route('/registration')
def registration():
    return render_template('registration.html')

# Route to handle login using POST method
@app.route('/login', methods=['POST'])
def login():
    # Retrieve data from the form
    username = request.form.get('username') #request.args.get('username')
    password = request.form.get('password') #request.args.get('password')
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        # Query to check if the user exists
        query = f"SELECT id, firstname, lastname, username, password, email FROM person WHERE username='{username}'"
        cursor.execute(query)
        user = cursor.fetchone()
        print(query)
        # Close database connection
        cursor.close()
        conn.close()

        if user:
            if user[4] == password:
                global firstname
                firstname = user[1]
                #return render_template('/retrieve',firstname=firstname)
                return redirect(url_for("retrieve"))
               # return render_template('newuser.html',firstname=firstname)
            else:
                return f"<h1>Invalid Password</h1>"
        else:
            return "<h1>Invalid username!</h1>"

    except Exception as e:
        return f"<h1>Database Error: {e}</h1>"
    
@app.route('/newuser')
def newuser():
    print("/newuser")
    return render_template('newuser.html',firstname=firstname,user=0)

@app.route('/user/<int:user_id>', methods=['POST'])
def user(user_id):
    print("/user/<int:user_id>")
    # Get form data
    firstname = request.form.get('first_name')
    lastname = request.form.get('last_name')
    location = request.form.get('location')
    phone = request.form.get('phone')
    print(f'user id is: {user_id}')
    user_id = int(user_id)
    print(f'firstname: {firstname}')
    print(f'lastname: {lastname}')
    print(f'location: {location}')
    print(f'phone: {phone}')

    print(f'before user id is: {user_id}')
    #user_id = request.args.get('user_id')
    #print(f'after user id is: {user_id}')
    #exit()
    conn=psycopg2.connect(database="project",user="postgres",
        password="Hello@123",host="localhost",port="5432")
    cur=conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS student(
        id SERIAL PRIMARY KEY,
        firstname TEXT NOT NULL,
        lastname TEXT,
        location TEXT NOT NULL,
        phone TEXT NOT NULL
    );
    """)
    if user_id != 0:
        print(f"record updated: {user_id}")
        querystr=f"UPDATE student SET firstname ='{firstname}', lastname ='{lastname}', location ='{location}',phone='{phone}' WHERE id ='{user_id}'"
        print(f"print query in update: {querystr}")
        #cur.execute("UPDATE student SET firstname = %s, lastname = %s, location = %s,phone= %s WHERE id = %s",(firstname, lastname, location,phone,user_id ))
        cur.execute(querystr)
        print("record after update query")
    else:
        print(f"record inserted: {user_id}")
        cur.execute("INSERT INTO student (firstname, lastname, location,phone ) VALUES (%s, %s, %s, %s)",(firstname, lastname, location,phone )) 
    conn.commit()
    print("record after update commit")
    cur.close()
    conn.close()
    # Save data to a database or return a success message
    # For now, we return a simple success response
    return redirect(url_for("retrieve"))

@app.route('/retrieve')
def retrieve():
    print("/retrieve")
    # Connect to the database
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    # Query to check if the user exists
    query = f"SELECT id, firstname, lastname, location, phone FROM student;"
    cursor.execute(query)
    user = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("welcome.html", student=user)

@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    # Delete the specified user by ID
    print("/delete_user/<int:user_id>")
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student WHERE id = %s", (user_id,))
    print(f"After deletion of {user_id}")
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("retrieve"))

@app.route("/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    print("Method /edit/<int:user_id>")
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT id,firstname, lastname, location, phone FROM student WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    print("Fetched student:", user) 
    cursor.close()
    conn.close()
    return render_template("newuser.html", user=user)


@app.route("/update/<int:user_id>", methods=["GET", "POST"])
def update_user(user_id):
    if request.method == "POST":
        # Update the user's data in the database
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        location = request.form["location"]
        phone = request.form["phone"]
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("UPDATE student SET firstname = %s, lastname = %s, location = %s,phone= %s WHERE id = %s",(user_id))(firstname, lastname, location,phone)
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("retrieve"))
    
@app.route('/loadproducts')
def loadproducts():
    url="https://fakestoreapi.com/products"
    response=requests.get(url)
    #print(f'response: {response}')
    if response.status_code:
        products = response.json()
        print(products)  # Convert response to JSON format
        posts = []  # Initialize an array

        # Store only the first 5 posts
        for post in products[:20]:
            posts.append({"id": post["id"], "title": post["title"], "price": post["price"],"description": post["description"],"category": post["category"]})

        return render_template("products.html", posts=posts)  # Pass data to HTML
    else:
        return "Failed to fetch API data"
    
@app.route("/newproducts")
def newproducts():
    df = pd.read_excel("C:/Users/riyay/OneDrive/Desktop/Python Project/templates/newproducts.xlsx", engine="openpyxl")  # Load Excel file
    print(df)
    return render_template("newproducts.html", tables=[df.to_html(classes='data', index=False)])

@app.route("/csvproducts")
def csvproducts():
    df = pd.read_csv("C:/Users/riyay/OneDrive/Desktop/Python Project/templates/csvproducts.csv")  # Replace with your file path
    table_html = df.to_html(classes="table table-bordered", index=False)  # Convert to HTML table
    return render_template("csvproducts.html", table=table_html)

@app.route("/newcsv")
def newcsv():
    return render_template("addcsv.html")

@app.route("/addcsv", methods=["POST"])
def addcsv():
    # Get form data
    product_name = request.form.get('product_name')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    data=[product_name,price,quantity]
    print(data)
    with open('templates/csvproducts.csv',mode='a',newline="") as file:
        writer=csv.writer(file)
       #writer.writerow([product_name,price,quantity])
        writer.writerow(data)
        print("data saved")
    flash("Your data has been saved to the CSV File!", "success")
    return ("Your data has been saved to the CSV File")
    return render_template(addcsv.html)

@app.route("/addexcel", methods=["GET", "POST"])
def addexcel():
    if os.path.exists('templates/newproducts.xlsx'):
        df = pd.read_excel('templates/newproducts.xlsx')
    else:
        df = pd.DataFrame(columns=["product_name", "price","quantity"])
    # Get form data
    product_name = request.form.get('product_name')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    data = {
    "Product_name":[product_name],
    "price":[price],
    "quantity":[quantity]
}
    print(data)
    df = pd.DataFrame(data)
    new_entry = pd.DataFrame(data)
    df = pd.concat([df, new_entry], ignore_index=True)
    #  Write to an Excel file
    df.to_excel("templates/newproducts.xlsx",index=False)
    for row in data:
        print(row)
    print("Excel file saved successfully!")
    return ("Your data has been saved to the Excel File")
    return render_template(addcsv.html)


if __name__ == '__main__':
    app.run(debug=True)

