"""
미적분 수행평가용
주제 : 자동미분 구현

작업기간
2022.07.05 ~ 2022.07.07

핵심 원리 : 역전파 알고리즘으로 함수식에 대한 미분 연산 없이 미분계수를 구할 수 있음
ex) 3x^2 + x + 1를 6x + 1로 미분하지 않고도 미분계수를 구할 수 있다

31214 지원재
"""
from dataclasses import dataclass

def add(a, b) :
    return a + b, (a, b)
def sub(a, b) :
    return a - b, (a, b)
def mul(a, b) :
    return a * b, (a, b)

def d_add(a, d = 1) :
    return 1 * d, 1 * d
def d_sub(a, d = 1) :
    return 1 * d, -1 * d
def d_mul(a, d = 1) :
    return a[1] * d, a[0] * d

class derivative :
    numerator : int = None # 분자 (임시변수 번호 a = 0, b =1 ..)
    denominator : int = None # 분모 (변수인 경우 연결된 인덱스 번호, 상수인 경우 -1, 임시변수인 경우 번호)
    denominator_type : int = None # 분모가 변수인 경우 0, 임시변수인 경우 1
    val : int = None # 미분계수 값

    def __init__(self, n, d, dt, v) :
        self.numerator = n
        self.denominator = d
        self.denominator_type = dt
        self.val = v

def find_number(string) :
    number = 0

    for i in string :
        # 상수값인 경우
        if 0x30 <= ord(i) and ord(i) <= 0x39 :
            # 두 자리 수, 세 자리 수 일 수도 있으므로 반복하며 읽어들인 후 number에 저장
            number *= 10
            number += int(i)
            continue # 다음으로

        # 상수값이 아닌데 number가 차있다??
        elif number != 0 :
            return int(number) # 찾은 상수값 반환
            
# 수식 중위 표기 => 후위 표기
def parser(string) :
    arr = []
    stack = []

    number = 0

    string += ' '
    # 계산구조 분석(한 글자씩)
    for i in range(0, len(string)) :
        character = string[i]
            
        # 상수값인 경우
        if 0x30 <= ord(character) and ord(character) <= 0x39 :
            # 두 자리 수, 세 자리 수 일 수도 있으므로 반복하며 읽어들인 후 number에 저장
            number *= 10
            number += int(character)
            continue # 다음으로

        # 상수값이 아닌데 number가 차있다??
        elif number != 0 :
            arr.append(str(number)) # 상수가 끝났으므로 arr에 뱉어줘야함
            number = 0

        # 변수인 경우
        if 0x61 <= ord(character) and ord(character) <= 0x7a :
            arr.append(character)
        
        # 연산자인 경우
        elif character == '*' :
            stack.append(character)

        elif character == '+' or character == '-' : 
            if len(stack) >= 1 :
                if stack[len(stack) - 1] == '*' :
                    for j in range(0, len(stack)) :
                        arr.append(stack.pop())
            stack.append(character)
    
    for i in range(0, len(stack)) :
        arr.append(stack.pop())

    
    return arr

def operate(formula, argn, argv) :
    formula_parsed = parser(formula)

    calc = formula
    for i in range(0, len(argn)) :
        calc = calc.replace(argn[i], argv[i])
    
    calc_parsed = parser(calc)
    derivatives = []
    temp_arg_count = 0

    # 미분계수 값을 derivatives에 정리하는 부분
    while len(formula_parsed) > 2 :
        for i in range(0, len(formula_parsed)) :

            operand = []
            operand_index = [-1, -1]
            operand_type = [0, 0]

            # 연산자가 걸리면
            operator = formula_parsed[i]
            if operator == '*' or operator == '+' or operator == '-' :

                # 피연산자 찾기(2개)
                j = i - 1
                while len(operand) < 2 :
                    if formula_parsed[j] != "+" and formula_parsed[j] != "-" and formula_parsed[j] != "*": # 피연산자라면
                        try :
                            operand_index[len(operand)] = argn.index(formula_parsed[j]) # 피연산자의 종류에 대한 정보 저장(상수인가? 변수인가?)
                        except :
                            operand_index[len(operand)] = -1
                            pass

                        # 임시변수일 경우
                        if formula_parsed[j][0] == '(' :
                            operand_index[len(operand)] = int(formula_parsed[j][1:]) # 임시변수의 번호를 확인해 저장
                            operand_type[len(operand)] = 1 # 인덱스 타입을 임시변수로 표시

                        operand.append(int(calc_parsed[j])) # 피연산자 목록에 추가

                        # 추가한 피연산자를 수식에서 지움
                        del calc_parsed[j]
                        del formula_parsed[j]
                        j -= 1

                v = 0
                cache_v = (0, 0)
                d_1 = 0
                d_2 = 0

                if operator == '*':
                    v, cache_v = mul(operand[0], operand[1])
                    d_1, d_2 = d_mul(cache_v)
                if operator == '+':
                    v, cache_v = add(operand[0], operand[1])
                    d_1, d_2 = d_add(cache_v)
                if operator == '-' :
                    v, cache_v = sub(operand[1], operand[0])
                    d_2, d_1 = d_sub(cache_v)

                # 계산식에 계산한 결과를 반영
                calc_parsed[j + 1] = str(v)
                formula_parsed[j + 1] = "(" + str(temp_arg_count)

                # 계산한 미분계수 저장
                if operand_index[0] != -1 :
                    derivatives.append(derivative(temp_arg_count, operand_index[0], operand_type[0], d_1))
                if operand_index[1] != -1 :
                    derivatives.append(derivative(temp_arg_count, operand_index[1], operand_type[1], d_2))

                temp_arg_count += 1
                break

    # 위 반복을 마친 시점에서 쪼개진 미분계수 값들이 derivatives에 정리되어 있음

    derivative_paths = []

    # 그걸 각 경로를 따라 한데 모은다
    while len(derivatives) > 0 :
        
        d = derivatives[len(derivatives) - 1]
        isTheEnd = 1
        for i in range(len(derivatives) - 2, -1 , -1) : 
            if d.denominator == derivatives[i].numerator and d.denominator_type == 1 : # 계산 그래프 상에서 이어져있다면
                # 계수 값을 합침(합성함수 미분법)
                derivatives[i].val *= d.val
                derivatives[i].numerator = d.numerator
                isTheEnd = 0
        
        derivatives.pop()
        if isTheEnd :
            derivative_paths.append(d)
        
    # 분모가 같은 것끼리 수렴한다
    results = []
    for i in range(0, len(argn)) :
        result = 0
        for j in range(0, len(derivative_paths)) :
            if derivative_paths[j].denominator == i :
                result += derivative_paths[j].val

        results.append(result)

    return results
    
# 수식을 입력 ex) x^2 + x + y
print("f = ", end='')
formula = input()
argn = []

# 안에 포함된 변수들 구하기(x, y 등) => argn에 저장
for i in formula :
    # 소문자인 경우를 찾음
    if 0x61 <= ord(i) and ord(i) <= 0x7a :

        # 변수가 이미 추가됬는지 확인
        found = 0
        for j in argn :
            if j == i :
                found = 1
                break
        
        # 추가되지 않았으면
        if found == 0 :
            argn.append(i) # 추가

# 구한 변수에 상수값 입력하기
argv = []
for i in argn :
    print(i + " = ", end='')
    v = input()
    argv.append(v)

print("")
results = operate(formula, argn, argv)

for i in range(0, len(argn)) :
    print("df/d" + argn[i] + " = ", results[i])