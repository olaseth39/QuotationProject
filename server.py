from flask import Flask, request, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from details import DetailsForm
from calculateDimensionForSteelGrp import SteelGRPDimension
from ComputeBestDimension import BestDimension

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

        # check if the type_of_tank selected is steel or grp
        if type_of_tank == "Steel":
            calculate_volume = SteelGRPDimension(volume)
            best_dimension = BestDimension(calculate_volume.calculate_dimension_steel(), 1.22, 1)
            get_best_dimension = best_dimension.compute_best_dimension()

        else:
            calculate_volume = SteelGRPDimension(volume)
            best_dimension = BestDimension(calculate_volume.calculate_dimension_grp(), 1, 2)
            get_best_dimension = best_dimension.compute_best_dimension()

        # create a cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, volume, type_of_tank) \
                    VALUES(%s, %s, %s, %s)", (name, email, volume, type_of_tank))

        # commit to db
        cur.connection.commit()

        # close connection
        cur.close()

        flash("Successfully registered", "success")

        # return redirect(url_for("quotation"))
        return render_template('quotation.html',
                               volume=volume,
                               get_best_dimension=get_best_dimension,
                               name=name,
                               email=email,
                               type_of_tank=type_of_tank)

    return render_template('home.html', form=form)


@app.route("/quotation", methods=['GET', 'POST'])
def quotation():

    return render_template("home.html")


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

