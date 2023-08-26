from wtforms import Form, StringField, validators, IntegerField, ValidationError, form, EmailField, SelectField, PasswordField, TextAreaField
# import wtforms
from flask import session


class DetailsForm(Form):
    name = StringField('Name', validators=[validators.input_required(), validators.length(max=100)],
                       render_kw={"placeholder": "Enter the name you want on the quotation "})
    email = EmailField('Email', validators=[validators.input_required()],
                       render_kw={"placeholder": "Enter the email you want on the quotation "})
    volume = IntegerField('Volume', validators=[validators.input_required()],
                          render_kw={"placeholder": "Enter the volume in liters "})
    type_of_tank = SelectField('Click to select type of tank', choices=['Steel', 'GRP'],
                               validators=[validators.input_required()])

    def validate_volume(form, field):
        if field.data < 4:
            raise ValidationError("We are sorry, volume can't be less than 4")


class SignUpForm(Form):
    name = StringField('Name', validators=[validators.input_required(), validators.length(min=1, max=100)],
                       render_kw={"placeholder": "Enter the name you want on the quotation "})
    email = EmailField('Email', validators=[validators.input_required()],
                       render_kw={"placeholder": "Enter the email you want on the quotation "})
    country = StringField('Country', validators=[validators.input_required()],
                          render_kw={"placeholder": "Enter your country where the quotation is to be used "})
    telephone = StringField('Telephone', validators=[validators.input_required()],
                        render_kw={"placeholder": "Enter your telephone number with your country code"})
    password = PasswordField('Password', validators=[validators.input_required()],
                            render_kw={"placeholder": "Password"})


# This is for editing prices by admins
class SelectFieldToEditForm(Form):
    field_to_edit = SelectField('Click to select what you want to edit', choices=['GRP prices', 'Steel prices', 'Vat'],
                                validators=[validators.input_required()])


# This is for admin_quotation
class AdminQuotationForm(Form):
    name = StringField('Name', validators=[validators.input_required(), validators.length(max=100)],
                       render_kw={"placeholder": "Enter the name you want on the quotation "})
    company = StringField('Company', validators=[validators.input_required(), validators.length(max=100)],
                       render_kw={"placeholder":"Enter the company you want on the quotation.Type residential for noncompany"})
    address = StringField('Address', validators=[validators.input_required(), validators.length(max=100)],
                       render_kw={"placeholder": "Enter the address you want on the quotation "})
    mobile = StringField('Mobile', validators=[validators.input_required(), validators.length(max=100)],
                       render_kw={"placeholder": "Enter the telephone number of your client"})
    email = EmailField('Email', validators=[validators.input_required()],
                       render_kw={"placeholder": "Enter the email you want on the quotation "})
    volume = IntegerField('Volume', validators=[validators.input_required()],
                          render_kw={"placeholder": "Enter the volume in liters "})
    type_of_tank = SelectField('Click to select type of tank', choices=['Steel', 'GRP'],
                               validators=[validators.input_required()])
    transport = IntegerField('Transport Fees', render_kw={"placeholder": "Enter the transport fee, if none put 0"})