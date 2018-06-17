from django.db import models

# Create your models here.
from django.db import models


class Department(models.Model):
    """部门模型类"""
    name = models.CharField(max_length=20, verbose_name='部门名称')
    create_date = models.DateField(verbose_name='成立时间')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    def __str__(self):
        return self.name

    class Meta(object):
        db_table = 'department'


class Employee(models.Model):
    """员工模型类"""
    choices_gender = (
        (0, '男'),
        (1, '女'),
    )

    name = models.CharField(verbose_name='姓名', max_length=20)
    age = models.IntegerField(verbose_name='年龄')
    gender = models.IntegerField(verbose_name='性别', default=0, choices=choices_gender)
    salary = models.DecimalField(verbose_name='工资', max_digits=8, decimal_places=2)
    comment = models.CharField(verbose_name='备注', max_length=300, null=True, blank=True)
    hire_date = models.DateField(verbose_name='入职时间', auto_now_add=True)
    # 关联属性
    department = models.ForeignKey('Department', verbose_name='所属部门')

    def __str__(self):
        return self.name

    class Meta(object):
        db_table = 'employee'


class User(models.Model):
    password = models.CharField(max_length=30)
