from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Department
from users.serializaers import DepartmentSerializer


def index(request):
    return HttpResponse('首页')

class DepartmentListAPIView(APIView):


    def get(self,request):
        """查询多条数据"""
        #查询所以部门的对象
        query_set=Department.objects.all()
        #创建序列化器（当传入的对象有多个时需要指定many=true
        serializer=DepartmentSerializer(query_set,many=True)
        #返回响应对应
        return Response(serializer.data)


    def post(self,request):
        """新增一条数据"""
        #创建序列化对象
        serializer=DepartmentSerializer(data=request.data)
        #验证参数的合法性
        #设置raise_exception=true后，出错时，会给客户端返回json出错信息
        serializer.is_valid(raise_exception=True)
        #保存部门导数据库表中
        serializer.save()
        #返回响应对象
        return Response(serializer.data)
class DepartmentDetailAPIView(APIView):

    def get(self,request,pk):
        """查询一条数据"""
        try:
            department=Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return Response(status=404)
        #创建序列化对象
        serializer=DepartmentSerializer(department)
        #返回响应对象，并传递字典数据
        return Response(serializer.data)

    def put(self,request,pk):
        """修改部门"""
        #要修改的部门对象
        try:
            department=Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return HttpResponse(status=404)
        #创建序列化器对象
        serializer=DepartmentSerializer(department,data=request.data)
        #验证参数的合法性
        #raise_exception=True;如果校验不通过，会返回json出错信息给客户端
        serializer.is_valid(raise_exception=True)
        #保存到数据库中
        #上面的代码，当创建DepartmentSerializer对象时，第一个参数传入了部门对象
        #则在调用save()方法时，会修改部门，如果没有传入对象，则会新增部门
        serializer.save()
        return Response(serializer.data)
    def delete(self,request,pk):
        #删除一个部门DELETE /departments/<pk>
        #查询要删除的部门对象
        try:
            department=Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return Response(status=404)
        #删除部门
        department.delete()
        #响应请求
        return Response(status=204)







"""
基于GENIRICAPIVIEW和扩展类，分装restAPI

"""
"""
users/urls.py
url(r'^department2/$',views.DepartmentListAPIView2.as_view())
"""

#users/views.py

class DepartmentListAPIView2(ListModelMixin,CreateModelMixin,GenericAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


    def get(self,request):
        return self.list(request)



    def post(self,request):
        return self.create(request)


class DepartmentAPIView2(RetrieveModelMixin,UpdateModelMixin,DestroyModelMixin,GenericAPIView):


    queryset = Department.objects.all()

    serializer_class = DepartmentSerializer


    def get(self,request,pk):
        return self.retrieve(request,pk)

    def put(self,request,pk):
        return self.update(request,pk)

    def delete(self,request,pk):
        return self.destroy(request,pk)




class DepartmentListAPIView3(ListAPIView):
    """查询多个部门"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
