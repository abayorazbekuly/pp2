import math

# 1) degree to radian
deg = float(input())
print(f"{math.radians(deg):.6f}")

# 2) area of a trapezoid: (a + b) / 2 * h
h = float(input())
a = float(input())
b = float(input())
print((a + b) * h / 2)

# 3) area of regular polygon: (n*s^2)/(4*tan(pi/n))
n = int(input())
s = float(input())
print((n * s * s) / (4 * math.tan(math.pi / n)))

# 4) area of a parallelogram: base * height
base = float(input())
height = float(input())
print(base * height)