// Демонстрация системы прерываний (упрощённая версия)

var interrupt_count = 0;

function main() {
    print("Демонстрация системы прерываний");
    
    var counter = 0;
    
    // Основной цикл работы
    while (counter < 100) {
        counter = counter + 1;
        
        // Периодически выводим состояние
        if (counter % 20 == 0) {
            print("Main loop: counter=");
            print(counter);
        }
        
        // Имитация полезной работы
        var dummy = counter * 2 + 1;
    }
    
    print("Основной цикл завершён");
}

main(); 