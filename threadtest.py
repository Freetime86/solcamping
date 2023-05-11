import threading, requests, time


def function_1():
    while True:
        print('function 1')


def function_2():
    while True:
        print('function 2')


def function_3():
    while True:
        print('function 3')


# 데몬 쓰레드
t1 = threading.Thread(target=function_1)
t2 = threading.Thread(target=function_2)
t3 = threading.Thread(target=function_3)

t1.start()
t2.start()
t3.start()

while True:
    pass
