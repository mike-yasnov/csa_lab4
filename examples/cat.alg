// Программа cat - печатает данные, поданные через ввод

function main() {
    var ch = 1;  // Инициализируем не нулём
    while (ch != 0) {
        ch = read();
        if (ch != 0) {
            print(ch);
        }
    }
}

main(); 