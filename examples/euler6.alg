// Эйлер задача 6: разность квадрата суммы и суммы квадратов первых 100 натуральных чисел
// Квадрат суммы: (1 + 2 + ... + 100)^2
// Сумма квадратов: 1^2 + 2^2 + ... + 100^2

function main() {
    var n = 100;
    var sum = 0;
    var sum_squares = 0;
    
    // Вычисляем сумму и сумму квадратов
    for (var i = 1; i <= n; i = i + 1) {
        sum = sum + i;
        sum_squares = sum_squares + i * i;
    }
    
    // Квадрат суммы
    var square_of_sum = sum * sum;
    
    // Разность
    var difference = square_of_sum - sum_squares;
    
    print("Квадрат суммы: ");
    print(square_of_sum);
    print("\nСумма квадратов: ");
    print(sum_squares);
    print("\nРазность: ");
    print(difference);
}

main(); 