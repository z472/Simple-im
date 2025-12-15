# jedi做LSP的时候，对于多根目录的vscode工作区有一个不好的现象就是。
# 即使配置了一个虚拟环境的解释器，打开不同目录的py文件，会在vscode的
# outline里出现第二个python进程。在查看一个函数的时候，它的代码提示就是
# 2份如果有2个工作区根目录，这个在vscode的process里面能明确看到。
# 下面代码无法执行，因为没有这个第三方包，但它是vscode中启动jedi语言服务器
# 的py脚本就是这样。
#     该问题可以把多个根目录合并到一个更重要的目录去“隐藏”起来。为了赶进度
# 还是先这样吧
#     有些背景知识是，现在的vscode的python拓展，需要手动安装jedi通过pip
# 才能正确切换到jedi而不是pylance（测试过），该拓展现在没有内置jedi了
#     与jedi相关还有一个bug，可能是只有我遇到了？就是vscode工作区的根目录
# 它无法视为一个包，无法import。很明显是一个逻辑错误。但更致命的某些vs py拓展版本
# 甚至无法让jedi功能正常，同样的jedi版本，就无法代码提示，会在鼠标那里一直
# 转圈reload。所以我没有更新ms-py的版本，使用的是2025.2.0 python extension
# 致命的py拓展版本问题我看到有一样的github issue，但最后也是切到Pylance没有下文
# 试过几乎所有LLM给的方法，如删除vscode拓展缓存文件都不对。
#     jedi的低内存占用让同样的第三方包，从pylance的1-2GB，有时候会把我分配的
# 4G wsl2进程给直接卡掉与win10 vscode的连接。而Jedi的分析解析只占用<200mb，
# 有代码跳转，代码结构展示，还要什么自行车啊


# from jedi_language_server.cli import cli
# cli()