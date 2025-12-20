import functools
import time


def ttl_cache(ttl_seconds):
    cache = {}
    # 注意下面这行，dubug的局部是相对断点
    # 所在行来说的局部作用域，如果直接离开该作用域
    # debug不会找到曾经进入又马上离开作用域的一个
    # 历史变量cache
    time.sleep(2)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args):
            now = time.time()
            if args in cache:
                value, timestamp = cache[args]
                if now - timestamp < ttl_seconds:
                    return value
            result = func(*args)
            cache[args] = (result, now)
            return result

        return wrapper

    return decorator


@ttl_cache(ttl_seconds=3)
def expensive(x):
    print("Computing...")
    return x * x


print("First call:")
print(expensive(4))
print("\nSecond call:")
print(expensive(4))
