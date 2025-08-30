// Программа sort - сортировка (упрощённая версия)

function main() {
    print("Сортировка трёх чисел:");
    
    // Упрощённая версия - сортируем 3 числа
    var a = 30;
    var b = 10; 
    var c = 20;
    
    print("До сортировки:");
    print(a);
    print(b);
    print(c);
    
    // Простая сортировка тремя сравнениями
    if (a > b) {
        var temp = a;
        a = b;
        b = temp;
    }
    
    if (b > c) {
        var temp = b;
        b = c;
        c = temp;
    }
    
    if (a > b) {
        var temp = a;
        a = b;
        b = temp;
    }
    
    print("После сортировки:");
    print(a);
    print(b);
    print(c);
}

main(); 