from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request

from models import UserInfo

admin_blueprint=Blueprint('admin',__name__,url_prefix='/admin')


@admin_blueprint.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('admin/login.html')
    elif request.method=='POST':
        dict1=request.form
        mobile=dict1.get('username')
        pwd=dict1.get('password')
        if not all([mobile,pwd]):
            return render_template('admin/login.html',
                                   msg='请填写用户名和密码')
        user=UserInfo.query.filter_by(isAdmin=True,mobile=mobile).first()
        if user is None:
            return render_template('admin/login.html',
                                   mobile=mobile,
                                   pwd=pwd,
                                   msg='用户名错误')
        if not user.check_pwd(pwd):
            return render_template('admin/login.html',
                                   mobile=mobile,
                                   pwd=pwd,
                                   msg='密码错误')
        return redirect('/admin/')
@admin_blueprint.route('/')
def index():
    return render_template('admin/index.html')