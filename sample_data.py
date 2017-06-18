import random, string, time

ns = lambda x: ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(x))


def assign_name(rng):
    return {i: ns(7) for i in range(rng)}


def gen_data(count):
    res = []
    name_count = 6
    names = assign_name(name_count)
    for i in range(count):
        id = random.randrange(1, name_count)
        res.append({
            "userid": id,
            "name": names[id],
            "activity": random.choice(["login", "logout", "withdraw", "deposit"]),
            "ip": "47.87.67." + str(random.randrange(10, 120)),
            "time": int(time.time()) + random.randrange(1, 500),
            "bal": random.randrange(1000, 10000),
            "dob": "1983-01-01"
        })
    return res

