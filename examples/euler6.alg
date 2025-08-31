// Эйлер задача 6: разность квадрата суммы и суммы квадратов первых 100 натуральных чисел
// Квадрат суммы: (1 + 2 + ... + 100)^2
// Сумма квадратов: 1^2 + 2^2 + ... + 100^2

function main() {
    print("Euler Problem 6:");
    print("Difference: square of sum vs sum of squares for first 100 numbers");
    
    var n = 100;
    
    // Sum of first n natural numbers: sum = n*(n+1)/2
    var sum = n * (n + 1) / 2;
    print("Sum of first 100 numbers: ");
    print_number(sum);
    
    // Square of the sum
    var sum_squared = sum * sum;
    print("Square of sum: ");
    print_number(sum_squared);
    
    // Sum of squares of first n numbers: sum_of_squares = n*(n+1)*(2*n+1)/6
    var sum_of_squares = n * (n + 1) * (2 * n + 1) / 6;
    print("Sum of squares: ");
    print_number(sum_of_squares);
    
    // Difference
    var difference = sum_squared - sum_of_squares;
    print("Difference: ");
    print_number(difference);
    
    print("Done!");
}

main(); 