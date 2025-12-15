import tornado
import threading
from contextlib import suppress
from django.core import signals
from django import http
from django.core.handlers.base import BaseHandler
from django.http import HttpRequest, HttpResponse as DjaHttpRequest, DjaHttpResponse
from django.urls import set_script_prefix
from tornado.httputil import HTTPServerRequest as TorHttpRequest
from tornado.iostream import StreamClosedError
from tornado.wsgi import WSGIContainer
from django.core.handlers.wsgi import WSGIRequest, get_script_name
from typing import Any
from asgiref.sync import sync_to_async, async_to_sync
from urllib.parse import unquote


class AsynchronousResponse(DjaHttpRequest):
    """
    This response is just a sentinel to be discarded by Tornado and replaced
    with a real response later; see zulip_finish.
    """
    status_code = 399

# todo: 是否有线程安全要test
current_handler_id = 0
handlers: dict[int, "AsyncDjangoHandler"] = {}
# https://www.tornadoweb.org/en/stable/wsgi.html 
# https://peps.python.org/pep-3333/ (复习wsgi,asgi)
# 该类接受wsgi_app为参数-> tornado.web.Application但这里只要它的
# environ字典
fake_wsgi_container = WSGIContainer(lambda environ, start_response: [])


def allocate_handler_id(handler: "AsyncDjangoHandler") -> int:
    global current_handler_id
    handlers[current_handler_id] = handler
    handler_id = current_handler_id
    current_handler_id += 1
    return handler_id

class AsyncDjangoHandler(tornado.web.RequestHandler):
    handler_id: int
    
    def initialize(self, django_handler: BaseHandler) -> None:
        # 这是可以在tornado 每个mvc中运行django MVT的关键，
        # 手动触发django wsgihandler默认处理http请求的完整逻辑
        # 复制django.core.handler.WsgiHandler类的__call__
        # get()内的很多行为都是复制__call__
        self.django_handler = django_handler
        # Prevent Tornado from automatically finishing the request
        self._auto_finish = False

        # Handler IDs are allocated here, and the handler ID map must
        # be cleared when the handler finishes its response.  See
        # on_finish and on_connection_close.
        self.handler_id = allocate_handler_id(self)

        self._request: TorHttpRequest | None = None
    
    async def get(self, *args: Any, **kwargs: Any) -> None:
        request = await self.convert_tornado_request_to_django_request()
        response = await sync_to_async(
            lambda: self.django_handler.get_response(request), thread_sensitive=True
        )()

        try:
            if isinstance(response, AsynchronousResponse):
                # 长轮询的逻辑，没有服务器对应的响应，不更新
                # todo:非阻塞记录log_data
                pass
            else:
                # For normal/synchronous requests that don't end up
                # long-polling, we just need to write the HTTP
                # response that Django prepared for us via Tornado.
                assert isinstance(response, DjaHttpResponse)
                await self.write_django_response_as_tornado_response(response)
        finally:
            # Tell Django that we're done processing this request on
            # the Django side; this triggers cleanup work like
            # resetting the urlconf and any cache/database
            # connections.From wsgihandler's superClass base.BaseHandler.
            await sync_to_async(response.close, thread_sensitive=True)()
    
    async def convert_tornado_request_to_django_request(self) -> DjaHttpRequest:
        # 转化tornado request为wsgi environ
        environ = fake_wsgi_container.environ(self.request)
        # 转url编码为str
        environ["PATH_INFO"] = unquote(environ["PATH_INFO"])

        # Django WSGIRequest setup code 
        set_script_prefix(get_script_name(environ))
        await sync_to_async(
            lambda: signals.request_started.send(sender=type(self.django_handler)),
            thread_sensitive=True,
        )()
        self._request = WSGIRequest(environ)        

        return self._request

    async def write_django_response_as_tornado_response(self, response:DjaHttpResponse) -> None:
        # This takes a Django HttpResponse and copies its HTTP status
        # code, headers, cookies, and content onto this
        # tornado.web.RequestHandler (which is how Tornado prepares a
        # response to write).

        # Copy the HTTP status code/headers/cookies/response content to cls().
        self.set_status(response.status_code)
        for name, value in response.items():
            self.set_header(name, value)        
        if not hasattr(self, "_new_cookies"):
            self._new_cookies: list[http.cookie.SimpleCookie] = []
        self._new_cookies.append(response.cookies)
        self.write(response.content)

        # Close the connection.
        # While writing the response, we might realize that the
        # user already closed the connection; that is fine.
        with suppress(StreamClosedError):
            await self.finish()

handlers_local = threading.local()
handlers_local.connsum = 0

class MainPageHandler(tornado.web.RequestHandler):
    
    def initialize(self, userid:int):
        print('Userid:',int(userid))
        handlers_local.connsum += 1
        
    def get(self, anystr:str):
        print(f'From {anystr} {handlers_local.connsum} requests.')
        