# 1) squares up to N
def squares_up_to(n: int):
    for i in range(1, n + 1):
        yield i * i


# 2) even numbers between 0 and n comma separated (n from console)
def evens(n: int):
    for i in range(0, n + 1):
        if i % 2 == 0:
            yield i

n = int(input())
print(",".join(map(str, evens(n))))


# 3) divisible by 3 and 4 between 0 and n
def div_by_3_and_4(n: int):
    for i in range(0, n + 1):
        if i % 12 == 0:
            yield i


# 4) squares from a to b
def squares(a: int, b: int):
    for i in range(a, b + 1):
        yield i * i


# 5) from n down to 0
def countdown(n: int):
    while n >= 0:
        yield n
        n -= 1