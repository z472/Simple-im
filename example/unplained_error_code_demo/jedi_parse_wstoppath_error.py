# jedi with vscode python 无法解析工作区顶级目录为一个python module，
# 也无法通过正确配置虚拟环境py解释器的sys.path或它的PYTHONPATH来改变
# 当然，pylance如果设置字段extrapath就可以正常使用，但jedi也可以通过
# 把上级目录移入工作区来解决此问题，jedi会正确解析，但要注意python拓展
# 如果版本太新，jedi即使是最新版本，他俩一起用也会出错，我目前是2025.2.0
# 版本正好完美联动最新的jedi 0.19.2版本。
# import distance
import jedi 
print(jedi.__version__)
import sys
print(sys.path)