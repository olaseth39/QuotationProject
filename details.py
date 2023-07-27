from wtforms import Form, StringField, validators, IntegerField, ValidationError, form, EmailField, SelectField
# import wtforms


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