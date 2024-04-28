from flask import Flask, render_template,redirect,request, flash, session
from database import User, add_to_db, File, open_db, Contact
# file upload 
from werkzeug.utils import secure_filename
from Common.file_utils import upload_file
from Common.helper import query
import pandas as pd
import plotly.express as px
app = Flask(__name__)
app.secret_key = 'thisissupersecretkeyfornoone'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print("Email =>", email)
        print("Password =>", password)
        # Logic for login
        # if dummy_user.password == password:
        #     return redirect('/')
        db = open_db()
        user = db.query(User).filter(User.email == email).first()
        if user:
            if user.password == password:
                flash("Login successful", 'success')
                session['user'] = user.id
                session['username'] = user.username
                session['email'] = user.email
                session['isauth'] = True
                return redirect('/')
            else:
                flash("Invalid password", 'danger')
                return redirect('/login')
        else:
            flash("User not found", 'danger')
            return redirect('/login')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        print(username, email, password, cpassword)
        # logic
        if len(username) == 0 or len(email) == 0 or len(password) == 0 or len(cpassword) == 0:
            flash("All fields are required", 'danger')
            return redirect('/register') # reload the page
        elif password != cpassword:
            flash("Passwords do not match", 'danger')
            return redirect('/register') # reload the page
        else:
            user = User(username=username, email=email, password=password)
            add_to_db(user)
            flash("Registration successful!", 'success')
            return redirect('/') # redirect to home page after successful registration
    return render_template('register.html') # render the register page

@app.route('/comment', methods=['GET', 'POST'])
def comment():
    if request.method == 'POST':
        # Get form data
        comment = request.form.get('comment')
        print(f"Comment: {comment}")
        if comment == "":
            flash("Comment is required", 'danger')
            return redirect('/comment')
        elif len(comment) < 10:
            flash("Comment is too short", 'danger')
            return redirect('/comment')
        elif len(comment) > 2000:
            flash("Comment is too long", 'danger')
            return redirect('/comment')
        try:
            output = query({"inputs": comment})
            print(output)
            results = pd.DataFrame(output[0])
            fig1 = px.pie(results, "label", "score", hole=.7)
            fig2 = px.bar(results, x="label", y="score")
            fig1 = fig1.to_html(full_html=False)
            fig2 = fig2.to_html(full_html=False)
            return render_template('result.html', fig1=fig1, fig2=fig2, 
                                comment=comment, 
                                results=results.to_html(classes='table table-striped table-hover table-bordered'))
        except Exception as e:
            print(e)
            flash("Please wait model is loading, refresh after 20 seconds", 'danger')
            return redirect('/comment')
    return render_template('comment.html')

@app.route('/file/upload', methods=['GET', 'POST'])
def file_upload():
    if request.method == 'POST':
        file = request.files['file']
        name = secure_filename(file.filename)
        path = upload_file(file, name)
        file = File(path=path, user_id=1)
        add_to_db(file)
        flash("File uploaded successfully", 'success')
    return render_template('upload.html')

@app.route('/file/list', methods=['GET', 'POST'])
def file_list():
    db = open_db()
    files = db.query(File).all()
    return render_template('display_list.html', files=files)

# 127.0.0.1:8000/file/4/view
@app.route('/file/<int:id>/view/')
def file_view(id):
    # code
    return render_template('view_file.html')

@app.route('/contact', methods=['GET','POST'])
def contact_info():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        phone = request.form['phone']
        # print(name, subject, email, message)
        if len(name) == 0 or len(phone) == 0 or len(email) == 0 or len(message) == 0:
            flash("All fields are required", 'danger')
            return redirect('/contact')
        contact = Contact(name=name, phone=phone, email=email, message=message)
        add_to_db(contact)
        flash("Message sent successfully", 'success')
        return redirect('/contact')

    return render_template('contact.html')
if __name__ == '__main__':

    app.run(host='127.0.0.1', port=8000, debug=True)
 