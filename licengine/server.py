from flask import render_template, request, redirect
from flask_security import Security, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from flask_restless import APIManager
from flask_jwt import JWT, jwt_required


from licengine.app import app, db
from licengine.models import user_datastore, SomeStuff
from licengine.admin import init_admin

security = Security(app, user_datastore)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/mypage')
@login_required
def mypage():
    return render_template('mypage.html')


@app.route('/logout')
def log_out():
    logout_user()
    return redirect(request.args.get('next') or '/')


def authenticate(username, password):
    user = user_datastore.find_user(email=username)
    if user and username == user.email and check_password_hash(user.password, password):
        return user
    return None


def load_user(payload):
    user = user_datastore.find_user(id=payload['identity'])
    return user


jwt = JWT(app, authenticate, load_user)


@jwt_required()
def auth_func(**kw):
    pass


apimanager = APIManager(app, flask_sqlalchemy_db=db)
apimanager.create_api(SomeStuff,
                      methods=['GET', 'POST', 'DELETE', 'PUT'],
                      url_prefix='/api/v1',
                      collection_name='free_stuff',
                      include_columns=['id', 'data1', 'data2', 'user_id'])
apimanager.create_api(SomeStuff,
                      methods=['GET', 'POST', 'DELETE', 'PUT'],
                      url_prefix='/api/v1',
                      preprocessors=dict(GET_SINGLE=[auth_func],
                                         GET_MANY=[auth_func]),
                      collection_name='protected_stuff',
                      include_columns=['id', 'data1', 'data2', 'user_id'])


init_admin()

if __name__ == '__main__':
    db.init_app(app)
    with app.context():
        db.create_all()
