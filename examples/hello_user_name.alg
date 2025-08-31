// Программа hello_user_name - запрашивает имя пользователя и приветствует

function main() {
    print("What is your name?\n");

    // Буфер 32 байта, инициализирован '_'
    var buf = alloc(32);
    // Читаем строку в буфер как C-string
    readLineBuf(buf, 32);

    // Печатаем приветствие
    print("Hello, ");
    print(buf);
    print("!");
}

main(); 