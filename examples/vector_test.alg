// Тест векторных операций

function main() {
    print("Тестируем векторные операции...");
    
    // Создаем векторы для тестирования
    var vec1 = <| 1, 2, 3, 4 |>;
    var vec2 = <| 5, 6, 7, 8 |>;
    
    print("Вектор 1: ");
    print_vector(vec1);
    
    print("Вектор 2: ");
    print_vector(vec2);
    
    // Тест базовых векторных операций
    test_vector_operations(vec1, vec2);
    
    print("Векторные тесты завершены!");
}

function test_vector_operations(a, b) {
    // Тест скалярного произведения
    var dot_result = vector_dot(a, b);  // 1*5 + 2*6 + 3*7 + 4*8 = 70
    print("Скалярное произведение: ");
    print_number(dot_result);
    
    // Тест суммы элементов
    var sum_a = vector_sum(a);         // 1 + 2 + 3 + 4 = 10
    print("Сумма элементов вектора 1: ");
    print_number(sum_a);
    
    // Тест максимального элемента
    var max_a = vector_max(a);         // max(1, 2, 3, 4) = 4
    print("Максимальный элемент: ");
    print_number(max_a);
}

function vector_dot(a, b) {
    // Скалярное произведение векторов
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3];
}

function vector_sum(vec) {
    // Сумма всех элементов вектора
    var sum = 0;
    for (var i = 0; i < len(vec); i = i + 1) {
        sum = sum + vec[i];
    }
    return sum;
}

function vector_max(vec) {
    // Максимальный элемент вектора
    var max_val = vec[0];
    for (var i = 1; i < len(vec); i = i + 1) {
        if (vec[i] > max_val) {
            max_val = vec[i];
        }
    }
    return max_val;
}

function print_vector(vec) {
    print("<| ");
    var size = len(vec);
    for (var i = 0; i < size; i = i + 1) {
        print_number(vec[i]);
        if (i < size - 1) {
            print(", ");
        }
    }
    print(" |>");
}

function print_number(n) {
    // Простой вывод числа
    out(n);
}

main(); 