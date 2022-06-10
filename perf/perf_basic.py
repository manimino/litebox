import random
import time
from dataclasses import dataclass
from rangeindex import RangeIndex


az = 'qwertyuiopasdfghjklzxcvbnm'
ten = list(range(10))


@dataclass
class Thing:
    x: int
    y: float
    desc: str


def make_thing():
    s = []
    for i in range(5):
        s.append(random.choice(az))
    return Thing(x=random.choice(ten), y=random.random(), desc=''.join(s))


def main(n=10**3):
    things = [make_thing() for _ in range(n)]
    ri = RangeIndex({'x': int, 'y': float})
    t0 = time.time()
    print('bout to add things')
    # time.sleep(5)
    print('ok here we go')
    ri.add_many(things)
    print('added things')
    # time.sleep(5)
    t1 = time.time()
    found_float = ri.find([('y', '<', 1), ('x', '<=', 0)])
    t2 = time.time()
    #found_str = ri.find([('desc', '<', 'zzzzz')])
    t3 = time.time()
    linear_find = tuple(filter(lambda t: t.y < 1 and t.x <= 0, things))
    t4 = time.time()
    print('t_add {} elements:'.format(len(things)), t1-t0)
    print('t_find {} elements:'.format(len(found_float)), t2-t1)
    #print('t_find {} elements:'.format(len(found_str)), t3-t2)
    print('linear find {} elements:'.format(len(linear_find)), t4-t3)

    print((t4-t3)/(t2-t1))


if __name__ == '__main__':
    main()