// Тест векторных операций

function main() {
    // Создаем векторы
    var vec1 = <| 1, 2, 3, 4 |>;
    var vec2 = <| 5, 6, 7, 8 |>;
    
    print("Вектор 1: ");
    print_vector(vec1);
    
    print("\nВектор 2: ");
    print_vector(vec2);
    
    // TODO: Добавить векторные операции когда они будут реализованы
    print("\nВекторные операции будут добавлены позже");
}

function print_vector(vec) {
    print("<| ");
    var size = len(vec);
    for (var i = 0; i < size; i = i + 1) {
        print(vec[i]);
        if (i < size - 1) {
            print(", ");
        }
    }
    print(" |>");
}

main(); 