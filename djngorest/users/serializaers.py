from rest_framework import serializers

from users.models import Department


class EmployeeSerializer(serializers.Serializer):
    choices_gender = (
        (0, '男'),
        (1, '女'),
    )
    id = serializers.IntegerField(read_only=True, label='ID')
    name = serializers.CharField(label='姓名', max_length=20)
    age = serializers.IntegerField(label='年龄')
    gender = serializers.ChoiceField(label='性别', default=0, choices=choices_gender)
    salary = serializers.DecimalField(label='工资', max_digits=8, decimal_places=2)
    comment = serializers.CharField(label='备注', max_length=300, allow_null=True, allow_blank=True)
    hire_date = serializers.DateField(label='入职时间')
    # 关联属性
    #方式一
    # department=serializers.PrimaryKeyRelatedField(label='所属部门',read_only=True)
    #方式二
    # department=DepartmentSerializer(read_only=True)

class DepartmentSerializer(serializers.Serializer):

    id=serializers.IntegerField(read_only=True,label='ID')
    name = serializers.CharField(max_length=20, label='部门名称')
    create_date = serializers.DateField(label='成立时间')
    is_delete = serializers.BooleanField(default=False, label='是否删除')

    # employee_set=serializers.PrimaryKeyRelatedField(read_only=True,many=True)
    employee_set=EmployeeSerializer(read_only=True,many=True)
    """部门序列化器"""
    ...

    def create(self, validated_data):
        """保存部门"""
        return Department.objects.create(**validated_data)
    def update(self, instance, validated_data):
        """修改部门:instance为要修改的部门对象，
            validated_data为用户发请求提交过来的数据，已经通过校验
        """
        instance.name=validated_data.get('name',instance.name)
        instance.create_date=validated_data.get('create_date',instance.create_date)
        instance.is_delete=validated_data.get('is_delete',instance.is_delete)
        instance.save() #修改数据库数据
        return instance





class DepartmentSerializer2(serializers.Serializer):
    employee_set=EmployeeSerializer()
    class Meta:
        model=Department
        exclude=('is_delete',)
        read_only_fields=('id',)