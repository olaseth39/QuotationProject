from wtforms import Form, FileField, StringField, SubmitField, validators, IntegerField, ValidationError, form, EmailField, SelectField, PasswordField, TextAreaField
# import wtforms
from flask import session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileSize, FileStorage
from flask_uploads import UploadSet, IMAGES, configure_uploads

# photos = UploadSet('photos', IMAGES)


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
    # def __init__(self, photo, *args, **kwargs):
    #     self.photos = photo
    #     # got the correction from the link below
    #     # https://stackoverflow.com/questions/61953652/modifying-flaskforms-class-object-has-no-attribute-fields
    #     super(SignUpForm, self).__init__(*args, **kwargs)

    name = StringField('Name', validators=[validators.input_required(), validators.length(min=1, max=100)],
                       render_kw={"placeholder": "Enter the name you want on the quotation "})
    email = EmailField('Email', validators=[validators.input_required()],
                       render_kw={"placeholder": "Enter the email you want on the quotation "})
    # country = StringField('Country', validators=[validators.input_required()],
    #                       render_kw={"placeholder": "Enter your country where the quotation is to be used "})
    country = SelectField('Click to select country',
                          choices=['Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda',
                                   'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain',
                                   'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan',
                                   'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria',
                                   'Burkina Faso', 'Burundi', 'Cape Verde', 'Cambodia', 'Cameroon', 'Canada',
                                   'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros',
                                   'Congo', 'Costa Rica', "CÃ´te d'Ivoire", 'Croatia', 'Cuba', 'Cyprus',
                                   'Czech Republic (Czechia)', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic',
                                   'DR Congo', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea',
                                   'Estonia', 'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon', 'Gambia',
                                   'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea',
                                   'Guinea-Bissau', 'Guyana', 'Haiti', 'Holy See', 'Honduras', 'Hungary', 'Iceland',
                                   'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica',
                                   'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan',
                                   'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein',
                                   'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali',
                                   'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia',
                                   'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar',
                                   'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger',
                                   'Nigeria', 'North Korea', 'North Macedonia', 'Norway', 'Oman', 'Pakistan', 'Palau',
                                   'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal',
                                   'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saint Kitts & Nevis', 'Saint Lucia', 'Samoa',
                                   'San Marino', 'Sao Tome & Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles',
                                   'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia',
                                   'South Africa', 'South Korea', 'South Sudan', 'Spain', 'Sri Lanka',
                                   'St. Vincent & Grenadines', 'State of Palestine', 'Sudan', 'Suriname', 'Sweden',
                                   'Switzerland', 'Syria', 'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo',
                                   'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu',
                                   'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States',
                                   'Uruguay', 'Uzbekistan', 'Vanuatu', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia',
                                   'Zimbabwe'],
                          validators=[validators.input_required()]
                          )
    telephone = StringField('Telephone', validators=[validators.input_required()],
                        render_kw={"placeholder": "Enter your telephone number with your country code"})
    company = StringField('Your Company',
                            render_kw={"placeholder": "Enter the name of your company"})
    company_address = StringField('Company Address',
                            render_kw={"placeholder": "Enter the address of your company"})
    bank_details = StringField('Bank Details',
                                  render_kw={"placeholder": "Acct number/ Bank name"})
    signatory = StringField('Signatory',
                                  render_kw={"placeholder": "Enter name of signatory"})
    logo = FileField('Logo', render_kw={"placeholder": "Upload your logo"})
    password = PasswordField('Password', validators=[validators.input_required()],
                            render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign up')


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
    validity = StringField('Validity', render_kw={"placeholder": "Validity of quote e.g 10 days"},
                               validators=[validators.input_required()])
    delivery_installation = StringField('Delivery and Installation',render_kw={"placeholder": "Enter delivery and installation period e.g 5 weeks"},
                           validators=[validators.input_required()])
    transport = IntegerField('Transport Fees', render_kw={"placeholder": "Enter the transport fee, if none put 0"})
    country = SelectField('Click to select the country you want to send the quote to',
                          choices=['Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda',
                                   'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain',
                                   'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan',
                                   'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria',
                                   'Burkina Faso', 'Burundi', 'Cape Verde', 'Cambodia', 'Cameroon', 'Canada',
                                   'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros',
                                   'Congo', 'Costa Rica', "Cote d'Ivoire", 'Croatia', 'Cuba', 'Cyprus',
                                   'Czech Republic (Czechia)', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic',
                                   'DR Congo', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea',
                                   'Estonia', 'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon', 'Gambia',
                                   'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea',
                                   'Guinea-Bissau', 'Guyana', 'Haiti', 'Holy See', 'Honduras', 'Hungary', 'Iceland',
                                   'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica',
                                   'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan',
                                   'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein',
                                   'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali',
                                   'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia',
                                   'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar',
                                   'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger',
                                   'Nigeria', 'North Korea', 'North Macedonia', 'Norway', 'Oman', 'Pakistan', 'Palau',
                                   'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland',
                                   'Portugal',
                                   'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saint Kitts & Nevis', 'Saint Lucia',
                                   'Samoa',
                                   'San Marino', 'Sao Tome & Principe', 'Saudi Arabia', 'Senegal', 'Serbia',
                                   'Seychelles',
                                   'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia',
                                   'South Africa', 'South Korea', 'South Sudan', 'Spain', 'Sri Lanka',
                                   'St. Vincent & Grenadines', 'State of Palestine', 'Sudan', 'Suriname', 'Sweden',
                                   'Switzerland', 'Syria', 'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo',
                                   'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu',
                                   'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States',
                                   'Uruguay', 'Uzbekistan', 'Vanuatu', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia',
                                   'Zimbabwe'],
                          validators=[validators.input_required()]
                          )


class ResetRequestForm(FlaskForm):

    email = EmailField('Email', validators=[validators.input_required()],
                       render_kw={"placeholder": "Enter your email "})
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
    new_password = PasswordField('New Passwrd',
                                 [validators.DataRequired(), validators.length(min=4, max=80)]
                                 )






