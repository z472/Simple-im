import threading
#当时可能不知道这个api，这就是它的意思，线程隔离
# 核心作用正好是线程安全的反面：它创建的是线程隔离
# 的变量，而不是线程共享的变量。线程共享的变量才会
# 出现线程安全问题。
# 类似的是contextvars.ContextVars('name')，但那个
# 只是一个上下文变量，local()这个是一个字典，所以更像
# 是contextvars.Context()这个是上下文字典，asyncio
# 协程配合使用，因为本来也是单线程内的协程嘛。和local()
# 类似的是 在不同协程中调用ContextVars()的命名一样，但
# 其实是隔离的不同内容。
threadLocal = threading.local()

class Executor(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        # Store name in object using self reference
        self.name = name

    def run(self):
        # Here we copy from object to local context,
        # since the thread is running
        threadLocal.name = self.name
        self.print_message()

    def print_message(self):
        print(self.name, ': ', vars(threadLocal))
   
A = Executor("A")
A.start()
B = Executor("B")
B.start()
print(vars(threadLocal))