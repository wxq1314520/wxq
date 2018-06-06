import re

from datetime import datetime
from flask import  Blueprint,make_response,jsonify,request,current_app,session
from flask import redirect
from flask import render_template

from models import UserInfo, db, NewsInfo, NewsCategory

user_blueprint=Blueprint('user',__name__,url_prefix='/user')

@user_blueprint.route('/image_yzm')
def image_yzm():
    from utills.captcha.captcha import captcha
    name,yzm,image=captcha.generate_captcha()
    #yzm 表示随机生成的验证码字符串
    #将数据进行保存，方便对比
    session['image_yzm']=yzm
    #image表示图片的二进制数据
    response=make_response(image)
    #默认浏览器将数据作为text/html解析
    #需要告诉浏览器当前数据的类型为image/png
    response.mimetype='image/png'
    return response

@user_blueprint.route('/sms_yzm')
def sms_yzm():
    #接收数据：手机号，图片验证码
    dict1=request.args
    mobile=dict1.get('mobile')
    yzm=dict1.get('yzm')
    #对比图片验证码
    if yzm!=session['image_yzm']:
        return jsonify(result=1)

    #随机生成一个4为的验证码
    import random
    yzm2=random.randint(1000,9999)
    #将短信验证码进行保存用于验证
    session['sms_yzm']=yzm2

    #发送短信
    from utills.ytx_sdk.ytx_send import sendTemplateSMS
    #sendTemplateSMS(mobile,{yzm2,5}1)
    print(yzm2)

    return jsonify(result=2)
@user_blueprint.route('/register',methods=['POST'])
def register():
    #接收数据
    dict1=request.form
    mobile=dict1.get('mobile')
    yzm_image=dict1.get('yzm_image')
    yzm_sms=dict1.get('yzm_sms')
    pwd=dict1.get('pwd')

    # 验证数据的有效性
    #保证所以的数据都被填写，列表中只要有一个值为flase，则结果为flase
    if not all([mobile,yzm_image,yzm_sms,pwd]):
        return jsonify(result=1)
    #对比图片验证码
    if yzm_image!=session['image_yzm']:
        return jsonify(result=2)
    #对比短信验证码
    if int(yzm_sms) !=session['sms_yzm']:
        return jsonify(result=3)
    #判断验证码的长度
    import re
    if not re.match(r'[a-zA-Z0-9]{6,20}',pwd):
        return jsonify(result=4)
    #验证mobile是否存在
    mobile_count=UserInfo.query.filter_by(mobile=mobile).count()
    if mobile_count>0:
        return jsonify(result=5)
    #创建对象
    user=UserInfo()
    user.nick_name=mobile
    user.mobile=mobile
    user.password=pwd

    #提交到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except:
        current_app.logger_xjzx.error('用户注册访问数据库失败')
        return jsonify(result=7)
    return jsonify(result=6)

@user_blueprint.route('/login',methods=['POST'])
def login():
    #接收数据
    dict1=request.form
    mobile=dict1.get('mobile')
    pwd=dict1.get('pwd')

    # 验证有效性
    if not all([mobile,pwd]):
        return jsonify(result=1)
    user=UserInfo.query.filter_by(mobile=mobile).first()
    # 判断mobile是否正确
    if user:
        #进行密码对比,flask内部提供了密码加密对比的函数
        if user.check_pwd(pwd):
            # 状态保持
            session['user_id']=user.id
            #返回成功的结果
            return jsonify(result=4,avatar=user.avatar_url,nick_name=user.nick_name)
        else:
            #密码错误
            return jsonify(result=3)
    else:
        #如果查询不到数据返回none，表示mobile错误
        return jsonify(result=2)


@user_blueprint.route('/logout',methods=['POST'])
def logout():
    del session['user_id']
    return jsonify(result=1)
import functools
def login_required(view_fun):
    @functools.wraps(view_fun)
    def fun2(*args,**kwargs):
        if 'user_id' not in session:
           return redirect('/')
        return view_fun(*args,**kwargs)
    return fun2
@user_blueprint.route('/')
@login_required
def index():

    #获得当前登陆的用户编号
    user_id=session['user_id']
    #根据编号查询当前登陆的用户对象
    user=UserInfo.query.get(user_id)
    #将对象传递到魔板中，用于显示昵称和头像
    return render_template('news/user.html',user=user)

@user_blueprint.route('/base',methods=['GET','POST'])
@login_required
def base():
    user_id=session['user_id']
    user=UserInfo.query.get(user_id)
    if request.method=='GET':
        return render_template('news/user_base_info.html',user=user)
    elif request.method=='POST':
        #接收
        dict1=request.form
        signature=dict1.get('signature')
        nick_name=dict1.get('nick_name')
        gender=dict1.get('gender')
        #查询（展示时也需要查询，所以将代码在上面写一遍
        #为属性赋值
        user.signature=signature
        user.nick_name=nick_name
        user.gender=bool(gender)
        #提交数据库
        db.session.commit()
        return jsonify(result=1)
@user_blueprint.route('/pic',methods=['GET','POST'])
@login_required
def pic():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)

    if request.method == 'GET':
        return render_template('news/user_pic_info.html', user=user)
    elif request.method == 'POST':
        # 接收文件
        avatar = request.files.get('avatar')

        # 上传到七牛云，并返回文件名
        from utills.qiniu_xjzx import upload_pic
        filename = upload_pic(avatar)

        # 修改用户的头像属性
        user.avatar = filename

        # 提交保存到数据库
        db.session.commit()

        # 返回响应
        return jsonify(result=1,avatar=user.avatar)
    # user_id=session['user_id']
    # user=UserInfo.query.get(user_id)
    #
    # if request.method=='GET':
    #     return render_template('news/user_pic_info.html',user=user)
    # if request.method=='POST':
    #     #接受文件夹
    #     avatar=request.files.get('avatar')
    #     from utills.qiniu_xjzx import upload_pic
    #     filename=upload_pic(avatar)
    #
    #     user.avatar=filename
    #     db.session.commit()
    #     return jsonify(result=1,avatar=user.avatar)
@user_blueprint.route('/follow')
@login_required
def follow():
    user_id=session['user_id']
    user=UserInfo.query.get(user_id)
    user_list=user.follow_user
    #获取当前也值
    page=int(request.args.get('page','1'))
    #通过关联属性获取关注的用户对象
    #对查询的数据进行分页
    pagination=user.follow_user.paginate(page,4,False)
    #获取当前页数
    user_list=pagination.items
    #获取分页总数
    total_page=pagination.pages

    return render_template(
        'news/user_follow.html',
        user_list=user_list,
        total_page=total_page,
        page=page
        )


@user_blueprint.route('/collection')
@login_required
def collection():
    user_id = session['user_id']
    user=UserInfo.query.get(user_id)
    #获取当前页码值
    page=int(request.args.get('page','1'))
    #获取当前用户收藏的新闻列表
    pagination=user.news_collect.order_by(NewsInfo.update_time.desc()).paginate(page,4,False)
    #获取当前页的数据
    news_list=pagination.items
    #获取总页码值
    total_page=pagination.pages
    return render_template('news/user_collection.html',
                           news_list=news_list,
                           page=page,
                           total_page=total_page
                           )

@user_blueprint.route('/pass_info',methods=['GET','POST'])
@login_required
def pass_info():
    if request.method=='GET':
        return render_template('news/user_pass_info.html')
    elif request.method=='POST':
        # 接受用户输入
        # 1.接收数据
        # 2. 验证
        # 3. 值部位空
        dict1=request.form
        current_pwd=dict1.get('current_pwd')
        new_pwd=dict1.get('new_pwd')
        new_pwd2=dict1.get('new_pwd2')
        if not all([current_pwd,new_pwd,new_pwd2]):
            return  render_template('news/user_pass_info.html',
                                    msg='请将信息填写完整')
        if not re.match(r'[a-zA-Z0-9 ]{6,20}',current_pwd):
            return render_template('news/user_pass_info.html',
                                   msg='当前密码错误')
        if not re.match(r'[a-zA-Z0-9_]{6,20}',new_pwd):
            return render_template('news/user_pass_info.html',
                                   msg='密码格式错误')

        if new_pwd!=new_pwd2:
            return render_template('news/user_pass_info.html',
                                   msg='两次密码不一致')
        user=UserInfo.query.get(session['user_id'])
        if user.check_pwd(current_pwd):
            return render_template('news/user_pass_info.html',
                                   msg='当前密码错误')
        user.password=new_pwd
        db.session.commit()
        return render_template('news/user_pass_info.html',
                               msg='密码修改成功')



@user_blueprint.route('/news_release',methods=['GET','POST'])
@login_required
def news_release():
    category_list = NewsCategory.query.all()
    if request.method=='GET':

        return render_template('news/user_news_release.html',
                           category_list=category_list)
    elif request.method=='POST':
        # 接受用户填写的数据 创建新闻对象，保存到数据库中
        #1.接受用户输入的数据
        # 2. 验证
        #3 .保证数据不为空
        dict1=request.form
        title=dict1.get('title')
        category_id= dict1.get('category')
        summary= dict1.get('summary')
        content= dict1.get('content')
        news_pic=request.files.get('news_pic')
        print(title,category_id,summary,content,news_pic)
        if not all([title,category_id,summary,content,news_pic]):
            return render_template('news/user_news_release.html',
                                   msg='数据不能为空',category_list=category_list)
        from  utills.qiniu_xjzx import  upload_pic
        filename=upload_pic(news_pic)
        news=NewsInfo()
        news.category_id=category_id
        news.pic=filename
        news.title=title
        news.summary=summary
        news.content=content
        news.user_id=session['user_id']
        db.session.add(news)
        db.session.commit()

        return redirect('/user/news_list')


@user_blueprint.route('/news_list')
@login_required
def news_list():
    user_id=session['user_id']
    user=UserInfo.query.get(user_id)
    #接收page
    page=int(request.args.get('page','1'))
    #使用关联属性访问发布的对象
    pagination=user.news.order_by(NewsInfo.update_time.desc()).paginate(page,6,False)
    news_list=pagination.items
    total_page=pagination.pages
    return render_template('news/user_news_list.html',
                           news_list=news_list,
                           page=page,
                           total_page=total_page)

@user_blueprint.route('/news_update/<int:news_id>',methods=['GET','POST'])
def news_update(news_id):
    news=NewsInfo.query.get(news_id)
    category_list=NewsCategory.query.all()
    if request.method=='GET':
        return render_template('news/user_news_update.html',
                            news=news,
                               category_list=category_list)
    elif request.method=='POST':
        dict1 = request.form
        title = dict1.get('title')
        category_id = dict1.get('category')
        summary = dict1.get('summary')
        content = dict1.get('content')
        news_pic = request.files.get('news_pic')
        if not all([title, category_id, summary, content]):
            return render_template('news/user_news_release.html',
                                   msg='数据不能为空', category_list=category_list)
        if news_pic:
            from  utills.qiniu_xjzx import upload_pic
            filename = upload_pic(news_pic)
        news.category_id = category_id
        if news_pic:
            news.pic = filename
        news.title = title
        news.summary = summary
        news.content = content
        news.user_id = session['user_id']
        news.update_time=datetime.now()
        news.status=1
        db.session.commit()

        return redirect('/user/news_list')
















