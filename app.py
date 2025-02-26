from datetime import datetime  
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired

# Initialize Flask App
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)

# ------------------- USER MODEL -------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(10), nullable=False)  # Date in YYYY-MM-DD format
    gender = db.Column(db.String(10), nullable=False)

# ------------------- FORM -------------------
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])
    date = DateField("Date (YYYY-MM-DD)", format="%Y-%m-%d", validators=[DataRequired()])
    gender = SelectField("Gender", choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    submit = SubmitField("Submit")

# ------------------- ROUTES -------------------
@app.route("/")
def index():
    users = User.query.all()
    return render_template("index.html", users=users)

@app.route("/add", methods=["GET", "POST"])
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        new_user = User(
            name=form.name.data,
            age=form.age.data,
            date=form.date.data.strftime('%Y-%m-%d'),
            gender=form.gender.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash("User added successfully!", "success")
        return redirect(url_for("index"))
    return render_template("add_user.html", form=form)

@app.route("/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Ensure date is converted correctly
    if isinstance(user.date, str):
        user.date = datetime.strptime(user.date, '%Y-%m-%d')

    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.name = form.name.data
        user.age = form.age.data
        user.date = form.date.data.strftime('%Y-%m-%d')  # Store as string
        user.gender = form.gender.data
        db.session.commit()
        flash("User updated successfully!", "success")
        return redirect(url_for("index"))
    
    return render_template("edit_user.html", form=form)


@app.route("/delete/<int:user_id>")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", "danger")
    return redirect(url_for("index"))

# ------------------- RUN THE APP -------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    app.run(debug=True)
 
