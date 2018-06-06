from flask_script.commands import Command

from models import UserInfo, db


class CreateAdminCommand(Command):
    def run(self):
        '''
        创建管理
        :return:
        '''
        mobile=input('请输入账号：')
        pwd=input('请输入密码：')
        #创建用户对象

        user_exists=UserInfo.query.filter_by(mobile=mobile).count()
        if user_exists>0:
            print('此账号以存在')
            return
        user = UserInfo()
        user.mobile=mobile
        user.password=pwd
        user.isAdmin=True
        db.session.add(user)
        db.session.commit()
        print('管理员创建成功')
