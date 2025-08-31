// Эйлер задача 6: разность квадрата суммы и суммы квадратов первых 100 натуральных чисел
// Квадрат суммы: (1 + 2 + ... + 100)^2
// Сумма квадратов: 1^2 + 2^2 + ... + 100^2

function main() {
    print("Euler задача 6:");
    print("Разность квадрата суммы и суммы квадратов первых 100 чисел");
    
    var n = 100;
    
    // Вычисляем сумму первых n натуральных чисел: sum = n*(n+1)/2
    var sum = n * (n + 1) / 2;
    print("Сумма первых 100 чисел: ");
    print_number(sum);
    
    // Квадрат суммы
    var sum_squared = sum * sum;
    print("Квадрат суммы: ");
    print_number(sum_squared);
    
    // Сумма квадратов первых n чисел: sum_of_squares = n*(n+1)*(2*n+1)/6
    var sum_of_squares = n * (n + 1) * (2 * n + 1) / 6;
    print("Сумма квадратов: ");
    print_number(sum_of_squares);
    
    // Разность
    var difference = sum_squared - sum_of_squares;
    print("Разность: ");
    print_number(difference);
    
    print("Решение найдено!");
}

main(); 