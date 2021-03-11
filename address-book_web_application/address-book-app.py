# Import Flask modules
from flask import Flask, request, render_template,g,redirect,session,url_for
from flaskext.mysql import MySQL
app = Flask(__name__) 
app.secret_key = 'somesecretkeythatonlyishouldknow'
#db_endpoint = open("/home/ec2-user/dbserver.endpoint", 'r', encoding='UTF-8') 
# Configure mysql database
app.config['MYSQL_DATABASE_HOST'] = 'address-book-app-db.cjwejqo3nbep.us-east-1.rds.amazonaws.com' #db_endpoint.readline().strip()
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'spring2021'
app.config['MYSQL_DATABASE_DB'] = 'address'
app.config['MYSQL_DATABASE_PORT'] = 3306
#db_endpoint.close()
mysql = MySQL()
mysql.init_app(app)
connection = mysql.connect()
connection.autocommit(True)
cursor = connection.cursor()
# Write a function named `init_todo_db` which initializes the todo db
# Create P table within sqlite db and populate with sample data
# Execute the code below only once.

def init_address_db():
    drop_table = 'DROP TABLE IF EXISTS address.address;'
    address_table = """
    CREATE TABLE address(
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    number VARCHAR(100) NOT NULL,
    PRIMARY KEY (id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    data = """
    INSERT INTO address.address (name, number)
    VALUES
        ("James", "1234567890"),
        ("John", "67854"),
        ("Matt", "876543554");
    """
    cursor.execute(drop_table)
    cursor.execute(address_table)
    cursor.execute(data)

@app.route("/")
def index():
    
    keyword = ''
    persons = find_persons(keyword)
    return render_template('index.html', persons=persons, keyword=keyword, show_result=True, developer_name='U&C')
    # return render_template('index.html')
    # redirect('/')
# Write a function named `find_persons` which finds persons' record using the keyword from the address table in the db,
# and returns result as list of dictionary 
# `[{'id': 1, 'name':'XXXX', 'number': 'XXXXXX'}]`.
def find_persons(keyword):
    query = f"""
    SELECT * FROM address WHERE name like '%{keyword.strip().lower()}%';
    """
    cursor.execute(query)
    result = cursor.fetchall()
    persons =[{'id':row[0], 'name':row[1].strip().title(), 'number':row[2]} for row in result]
    if len(persons) == 0:
        persons = [{'name':'No Result', 'number':'No Result'}]
    return persons
def get_person_byId(id):
    query = f"""
    SELECT * FROM address WHERE id={id}
    """
    cursor.execute(query)
    result = cursor.fetchall()
    persons =[{'id':row[0], 'name':row[1].strip().title(), 'number':row[2]} for row in result]
    if len(persons) == 0:
        persons = [{'name':'No Result', 'number':'No Result'}]
    return persons[0]
# Write a function named `insert_person` which inserts person into the address table in the db,
# and returns text info about result of the operation
def insert_person(name, number):
    query = f"""
    SELECT * FROM address WHERE name like '{name.strip().lower()}';
    """
    cursor.execute(query)
    row = cursor.fetchone()
    if row is not None:
        return f'Person with name {row[1].title()} already exits.'
    insert = f"""
    INSERT INTO address (name, number)
    VALUES ('{name.strip().lower()}', '{number}');
    """
    cursor.execute(insert)
    result = cursor.fetchall()
    return f'Person {name.strip().title()} added to address successfully'
# Write a function named `update_person` which updates the person's record in the address table,
# and returns text info about result of the operation
def update_person(id, name, number):
    query = f"""
    SELECT * FROM address WHERE id={id};
    """
    cursor.execute(query)
    row = cursor.fetchone()
    if row is None:
        return f'Person with name {name.strip().title()} does not exist.'
    update = f"""
    UPDATE address
    SET name='{name}', number = '{number}'
    WHERE id= {row[0]};
    """
    try:
        cursor.execute(update)
    except:
        return f'Exception Phone record of {name.strip().title()}'
    return f'Phone record of {name.strip().title()} is updated successfully'
# Write a function named `delete_person` which deletes person record from the address table in the db,
# and returns returns text info about result of the operation
def delete_person(id):
    query = f"""
    SELECT * FROM address WHERE id={id};
    """
    cursor.execute(query)
    row = cursor.fetchone()
    if row is None:
        return f'Person does not exist, no need to delete.'
    delete = f"""
    DELETE FROM address
    WHERE id={id};
    """
    cursor.execute(delete)
    return f'Phone record deleted from the address successfully'
# Write a function named `find_records` which finds phone records by keyword using `GET` and `POST` methods,
# using template files named `index.html` given under `templates` folder
# and assign to the static route of ('/')
    
@app.route('/', methods=['POST'])
def find_records():
    keyword = request.form['username']
    persons = find_persons(keyword)
    return render_template('index.html', persons=persons, keyword=keyword, show_result=True, developer_name='U&C')
        
# @app.route('/', methods=['GET'])

# Write a function named `add_record` which inserts new record to the database using `GET` and `POST` methods,
# using template files named `add-update.html` given under `templates` folder
# and assign to the static route of ('add')
@app.route('/add', methods=['GET', 'POST'])
def add_record():
    if request.method == 'POST':
        name = request.form['username']
        if name is None or name.strip() == "":
            return render_template('add-update.html', not_valid=True, message='Invalid input: Name can not be empty', show_result=False, action_name='save', developer_name='U&C')
        elif name.isdecimal():
            return render_template('add-update.html', not_valid=True, message='Invalid input: Name of person should be text', show_result=False, action_name='save', developer_name='U&C')
        phone_number = request.form['phonenumber']
        if phone_number is None or phone_number.strip() == "":
            return render_template('add-update.html', not_valid=True, message='Invalid input: Phone number can not be empty', show_result=False, action_name='save', developer_name='U&C')
        elif not phone_number.isdecimal():
            return render_template('add-update.html', not_valid=True, message='Invalid input: Phone number should be in numeric format', show_result=False, action_name='save', developer_name='U&C')
        result = insert_person(name, phone_number)
        return redirect('/')
        # return render_template('add-update.html', show_result=True, result=result, not_valid=False, action_name='save', developer_name='U&C')
    else:
        return render_template('add-update.html', show_result=False, not_valid=False, action_name='save', developer_name='U&C')
# Write a function named `update_record` which updates the record in the db using `GET` and `POST` methods,
# using template files named `add-update.html` given under `templates` folder
# and assign to the static route of ('update')
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_record(id):
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        if name is None or name.strip() == "":
            return render_template('update.html', not_valid=True, message='Invalid input: Name can not be empty', show_result=False, action_name='update', developer_name='U&C')
        phone_number = request.form['phonenumber']
        if phone_number is None or phone_number.strip() == "":
            return render_template('update.html', not_valid=True, message='Invalid input: Phone number can not be empty', show_result=False, action_name='update', developer_name='U&C')
        elif not phone_number.isdecimal():
            return render_template('update.html', not_valid=True, message='Invalid input: Phone number should be in numeric format', show_result=False, action_name='update', developer_name='U&C')
        result = update_person(id, name, phone_number)
        return redirect('/')
    else:
        person = get_person_byId(id)
        return render_template('update.html', person=person, show_result=False, not_valid=False, action_name='update', developer_name='U&C')
# Write a function named `delete_record` which updates the record in the db using `GET` and `POST` methods,
# using template files named `delete.html` given under `templates` folder
# and assign to the static route of ('delete')
#@app.route('/delete', methods=['GET', 'POST'])
@app.route('/delete/<int:id>')
def delete_record(id):
    try:
        delete_person(id)
        return redirect('/')
    except:
        return 'There was a problem deletting that person'
    # if request.method == 'POST':
    #     name = request.form['username']
    #     if name is None or name.strip() == "":
    #         return render_template('delete.html', not_valid=True, message='Invalid input: Name can not be empty', show_result=False, developer_name='U&C')
    #     result = delete_person(name)
    #     return render_template('delete.html', show_result=True, result=result, not_valid=False, developer_name='U&C')
    # else:
    #     return render_template('delete.html', show_result=False, not_valid=False, developer_name='U&C')
# Add a statement to run the Flask application which can be reached from any host on port 80.
if __name__== '__main__':
    # init_address_db()
    # app.run(debug=True)
    # init_persons()
    app.run(host='0.0.0.0', port=80) 