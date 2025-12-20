import sys
from io import BytesIO
from django import setup
from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler, WSGIRequest
from django.core.signals import request_started, request_finished
from django.http import HttpResponse
from django.urls import path

# ----------------------------
# 步骤 1: 初始化 Django 环境（无需完整项目）
# ----------------------------
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="django-insecure-测试密钥-仅供临时使用",  # 添加 SECRET_KEY
        ROOT_URLCONF=__name__,  # 直接在此文件中定义 URL 路由
        MIDDLEWARE=[
            "django.middleware.common.CommonMiddleware",  # 示例中间件
        ],
    )
    setup()  # 初始化 Django


# ----------------------------
# 步骤 2: 定义一个简单的视图和路由
# ----------------------------
def test_view(request):
    """测试视图，返回简单响应"""
    return HttpResponse("Hello from Django!", content_type="text/plain")


# 手动定义 URL 路由
urlpatterns = [
    path("test/", test_view),
]


# ----------------------------
# 步骤 3: 自定义中间件（用于验证中间件是否被触发）
# ----------------------------
class LoggingMiddleware:
    """自定义中间件，记录请求和响应的日志"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("Middleware: Process request (before view)")
        response = self.get_response(request)
        print("Middleware: Process response (after view)")
        return response


# 将自定义中间件添加到配置中
settings.MIDDLEWARE = ["__main__.LoggingMiddleware"] + settings.MIDDLEWARE


# ----------------------------
# 步骤 4: 手动创建 WSGIRequest 并触发处理流程
# ----------------------------
def simulate_django_request():
    # 1. 创建 WSGI environ 字典（模拟 HTTP 请求）
    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/test/",  # 对应定义的路由
        "QUERY_STRING": "",
        "wsgi.input": BytesIO(b""),  # 空的请求体
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "SERVER_NAME": "localhost",  # 服务器名称
        "SERVER_PORT": "8000",  # 服务器端口
        "wsgi.url_scheme": "http",  # 协议类型（HTTP/HTTPS）
    }

    # 2. 创建 Django 的 WSGIRequest 对象
    django_request = WSGIRequest(environ)

    # 3. 创建 Django 的 WSGIHandler（入口点）
    handler = WSGIHandler()

    # 4. 绑定信号监听器（验证信号是否触发）
    def on_request_started(sender, **kwargs):
        print("Signal: request_started triggered")

    def on_request_finished(sender, **kwargs):
        print("Signal: request_finished triggered")

    request_started.connect(on_request_started)
    request_finished.connect(on_request_finished)

    # 5. 纯手动调用 WSGIHandler 处理请求（触发完整流程）
    request_started.send(sender=handler.__class__)
    response = handler.get_response(django_request)
    request_finished.send(sender=handler.__class__)

    # 6. 输出结果
    print("\nResponse status code:", response.status_code)
    print("Response content:", response.content.decode())


# ----------------------------
# 执行测试
# ----------------------------
if __name__ == "__main__":
    simulate_django_request()
