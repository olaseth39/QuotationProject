
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, send_from_directory
from flask import send_from_directory, make_response
from flask_mysqldb import MySQL, MySQLdb
from details import DetailsForm, SignUpForm, SelectFieldToEditForm, AdminQuotationForm, ResetRequestForm
from calculateDimensionForSteelGrp import SteelGRPDimension
from ComputeBestDimension import BestDimension
from passlib.hash import sha256_crypt
from functools import wraps
from figure_converter import convert_to_words
import os, requests
import uuid
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from random import randint
from itsdangerous import URLSafeTimedSerializer
from countries import country_and_currency_codes, country_codes_and_html
from api_currency_converter import CurrencyConverter
import pdfkit
import json


# werkzeug means work stuff in German. It is a library that comes with flask

# import mysql.connector

app = Flask(__name__)

# uncomment if mail does not work. I have written the same in the config file.
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'olaseth39@gmail.com'
app.config['MAIL_PASSWORD'] = 'tjmqvazoyuafpwrm'
app.config['MAIL_USE_TLS'] = False          # Transport Layer Security
app.config['MAIL_USE_SSL'] = True           # Secure Socket Layers

# make an instance of mysql
mysql = MySQL(app)

# make an instance of Mail
mail = Mail(app)


# connect to mysql

# app.config["MYSQL_HOST"] = "localhost"
# app.config["MYSQL_USER"] = "root"
# app.config["MYSQL_PASSWORD"] = ""
# app.config["MYSQL_DB"] = "quotation_formulator"
# app.config["MYSQL_CURSORCLASS"] = "DictCursor"

with open('config.json') as config_file:
    config_data = json.load(config_file)

# database configuration
db_settings = config_data['database']
app.config.update(db_settings)

# for tanks
steel = config_data['steel_tank']
grp = config_data['grp_tank']
vat = config_data['vat']

# for api
api = config_data['api']

# mail configuration
# mail_settings = config_data['mail_settings']
# app.config.update(mail_settings)

# We will be using File-uploads for uploading logos, picture or any document
# File-uploads allow flexibility and efficiency for files handling by our application

# set the path or directory where uploaded files would be stored
# app.config["UPLOADED_PHOTOS_DEST"] = "uploads"
app.config["UPLOAD_DIRECTORY"] = "static/uploads/"

# set maximum logo size limit
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024  # 1mb

# set the allowed extension
app.config["ALLOWED_EXTENSION"] = ['.jpg', '.jpeg', '.png', '.svg', '.gif']

# make an instance of the serializer
s = URLSafeTimedSerializer('mysecretkey')


@app.route('/', methods=['POST', 'GET'])
def home():
    form = DetailsForm(request.form)
    if request.method == 'POST' and form.validate():
        # get the values of data
        name = form.name.data
        email = form.email.data
        volume = form.volume.data
        type_of_tank = form.type_of_tank.data

        # This is from the API. It can only be used for Nigerian currencies and clients
        country = 'Nigeria'
        ngn_usd_er, usd_currency_code = 1, 1  # for NGN calculations
        currency_html = 8358
        currency_code = 'NGN'

        # get the value of unit_length for steel and grp to be used dynamically
        # create a cursor
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM grp_tank_details grp, steel_tank_details stl, vat vt")

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
            get_best_dimension = best_dimension.compute_best_dimension(type_of_tank)

        else:
            calculate_volume = SteelGRPDimension(volume)
            best_dimension = BestDimension(calculate_volume.calculate_dimension_grp(), grp_unit_length, 2)
            get_best_dimension = best_dimension.compute_best_dimension(type_of_tank)

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

        # data = []
        # if len(row) > 1:
        #     data = row[-1]  # select the last data
        #     data.append(data)

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
                               get_updated_prices=result,
                               result=result,
                               converter=convert_to_words,
                               country=country,
                               ngn_usd_er=ngn_usd_er,
                               usd_currency_code=usd_currency_code,
                               currency_html=currency_html,
                               currency_code=currency_code
                             )

    return render_template('home.html', form=form)

# proposed process to be taken for confirmation of email
# 1. confirmation link is sent after sign up
# 2. If the user clicks the link, they should be taken to login page and to the admin page after successfully logging in
# 3. In the event the confirmation link gets expired, initiate the resend link button
# 4. put the confirmed option in session

# 5. For users that could not be confirmed for one reason or the other and their  email has been used
# 6. Send a message showing this but they need to enter their password to get the link again
# 7. If their password does not correspond, they are to use another email to signup


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignUpForm(request.form)

    if request.method == 'POST' and form.validate():
        # get the values of data
        try:
            file = request.files.get('logo')
            # file = form.data['logo']

            if file:
                # sanitize the filename
                filename = secure_filename(file.filename)
                # get the extension
                extension = os.path.splitext(filename)[1].lower()
                # check for the right extension
                if extension not in app.config['ALLOWED_EXTENSION']:
                    flash("Image not allowed. Image must be jpeg, png, gif or svg", "warning")
                    return redirect("/signup")
                # save the file with the right extension
                file.save(os.path.join(app.config["UPLOAD_DIRECTORY"], filename))
            else:
                flash("You need to upload your company's logo. This will show on the quotation.", "warning")
                return redirect("/signup")

        # exception error for file larger than 100kb
        except RequestEntityTooLarge:
            flash("File must not be larger than 100kb", "warning")
            return redirect("/signup")

        # get the remaining data
        admin_name = form.name.data
        email = form.email.data
        country = form.country.data
        telephone = form.telephone.data
        company = form.company.data
        company_address = form.company_address.data
        bank_details = form.bank_details.data
        signatory = form.signatory.data
        password = sha256_crypt.hash(str(form.password.data))

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO admins(admin_name, email, country, telephone, password, company, company_address,bank_details ,signatory ,logo_path) \
                                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (admin_name, email, country, telephone, password, company, company_address, bank_details,
                         signatory, filename))


            # commit to database
            # cur.connection.commit()

            # let's insert the default price into grp and steel
            # We will first get the user's sign up id
            cur.execute("SELECT * from admins WHERE email=%s", [email])

            output = cur.fetchall()
            columns = output[0]
            id_ = columns['id']
            print(id_)

            session['id_'] = id_ # I didn't use this one again. It didn't work in some places
            print(session['id_'])

            # Now let's insert the default values int grp and steel tables
            # insert the values into db
            cur.execute("INSERT INTO steel_tank_details(unit_price, installation_price, "
                        "unit_length, admin_id, status_, quote_country)"
                        "VALUES(%s,%s, %s, %s, %s, %s)",
                        (steel['unit_price'], steel['installation_price'], steel['unit_length'],
                         id_, steel['status'], "Nigeria")
                        )

            cur.execute("INSERT INTO grp_tank_details(height_1m, height_2m, "
                        "height_3m, height_4m, installation_price, unit_length, admin_id, status_, quote_country)"
                        "VALUES(%s,%s, %s, %s, %s, %s, %s, %s, %s)",
                        (grp['h1'], grp['h2'], grp['h3'], grp['h4'],
                         grp['installation_price'], grp['unit_length'], id_, grp['status'], "Nigeria")
                        )

            cur.execute("INSERT INTO vat(vat, admin_id, status_) VALUES(%s, %s, %s)",
                        (vat['vat'], id_, vat['status']))

            # commit to db
            cur.connection.commit()

            cur.close()

        except (MySQLdb.Error, MySQLdb.Warning) as error:
            return render_template("signup.html", error=error, form=form)

        token = s.dumps(email, salt='email-confirmation-key')
        msg = Message('confirmation', sender='olaseth39@gmail.com', recipients=[email])
        link = url_for('confirm', token=token, eml=email, _external=True)
        msg.body = "Welcome! Thanks for signing in. Please follow this link to activate your account " + link
        mail.send(msg)

        # flash("Signed up successfully", "success")

        # return redirect(url_for("login"))

        return render_template("confirmation_msg.html", email=email)

    return render_template("signup.html", form=form)


@app.route('/confirm/<token>/<eml>', methods=['POST', 'GET'])
def confirm(token, eml):
    try:
        email = s.loads(token, salt='email-confirmation-key', max_age=3600)
    except Exception:

        return render_template('confirmation_fail_msg.html', email=eml)

    cur = mysql.connection.cursor()
    cur.execute("UPDATE admins SET confirmation_status='confirmed' where email= %s", [eml])
    cur.connection.commit()

    # let's get the confirmation_status
    cur.execute("SELECT confirmation_status FROM admins where email = %s", [eml])
    row = cur.fetchone()
    if row['confirmation_status'] == 'confirmed':
        session['confirmed'] = True
        session['email'] = eml
    cur.connection.commit()

    cur.close()

    return redirect(url_for('admin_page'))


@app.route("/resend_confirmation/<email>", methods=['POST', 'GET'])
def resend_confirmation(email):
    token = s.dumps(email, salt='email-confirmation-key')
    msg = Message('confirmation', sender='olaseth39@gmail.com', recipients=[email])
    link = url_for('confirm', token=token, eml=email, _external=True)
    msg.body = "Welcome! Thanks for signing in. Please follow this link to activate your account " + link
    mail.send(msg)

    return render_template('resent_confirmation_msg.html')


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
            user_id = data['id']

            # compare passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['email'] = email   #one email in session in the confirm route has been used
                session['user_id'] = user_id
                flash("You are Logged in successfully", "success")
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
        if "logged_in" or "confirmed" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized page, please login", "danger")
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
    cur.execute("SELECT company, company_address,logo_path, country, id FROM admins WHERE email = %s",
                [session['email']])

    # data for the particular client
    data = cur.fetchall()
    get_id = data[0]['id']  # we want to select the id
    session['get_id'] = get_id

    get_status = "Select from the dropdown to check the status"

    if request.method == 'POST' and form.validate():
        field_to_edit = form.field_to_edit.data

        price_list = ['GRP prices', 'Steel prices', 'Vat']
        tables = ['grp_tank_details', 'steel_tank_details', 'vat']
        tanks_dict = {'GRP prices': 'grp_tank_details', 'Steel prices': 'steel_tank_details', 'Vat':'vat'}

        # let's get the status of the table. This will be used to check whether the user needs to update the prices
        cur.execute("SELECT status_ FROM {} WHERE admin_id = %s ".format(tanks_dict[field_to_edit]), [get_id])
        status = cur.fetchone()
        get_status = status['status_']

        for val in enumerate(price_list):
            if field_to_edit == price_list[val[0]]:
                table = tables[val[0]]
                result = cur.execute("SELECT * FROM {} WHERE admin_id = %s".format(tables[val[0]]), [get_id])

                cur.connection.commit()

                if result > 0:
                    output = cur.fetchall()
                    return render_template("admin_page.html", results=output,get_status=get_status, table=table, form=form, data=data)

        cur.close()

    return render_template("admin_page.html", form=form, data=data, get_status=get_status)


@app.route("/serve_image/<file_name>", methods=['GET', 'POST'])
def serve_image(file_name):
    return send_from_directory(app.config["UPLOAD_DIRECTORY"], file_name)


@app.route('/my_client', methods=['GET', 'POST'])
@is_logged_in
def my_client():
    # create mysql connection
    cur = mysql.connection.cursor()

    # get admins quotation details from the admin_quote table
    row = cur.execute("SELECT q.* FROM admins adm, admin_quote q WHERE adm.email = %s AND adm.id = q.admin_id",
                      [session['email']])

    details = cur.fetchall()

    return render_template('clients.html', details=details)


@app.route("/edit_page/<table>", methods=['GET', 'POST'])
@is_logged_in
def edit_page(table):
    # create cursor to get id
    cur = mysql.connection.cursor()

    row = cur.execute("SELECT * FROM {} WHERE admin_id = %s".format(table), [session['get_id']])

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
            quote_country = request.form.get('quote_country', None)
            vat = request.form.get('vat', None)

            if table == "grp_tank_details":
                cur.execute("UPDATE grp_tank_details SET height_1m=%s,"
                            "height_2m=%s, height_3m=%s, height_4m=%s, installation_price=%s,"
                            "unit_length=%s, quote_country=%s WHERE admin_id=%s",
                            (height_1m, height_2m, height_3m, height_4m, installation_price, unit_length, quote_country, [session['get_id']]))

            elif table == "steel_tank_details":
                cur.execute("UPDATE steel_tank_details SET unit_price=%s, installation_price=%s, "
                            "unit_length=%s, quote_country=%s WHERE admin_id=%s",
                            (unit_price, installation_price, unit_length, quote_country, [session['get_id']]))

            elif table == "vat":
                cur.execute("UPDATE vat SET vat=%s", (vat,))

            else:
                msg = "You have made a wrong selection"
                return render_template("edit_page.html", msg=msg)

            cur.connection.commit()

            cur.close()

            # what to do if post request is successful
            flash("Details updated successfully", "success")

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
        country = form.country.data
        validity = form.validity.data
        delivery_installation = form.delivery_installation.data

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
            get_best_dimension = best_dimension.compute_best_dimension(type_of_tank)
            tank_selected = "steel_tank_details"  # used in the currency conversion

        else:
            calculate_volume = SteelGRPDimension(volume)
            best_dimension = BestDimension(calculate_volume.calculate_dimension_grp(), grp_unit_length, 2)
            get_best_dimension = best_dimension.compute_best_dimension(type_of_tank)
            tank_selected = "grp_tank_details" # used in the currency conversion

        # get admin id
        cur.execute("SELECT * FROM admins WHERE email= %s", [session['email']])

        output = cur.fetchall()  # result is a tuple of dictionary

        dict_row = output[0]  # get the first element containing the values we need

        id_admin = dict_row['id']  # get the id value

        logo = dict_row['logo_path']  # get the logo`

        c_address = dict_row['company_address'] # get the issuing company_address

        c_name = dict_row['company'] # get the issuing company_name

        bank_details = dict_row['bank_details'] # get the bank details

        signatory = dict_row['signatory'] # get signatory

        user_country = dict_row['country'] # get country

        # create a cursor
        # cur = mysql.connection.cursor()
        cur.execute("INSERT INTO admin_quote(name,company,address,mobile,email,volume,type_of_tank,transport, admin_id, validity, country, delivery_installation) \
                            VALUES(%s,%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)",
                            (name, company, address, mobile, email, volume, type_of_tank, transport, id_admin,
                             validity, country, delivery_installation))

        # commit to db
        cur.connection.commit()

        # create a cursor to get date
        cur = mysql.connection.cursor()
        cur.execute("SELECT date from admin_quote where email=%s", [email])
        row = cur.fetchall()

        data = row[-1]  # select the last data

        # Conversion procedure
        # first get the country of the company
        # convert the currencies to the country's, the default currency is in NGN
        # query the db for the unit price and convert them to the country's
        # Join the admins table with the tank tables such that each admin have their particular updated prices
        # then insert the new prices. This is to enable each of the admins to have their prices.

        # select the country code from the country selected from the dropdown
        currency_code = country_and_currency_codes[country]
        currency_html = country_codes_and_html[currency_code]

        # query for admin id
        # output = cur.execute("SELECT * FROM admins WHERE email=%s", [session['email']])
        # if output > 0:
        #     match = cur.fetchone()
        #     print(match)

        # query prices for both tanks and admin
        cur.execute("SELECT a.*, b.* FROM admins a, {} b WHERE a.email=%s and a.id = b.admin_id".format(tank_selected), [session['email']])

        price_items = cur.fetchall()  # tuple of dictionary
        print(price_items)
        price = price_items[0]  # get the last element dict
        print(price)

        admin_id = price['id']
        status = price['status_']
        quote_country_db = price['quote_country'] # this will be used where the prices have been changed
        h_1 = price['height_1m']
        h_2 = price['height_2m']
        h_3 = price['height_3m']
        h_4 = price['height_4m']

        # price_list = list(price.values())  # get the price values and change them to list
        # print(price_list)

        # conversion of currency via api
        # first let's convert from NGN to USD
        # We convert only if the status has not been changed, that is, it has not been converted before

        # first conversion is always to usd from ngn
        from_ngn = "NGN"
        to_usd = "USD"

        convert_to_usd = CurrencyConverter(api['currency']).convert_to_usd(from_ngn, to_usd)

        # Now convert to the required currency
        required_currency = CurrencyConverter(api['currency']).convert_to_currency(currency_code)

        # catch the unchanged status to convert
        if status == "unchanged" and currency_code != "NGN":
            # user_country is the sign in country while the other country is the country on the quote
            if quote_country_db == country:
                # check for steel
                # we are converting because the default price is in naira
                if tank_selected == "steel_tank_details":
                    unit_price = price['unit_price']
                    install_price_steel = price['installation_price']

                    unit_price_c = round(unit_price * convert_to_usd * required_currency, 0)
                    install_price_steel_c = round(install_price_steel * convert_to_usd * required_currency, 0)

                    # update the values into db
                    cur.execute("UPDATE steel_tank_details SET unit_price = %s, installation_price = %s,"
                                "status_ = %s, quote_country=%s WHERE admin_id = %s", (unit_price_c, install_price_steel_c, "changed", country, admin_id)
                                )

                # for grp
                else:

                    install_price_grp = price['installation_price']
                    h_1c = round(h_1 * convert_to_usd * required_currency, 0)
                    h_2c = round(h_2 * convert_to_usd * required_currency, 0)
                    h_3c = round(h_3 * convert_to_usd * required_currency, 0)
                    h_4c = round(h_4 * convert_to_usd * required_currency, 0)
                    install_price_grp_c = round(install_price_grp * convert_to_usd * required_currency, 0)
                    # print(h_1c)

                    # update the values into db
                    cur.execute("UPDATE grp_tank_details SET height_1m = %s, height_2m = %s, height_3m = %s,"
                                "height_4m = %s, installation_price=%s,status_ = %s, quote_country=%s WHERE admin_id = %s",
                                (h_1c, h_2c,h_3c,h_4c, install_price_grp_c, 'changed', country, admin_id)
                                )

            else:
                # if quote_country_db not equal country
                # first change from naira to user_country since naira is the default currency
                # then convert naira to the user country's denomination
                # then we now change to the country where the quotation is to be sent to

                # first change from naira to user_country, we have done this at the top

                required_currency = CurrencyConverter(api['currency']).convert_to_currency(currency_code)

                # check for steel
                if tank_selected == "steel_tank_details":
                    unit_price = price['unit_price']
                    install_price_steel = price['installation_price']

                    unit_price_c = round(unit_price * convert_to_usd * required_currency)
                    install_price_steel_c = round(install_price_steel * convert_to_usd * required_currency, 0)

                    # update the values into db
                    cur.execute("UPDATE steel_tank_details SET unit_price = %s, installation_price = %s",
                                "status_ = %s, quote_country=%s WHERE admin_id = %s",
                                (unit_price_c, install_price_steel_c, "changed", country, admin_id)
                                )
                    # for grp
                else:

                    install_price_grp = price['installation_price']
                    h_1c = round(h_1 * convert_to_usd * required_currency, 0)
                    h_2c = round(h_2 * convert_to_usd * required_currency, 0)
                    h_3c = round(h_3 * convert_to_usd * required_currency, 0)
                    h_4c = round(h_4 * convert_to_usd * required_currency, 0)
                    install_price_grp_c = round(install_price_grp * convert_to_usd * required_currency, 0)
                    # print(h_1c)

                    # update the values into db
                    cur.execute("UPDATE grp_tank_details SET height_1m = %s, height_2m = %s, height_3m = %s,"
                                "height_4m=%s,installation_price=%s,status_=%s,quote_country=%s WHERE admin_id = %s",
                                (h_1c, h_2c, h_3c, h_4c, install_price_grp_c, 'changed', country, admin_id)
                                )

        elif status == "changed" and currency_code != "NGN":
            # this is when prices are changed already. We will use the default prices
            # first query the tank table to get the quote_country
            # the query is at the top
            # then convert from using the quote_country to the delivering country

            if quote_country_db != country:
                # if quote_country_db not equal country which the quotation is being sent to
                quote_country_db_code = country_and_currency_codes[quote_country_db]
                convert_to_usd = CurrencyConverter(api['currency']).convert_to_usd(quote_country_db_code, to_usd)
                # Now convert to the required currency
                # recall currency_code is the code of the country from the admin's quotation
                required_currency = CurrencyConverter(api['currency']).convert_to_currency(currency_code)
                # check for steel
                if tank_selected == "steel_tank_details":
                    unit_price = price['unit_price']
                    install_price_steel = price['installation_price']

                    unit_price_c = round(unit_price * convert_to_usd * required_currency, 0)
                    install_price_steel_c = round(install_price_steel * convert_to_usd * required_currency, 0)

                    # update the values into db
                    cur.execute("UPDATE steel_tank_details SET unit_price = %s, installation_price = %s,"
                                "status_ = %s, quote_country=%s WHERE admin_id = %s",
                                (unit_price_c, install_price_steel_c, "changed", country, admin_id)
                                )

                else:

                    install_price = grp['installation_price']
                    h_1c = round(h_1 * convert_to_usd * required_currency, 0)
                    h_2c = round(h_2 * convert_to_usd * required_currency, 0)
                    h_3c = round(h_3 * convert_to_usd * required_currency, 0)
                    h_4c = round(h_4 * convert_to_usd * required_currency, 0)
                    install_price_grp_c = round(install_price * convert_to_usd * required_currency, 0)

                    # update the values into db
                    cur.execute("UPDATE grp_tank_details SET height_1m = %s, height_2m = %s, height_3m = %s,"
                                "height_4m=%s,installation_price=%s,status_= %s, quote_country=%s WHERE admin_id = %s",
                                (h_1c, h_2c, h_3c, h_4c, install_price_grp_c, 'changed', country, admin_id)
                                )

            else:
                # If they are the same we don't have to convert again
                convert_to_usd = 1
                required_currency = 1

                if tank_selected == "steel_tank_details":
                    unit_price = price['unit_price']
                    install_price_steel = price['installation_price']

                    unit_price_c = round(unit_price * convert_to_usd * required_currency, 0)
                    install_price_steel_c = round(install_price_steel * convert_to_usd * required_currency, 0)

                    # update the values into db
                    cur.execute("UPDATE steel_tank_details SET unit_price = %s, installation_price = %s,"
                                "status_ = %s, quote_country=%s WHERE admin_id = %s",
                                (unit_price_c, install_price_steel_c, "changed", country, admin_id)
                                )

                else:

                    install_price_grp = price['installation_price']
                    h_1c = round(h_1 * convert_to_usd * required_currency, 0)
                    h_2c = round(h_2 * convert_to_usd * required_currency, 0)
                    h_3c = round(h_3 * convert_to_usd * required_currency, 0)
                    h_4c = round(h_4 * convert_to_usd * required_currency, 0)
                    install_price_grp_c = round(install_price_grp * convert_to_usd * required_currency, 0)

                    # update the values into db
                    cur.execute("UPDATE grp_tank_details SET height_1m = %s, height_2m = %s, height_3m = %s,"
                                "height_4m = %s,installation_price=%s,status_=%s,quote_country=%s WHERE admin_id = %s",
                                (h_1c, h_2c, h_3c, h_4c, install_price_grp_c, 'changed', country, admin_id)
                                )

        else:
            # this section is for Nigerians only

            if quote_country_db != country:
                # it is possible the user_country does not equal the country receiving the quotation
                # if quote_country_db not equal country which the quotation is being sent to
                quote_country_db_code = country_and_currency_codes[quote_country_db]
                convert_to_usd = CurrencyConverter(api['currency']).convert_to_usd(quote_country_db_code, to_usd)
                # Now convert to the required currency
                # recall currency_code is the code of the country from the admin's quotation
                required_currency = CurrencyConverter(api['currency']).convert_to_currency(currency_code)
                # check for steel
                if tank_selected == "steel_tank_details":
                    unit_price = price['unit_price']
                    install_price_steel = price['installation_price']

                    unit_price_c = round(unit_price * convert_to_usd * required_currency, 0)
                    install_price_steel_c = round(install_price_steel * convert_to_usd * required_currency, 0)

                    # update the values into db
                    cur.execute("UPDATE steel_tank_details SET unit_price = %s, installation_price = %s,"
                                "status_ = %s, quote_country=%s WHERE admin_id = %s",
                                (unit_price_c, install_price_steel_c, "changed", country, admin_id)
                                )

                else:

                    install_price = grp['installation_price']
                    h_1c = round(h_1 * convert_to_usd * required_currency, 0)
                    h_2c = round(h_2 * convert_to_usd * required_currency, 0)
                    h_3c = round(h_3 * convert_to_usd * required_currency, 0)
                    h_4c = round(h_4 * convert_to_usd * required_currency, 0)
                    install_price_grp_c = round(install_price * convert_to_usd * required_currency, 0)

                    # update the values into db
                    cur.execute("UPDATE grp_tank_details SET height_1m = %s, height_2m = %s, height_3m = %s,"
                                "height_4m=%s,installation_price=%s,status_= %s, quote_country=%s WHERE admin_id = %s",
                                (h_1c, h_2c, h_3c, h_4c, install_price_grp_c, 'changed', country, admin_id)
                                )

            else:
                convert_to_usd = 1
                required_currency = 1

                if tank_selected == "steel_tank_details":
                    unit_price = price['unit_price']
                    install_price_steel = price['installation_price']

                    # update the values into db
                    cur.execute("UPDATE steel_tank_details SET unit_price = %s, installation_price = %s,"
                                "status_ = %s, quote_country=%s WHERE admin_id = %s",
                                (unit_price, install_price_steel, "changed", country, admin_id)
                                )

                else:
                    
                    install_price_grp = grp['installation_price']

                    # update the values into db
                    cur.execute("UPDATE grp_tank_details SET height_1m = %s, height_2m = %s, height_3m = %s,"
                                "height_4m = %s,installation_price=%s,status_=%s,quote_country=%s WHERE admin_id = %s",
                                (h_1, h_2, h_3, h_4, install_price_grp, 'changed', country, admin_id)
                                )

        # query prices for both tanks and admin for the updated price
        cur.execute(
            "SELECT a.*, b.* FROM admins a, {} b WHERE a.email=%s and a.id = b.admin_id".format(tank_selected),
            [session['email']])

        updated_prices = cur.fetchall()               # tuple
        get_updated_prices = updated_prices[0]  # dict
        print('This is the updated value', get_updated_prices)

        # commit to db
        cur.connection.commit()

        # close connection
        cur.close()

        # return redirect(url_for("quotation"))
        return render_template('quotation.html',
                               volume=volume,
                               company=company,
                               address=address,
                               c_address=c_address,
                               c_name=c_name,
                               bank_details=bank_details,
                               signatory=signatory,
                               mobile=mobile,
                               get_best_dimension=get_best_dimension,
                               name=name,
                               email=email,
                               type_of_tank=type_of_tank,
                               transport=transport,
                               country=country,
                               data=data,
                               result=result,
                               logo=logo,
                               currency_html=currency_html,
                               currency_code=currency_code,
                               validity=validity,
                               delivery_installation=delivery_installation,
                               quote_country=quote_country_db,
                               convert_to_usd=convert_to_usd,
                               required_currency=required_currency,
                               get_updated_prices=get_updated_prices
                               )

    return render_template("admin_quotation.html", form=form)


# route for getting quotation in pdf format
@app.route('/pdf_quote', methods=['GET', 'POST'])
@is_logged_in
def get_pdf_quote():

    admin_quotation().get_pdf()

    def get_pdf():
        rendered = render_template('quotation.html')

        # change from html format to string and keep in memory for now(that's why we used False)
        pdf = pdfkit.from_string(rendered, False)

        # enable additional headers to be added to the view(i.e. stringed html, pdf) using the make_response
        response_ = make_response(pdf)

        # change the content type to pdf for the browser
        response_.headers['Content-Type'] = 'application/pdf'

        # tell the browser how to handle the file and specify the filename
        response_.headers['Content-Disposition'] = 'attachment; file_name=output.pdf'

        return response_


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ResetRequestForm()
    if request.method == "POST" and form.validate_on_submit():
        user = form.email.data
        code = str(uuid.uuid4())
        cur = mysql.connection.cursor()
        data = cur.execute("SELECT * FROM admins WHERE email = %s", [user])
        if data > 0:
            data = cur.fetchone()
            cur.execute("UPDATE admins SET token = %s WHERE email=%s", [code, user])
            cur.connection.commit()
            cur.close()
            flash("Reset request sent. You can now change your password.", "success")
            return redirect(url_for("reset_password", token=code))
        flash("You will receive a password reset email if your email is found in our database ", "success")
    return render_template('forgot_password.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):

    if request.method == "POST":
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        new_token = str(uuid.uuid4())

        if password != confirm_password:
            flash("Passwords does not match", "danger")
            return redirect(request.url)

        new_password = sha256_crypt.hash(str(password))
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admins WHERE token=%s", [token])

        user = cur.fetchone()
        if user:
            cur.execute("UPDATE admins SET password=%s, token=%s WHERE token=%s", [new_password, new_token, token])
            flash("Password updated successfully.", "success")
            cur.connection.commit()
            cur.close()
            return redirect(url_for("login"))

    return render_template('password_reset.html')


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

