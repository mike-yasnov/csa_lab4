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
    // Сумма всех элементов вектора (упрощенная версия для 4 элементов)
    return vec[0] + vec[1] + vec[2] + vec[3];
}

function vector_max(vec) {
    // Максимальный элемент вектора (упрощенная версия для 4 элементов)
    var max_val = vec[0];
    if (vec[1] > max_val) max_val = vec[1];
    if (vec[2] > max_val) max_val = vec[2];
    if (vec[3] > max_val) max_val = vec[3];
    return max_val;
}

function print_vector(vec) {
    print("<| ");
    print_number(vec[0]);
    print(", ");
    print_number(vec[1]);
    print(", ");
    print_number(vec[2]);
    print(", ");
    print_number(vec[3]);
    print(" |>");
}

function print_number(n) {
    // Простой вывод числа
    out(n);
}

main(); 