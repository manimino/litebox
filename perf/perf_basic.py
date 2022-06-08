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


def lots_of_things():
    n = 10**6
