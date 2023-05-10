import threading

def func1():
    print("1")
    pass

def func2():
    print("2")
    pass

def func3():
    print("3")
    pass

# 함수들을 리스트에 담습니다.
funcs = [func1, func2, func3]

# 스레드를 담을 리스트를 생성합니다.
threads = []

# 함수를 실행하는 스레드를 생성합니다.
for func in funcs:
    thread = threading.Thread(target=func)
    threads.append(thread)

# 모든 스레드를 실행합니다.
for thread in threads:
    thread.start()

# 모든 스레드가 종료될 때까지 대기합니다.
for thread in threads:
    thread.join()

print('모든 함수 실행 완료')
