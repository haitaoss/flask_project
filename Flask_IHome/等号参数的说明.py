from ihome.models import *

li = []
li.append(House.area_id == 1)

print(li)  # [<sqlalchemy.sql.elements.BinaryExpression object at 0x7f2d857b27f0>]

print(House.area_id.__eq__(1))  # ih_house_info.area_id = :area_id_1
print(1 == 1)  # True


# 其实我们的==号是魔法属性__eq__的简写。
# 我们的模型类重写了__eq__，所以House.area_id == 1 返回的是sql表单是，而不是True或者False

class Foo(object):
    def __eq__(self, other):
        return True


foo = Foo()
print(foo=="sdaf")


print(dir(1))