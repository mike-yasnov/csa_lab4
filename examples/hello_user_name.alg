// Программа hello_user_name - запрашивает имя пользователя и приветствует

function main() {
    print("What is your name?");
    
    // Упрощённая версия - читаем один символ как имя
    var ch = read();
    
    print("Hello, ");
    print(ch);  // Печатаем код символа
    print("!");
}

main(); 