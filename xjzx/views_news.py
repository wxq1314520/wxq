from flask import Blueprint, session
from flask import render_template

from models import NewsCategory, UserInfo, NewsInfo

news_blueprint=Blueprint('news',__name__)
@news_blueprint.route('/')
def index():
    category_list=NewsCategory.query.all()
    if 'user_id' in session:
        user=UserInfo.query.get(session['user_id'])
    else:
        user=None
    count_list=NewsInfo.query.filter_by(status=2).order_by(NewsInfo.click_count.desc())[0:6]
    return render_template('news/index.html',
                           category_list=category_list,
                           user=user,
                           count_list=count_list)