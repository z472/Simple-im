import asyncio

# asyncio.task.cancel()
# 该方法安排在事件循环的下一个周期中将 CancelledError 异常
# 抛入包装的协程中。（注意这不是强制，保证取消了该协程该task，
# 它可以内部捕捉该异常并抑制效果，AI说在正在执行计算或释放资源
# 的时候也有“延迟”停止，这里感觉容易出bug，所以用官方文档的例子
# 来感受一下）

# async def cancel_me():
#     re = 0
#     try:
#         while 1:
#             await asyncio.sleep(0.1)
#             re += 0.1
#     except asyncio.CancelledError:
#         raise
#     finally:
#         return re

# async def main():
#     task = asyncio.create_task(cancel_me())
#     await asyncio.sleep(1)
#     task.cancel()
#     await asyncio.sleep(1)

#     try:
#         re = await task
#         print(f"re = {re}")
#     except asyncio.CancelledError:
#         print("main(): 捕获到CancelledError")

# asyncio.run(main())
# test1: re = 0.8999999999999999

# async def cancel_me():
#     re = 0
#     try:
#         while 1:
#             await asyncio.sleep(0.1)
#             re += 0.1
#     except asyncio.CancelledError:
#         raise
#     finally:
#         return re

# async def main():
#     task = asyncio.create_task(cancel_me())

#     task.cancel()
#     await asyncio.sleep(1)

#     try:
#         re = await task
#         print(f"re = {re}")
#     except asyncio.CancelledError:
#         print("main(): 捕获到CancelledError")

# asyncio.run(main())
# test2 : main(): 捕获到CancelledError怎么感觉

# async def cancel_me():
#     re = 0
#     try:
#         while 1:
#             await asyncio.sleep(0.1)
#             re += 0.1  # 加一行print(f're={re}')结果不变
#     except asyncio.CancelledError:
#         return re


# async def main():
#     task = asyncio.create_task(cancel_me())

#     task.cancel()
#     await asyncio.sleep(1) # 删了这行结果不变

#     try:
#         re = await task
#         print(f"re = {re}")
#     except asyncio.CancelledError:
#         print("main(): 捕获到CancelledError")

# asyncio.run(main())
# test3 ：main(): 捕获到CancelledError
# 结论：给一个没运行的task，直接task.cancel()，内部怎样都不会执行。
# 此时的取消是真停止行为了。不是文档讲的可能没停止行为。我也不懂为何先
# cancel再await task，这是文档的原版例子。
