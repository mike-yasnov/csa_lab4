// Program sort - simple sorting of three numbers

function main() {
    print("Sorting three numbers:");
    
    // Simplified version - sort 3 numbers
    var a = 30;
    var b = 10; 
    var c = 20;
    
    print("Before sorting:");
    print_number(a);
    print_number(b);
    print_number(c);
    
    // Simple sort with three comparisons
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
    
    print("After sorting:");
    print_number(a);
    print_number(b);
    print_number(c);
}

main(); 