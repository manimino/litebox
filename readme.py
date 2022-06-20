import random
import time
from rangeindex import RangeIndex

class CatPhoto:
    def __init__(self):
        self.width = random.choice(range(200, 2000))
        self.height = random.choice(range(200, 2000))
        self.brightness = random.random()*10
        self.name = random.choice(['Luna', 'Willow', 'Elvis', 'Nacho', 'Tiger'])
        self.image_data = 'Y2Ugbidlc3QgcGFzIHVuZSBjaGF0dGU='

# Make a million
photos = [CatPhoto() for _ in range(10**6)]

# Build RangeIndex
ri = RangeIndex(photos, 
                on={'height': int, 'width': int, 'brightness': float, 'name': str}, 
                engine='sqlite',
                table_index=[('width', 'height', 'brightness')])
                
# Find matches
import time
t0 = time.time()
matches = ri.find("height > 1900 and width >= 1900 and brightness >= 9 and name='Tiger'")
t1 = time.time()
match_generator = [p for p in photos if p.height > 1900 and p.width >= 1900 and p.brightness >= 9 and p.name == 'Tiger']
t2 = time.time()
print('gene time', t2-t1, len(match_generator))
print('match_time', t1-t0, len(matches))

