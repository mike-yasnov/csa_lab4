// Double-precision arithmetic: 64-bit numbers on 32-bit machine
// Represent 64-bit number as pair of 32-bit (high, low)

function main() {
    print("Demo: 64-bit arithmetic");
    
    // Number 1: 0x00000001_FFFFFFFF (8589934591)
    var a_high = 1;
    var a_low = 1000000;  // Large but valid number
    
    // Number 2: 0x00000002_00000001 (8589934593)  
    var b_high = 2;
    var b_low = 1;
    
    print("Number A: high=");
    print_number(a_high);
    print(" low=");
    print_number(a_low);
    
    print("Number B: high=");
    print_number(b_high);
    print(" low=");
    print_number(b_low);
    
    // Addition of 64-bit numbers
    var result_low = a_low + b_low;
    var carry = 0;
    
    // Check low-part overflow
    if (result_low < a_low) {
        carry = 1;
    }
    
    var result_high = a_high + b_high + carry;
    
    print("A + B: high=");
    print_number(result_high);
    print(" low=");
    print_number(result_low);
    
    // Multiply by constant
    var mult_low = a_low * 3;
    var mult_high = a_high * 3;
    
    print("A * 3: high=");
    print_number(mult_high);
    print(" low=");
    print_number(mult_low);
    
    print("64-bit arithmetic done!");
}

main(); 