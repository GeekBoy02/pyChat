import random

def generate_item():
    item_types = ['Blaster', 'Laser Pistol', 'Energy Sword', 'Plasma Rifle']
    item_type = random.choice(item_types)
    
    attributes = {
        'speed': random.randint(5, 20),
        'intellect': random.randint(10, 50),
        'luck': random.randint(60, 90),
        'weight': random.randint(1, 10),
        'rarity': random.choice(['Common', 'Uncommon', 'Rare', 'Epic'])
    }
    
    item = {
        'type': item_type,
        'attributes': attributes
    }
    
    return item
