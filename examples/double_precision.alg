// Арифметика двойной точности: работа с 64-битными числами на 32-битной машине
// Представляем 64-битное число как пару 32-битных (high, low)

function main() {
    print("Демонстрация 64-битной арифметики:");
    
    // Число 1: 0x00000001_FFFFFFFF (8589934591)
    var a_high = 1;
    var a_low = 1000000;  // Большое но допустимое число
    
    // Число 2: 0x00000002_00000001 (8589934593)  
    var b_high = 2;
    var b_low = 1;
    
    print("Число A: high=");
    print(a_high);
    print(" low=");
    print(a_low);
    
    print("Число B: high=");
    print(b_high);
    print(" low=");
    print(b_low);
    
    // Сложение 64-битных чисел
    var result_low = a_low + b_low;
    var carry = 0;
    
    // Проверяем переполнение младших разрядов
    if (result_low < a_low) {
        carry = 1;
    }
    
    var result_high = a_high + b_high + carry;
    
    print("A + B: high=");
    print(result_high);
    print(" low=");
    print(result_low);
    
    // Умножение на константу
    var mult_low = a_low * 3;
    var mult_high = a_high * 3;
    
    print("A * 3: high=");
    print(mult_high);
    print(" low=");
    print(mult_low);
    
    print("64-битная арифметика завершена!");
}

main(); 