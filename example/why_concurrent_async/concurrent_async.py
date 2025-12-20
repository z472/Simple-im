from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

"""ThreadPoolExecutor类源码速写：
    该类我愿称为多消费者线程的“协调者”
    单生产者(执行器类的self._work_queue，queue.SimpleQueue() )——多消费者work线程
        通过线程信号量来同步空闲的线程数量；
        通过queue的get让消费者无限等待，实际是put(_work_item())时候queue来唤醒一个
    等待线程实现的；
        通过线程普通锁确保在同一时间只有一个线程在做各种操作，submit(),shutdown()，
    还有全局的线程锁好像是和解释器是否退出相关

    线程池协调器退出逻辑：
        executor类退出逻辑是执行__exit__()中的shutdown()逻辑。
    先逐一关闭线程再关闭executor。但py出于一些理由不会直接关闭线程。
    thread.join()是阻塞并等线程target自己退出。否则每个消费者
    queue.get(block=True)会永久等待。
        每个target退出是接受executor.shutdown标志然后它自己return
    之前还要queue.put(None)告诉下一个等待的线程函数，传递出去，因为
    queue是根据内部顺序去给这些消费者进程去传递的，每次传一个None关闭
    一个对象，它不是Pub-sub那样群发给全部消费者。
    
    一个意外情况：executor先消失了，每个线程需要逐一关闭，这里用弱引用
    回调来实现。理论上应该是executor最后执行__exit__()中的shutdown()逻辑。
    先逐一关闭线程再关闭executor
    # When the executor gets lost, the weakref callback will wake up
        # the worker threads.
        def weakref_cb(_, q=self._work_queue):
            q.put(None)
    
    一个fork和线程锁的黑科技：
    if hasattr(os, 'register_at_fork'):
    os.register_at_fork(before=_global_shutdown_lock.acquire,
                        after_in_child=_global_shutdown_lock._at_fork_reinit,
                        after_in_parent=_global_shutdown_lock.release)
    # 1. fork 前：获取全局锁
    #    确保 fork 时没有线程在修改共享状态

    # 2. fork 后（子进程）：重新初始化锁
    #    _at_fork_reinit() 创建锁的新实例
    #    避免继承父进程的锁状态

    # 3. fork 后（父进程）：释放锁
    #    恢复正常的线程执行
"""
