from flask import Flask, request, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL, MySQLdb
from details import DetailsForm, SignUpForm, SelectFieldToEditForm, AdminQuotationForm
from calculateDimensionForSteelGrp import SteelGRPDimension
from ComputeBestDimension import BestDimension
from passlib.hash import sha256_crypt
from functools import wraps
from figure_converter import convert_to_words
# import mysql.connector


app = Flask(__name__)

# make an instance of mysql
mysql = MySQL(app)


# connect to mysql
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "quotation_formulator"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"


@app.route('/', methods=['POST', 'GET'])
def home():

    form = DetailsForm(request.form)

    if request.method == 'POST' and form.validate():
        # get the values of data
        name = form.name.data
        email = form.email.data
        volume = form.volume.data
        type_of_tank = form.type_of_tank.data

        # # put name and email in session
        # session['name'] = name
        # session['email'] = email

        # get the value of unit_length for steel and grp to be used dynamically
        # create a cursor
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM grp_tank_details grp, steel_tank_details stl, vat vt")

        result = cur.fetchone()

        # convert result to a dictionary
        all_tanks_details = dict(result)

        # get the unit_length for grp
        grp_unit_length = all_tanks_details['unit_length']

        # get the unit_length for steel
        steel_unit_length = all_tanks_details['stl.unit_length']

        # check if the type_of_tank selected is steel or grp
        if type_of_tank == "Steel":
            calculate_volume = SteelGRPDimension(volume)
            best_dimension = BestDimension(calculate_volume.calculate_dimension_steel(), steel_unit_length, 1)
            get_best_dimension = best_dimension.compute_best_dimension()

        else:
            calculate_volume = SteelGRPDimension(volume)
            best_dimension = BestDimension(calculate_volume.calculate_dimension_grp(), grp_unit_length, 2)
            get_best_dimension = best_dimension.compute_best_dimension()

        # create a cursor
        # cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, volume, type_of_tank) \
                    VALUES(%s, %s, %s, %s)", (name, email, volume, type_of_tank))

        # commit to db
        cur.connection.commit()

        # create a cursor to get date
        cur = mysql.connection.cursor()
        cur.execute("SELECT date from users")
        row = cur.fetchall()

        if len(row) > 1:
            data = row[-1]  # select the last data

        # commit to db
        cur.connection.commit()

        # close connection
        cur.close()

        # return redirect(url_for("quotation"))
        return render_template('quotation.html',
                               volume=volume,
                               get_best_dimension=get_best_dimension,
                               name=name,
                               email=email,
                               type_of_tank=type_of_tank,
                               data=data,
                               result=result,
                               converter=convert_to_words
                               )

    return render_template('home.html', form=form)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignUpForm(request.form)

    if request.method == 'POST' and form.validate():
        # get the values of data
        admin_name = form.name.data
        email = form.email.data
        country = form.country.data
        telephone = form.telephone.data
        password = sha256_crypt.hash(str(form.password.data))

        # create a cursor
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO admins(admin_name, email, country, telephone, password) \
                                VALUES(%s, %s, %s, %s, %s)", (admin_name, email, country, telephone, password))

            # commit to db
            cur.connection.commit()

        except (MySQLdb.Error, MySQLdb.Warning) as error:
            return render_template("signup.html", error=error, form=form)

        # close connection
        cur.close()

        # flash("Signed up successfully", "success")

        return redirect(url_for("login"))

    return render_template("signup.html", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password_candidate = request.form['password']

        # create a cursor
        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM admins WHERE email = %s ", [email])

        cur.connection.commit()

        # Check if the email has been used
        if result > 0:
            data = cur.fetchone()
            password = data['password']

            # compare passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['email'] = email
                flash("You are Logged in successfully", "Success")
                return redirect(url_for("admin_page"))
            else:
                error = "Invalid email or password"
                return render_template("login.html", error=error)

            # close connection
            cur.close()

        else:
            error = "Email or Password not found"
            return render_template("login.html", error=error)

    return render_template("login.html")


# This is to check if the user is logged in
def is_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized page, please login", "Danger")
            return redirect(url_for("login"))
    return decorated_function


@app.route("/logout")
def logout():
    session.clear()
    flash("You are now logged out", "success")

    return redirect(url_for("home"))


@app.route("/admin_page", methods=['GET', 'POST'])
@is_logged_in
def admin_page():

    # get the form to edit
    form = SelectFieldToEditForm(request.form)

    # create mysql connection
    cur = mysql.connection.cursor()

    # get admins quotation details from the admin_quote table
    row = cur.execute("SELECT q.* FROM admins adm, admin_quote q WHERE adm.email = %s AND adm.id = q.admin_id",
                      [session['email']])

    details = cur.fetchall()

    if request.method == 'POST' and form.validate():
        field_to_edit = form.field_to_edit.data

        if field_to_edit == "GRP prices":
            # for grp
            table = "grp_tank_details"
            result = cur.execute("SELECT * FROM grp_tank_details")

            if result > 0:
                grp_data = cur.fetchall()
                return render_template("admin_page.html", results=grp_data, form=form, table=table, details=details)

        elif field_to_edit == "Steel prices":
            # for steel
            table = "steel_tank_details"
            result = cur.execute("SELECT * FROM steel_tank_details")

            if result > 0:
                steel_data = cur.fetchall()
                return render_template("admin_page.html", results=steel_data, form=form, table=table, details=details)

        elif field_to_edit == "Vat":
            # for vat
            table = "vat"
            result = cur.execute("SELECT * FROM vat")

            if result > 0:
                vat_data = cur.fetchall()
                return render_template("admin_page.html", results=vat_data, form=form, table=table, details=details)

        else:
            msg = "You have not selected anything, kindly select what you want to edit"
            return render_template("admin_page.html", msg=msg, form=form)

        cur.connection.commit()

        cur.close()


    return render_template("admin_page.html", form=form)


@app.route("/edit_page/<string:table>", methods=['GET', 'POST'])
@is_logged_in
def edit_page(table):
    # create cursor to get id
    cur = mysql.connection.cursor()

    row = cur.execute("SELECT * FROM {}".format(table))

    if row > 0:
        details = cur.fetchone()

        cur.connection.commit()

        if request.method == "POST":
            height_1m = request.form.get('height_1m', None)
            height_2m = request.form.get('height_2m', None)
            height_3m = request.form.get('height_3m', None)
            height_4m = request.form.get('height_4m', None)
            installation_price = request.form.get('installation_price', None)
            unit_length = request.form.get('unit_length', None)
            unit_price = request.form.get('unit_price', None)
            vat = request.form.get('vat', None)

            if table == "grp_tank_details":
                cur.execute("UPDATE grp_tank_details SET height_1m=%s,"
                            "height_2m=%s, height_3m=%s, height_4m=%s, installation_price=%s, unit_length=%s",
                            (height_1m, height_2m, height_3m, height_4m, installation_price, unit_length))

            elif table == "steel_tank_details":
                cur.execute("UPDATE steel_tank_details SET unit_price=%s, installation_price=%s, unit_length=%s",
                            (unit_price, installation_price, unit_length))

            elif table == "vat":
                cur.execute("UPDATE vat SET vat=%s ", (vat,))

            else:
                msg = "You have made a wrong selection"
                return render_template("edit_page.html", msg=msg)

            cur.connection.commit()

            cur.close()

            # what to do if post request is successful
            flash("Details updated successfully", "Success")

            return redirect(url_for("admin_page"))

    return render_template("edit_page.html", details=details)


@app.route('/admin_quotation', methods=['POST', 'GET'])
@is_logged_in
def admin_quotation():

    form = AdminQuotationForm(request.form)
    if request.method == 'POST' and form.validate():
        # get the values of data
        name = form.name.data
        company = form.company.data
        address = form.address.data
        mobile = form.mobile.data
        email = form.email.data
        volume = form.volume.data
        type_of_tank = form.type_of_tank.data
        transport = form.transport.data

        # get the value of unit_length for steel and grp to be used dynamically
        # create a cursor
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM grp_tank_details grp, steel_tank_details stl, vat vt")

        result = cur.fetchone()

        # convert result to a dictionary
        all_tanks_details = dict(result)

        # get the unit_length for grp
        grp_unit_length = all_tanks_details['unit_length']

        # get the unit_length for steel
        steel_unit_length = all_tanks_details['stl.unit_length']

        # check if the type_of_tank selected is steel or grp
        if type_of_tank == "Steel":
            calculate_volume = SteelGRPDimension(volume)
            best_dimension = BestDimension(calculate_volume.calculate_dimension_steel(), steel_unit_length, 1)
            get_best_dimension = best_dimension.compute_best_dimension()

        else:
            calculate_volume = SteelGRPDimension(volume)
            best_dimension = BestDimension(calculate_volume.calculate_dimension_grp(), grp_unit_length, 2)
            get_best_dimension = best_dimension.compute_best_dimension()

        # get admin id
        cur.execute("SELECT * FROM admins WHERE email= %s", [session['email']])

        output = cur.fetchall()  # result is a tuple of dictionary

        dict_row = output[0]  # get the first element containing the values we need

        id_admin = dict_row['id']  # get the id value

        # create a cursor
        # cur = mysql.connection.cursor()
        cur.execute("INSERT INTO admin_quote(name,company,address,mobile,email,volume,type_of_tank,transport, admin_id) \
                            VALUES(%s,%s, %s, %s, %s, %s, %s, %s, %s)",
                            (name, company, address, mobile, email, volume, type_of_tank, transport, id_admin))

        # commit to db
        cur.connection.commit()

        # create a cursor to get date
        cur = mysql.connection.cursor()
        cur.execute("SELECT date from admin_quote where email=%s", [email])
        row = cur.fetchall()

        data = row[-1]  # select the last data

        # commit to db
        cur.connection.commit()

        # close connection
        cur.close()

        # return redirect(url_for("quotation"))
        return render_template('quotation.html',
                               volume=volume,
                               company=company,
                               address=address,
                               mobile=mobile,
                               get_best_dimension=get_best_dimension,
                               name=name,
                               email=email,
                               type_of_tank=type_of_tank,
                               transport=transport,
                               data=data,
                               result=result,
                               id_admin=id_admin
                               )

    return render_template("admin_quotation.html", form=form)


if __name__ == "__main__":
    print("Starting Flask server for QuotationFormulator application")
    # print(dir(form))
    app.secret_key = "quotationsecrettanks"

    # calculate_volume = SteelGRPDimension(79)
    # best_dimension = calculate_volume.calculate_dimension_grp()
    # print(best_dimension)

    # calculate_volume = SteelGRPDimension(70)
    # print(calculate_volume.calculate_dimension())
    # get_best_dimension = BestDimension(calculate_volume.calculate_dimension())
    # print(get_best_dimension.compute_best_dimension())
    app.run(debug=True)

