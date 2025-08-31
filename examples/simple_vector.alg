// Simple vector demo

function main() {
    print("Simple vector demo");

    let v1 = <| 1, 2, 3, 4 |>;
    let v2 = <| 5, 6, 7, 8 |>;

    // Load into vector registers
    v_load(v1, 4, 0);
    v_load(v2, 4, 1);

    // Dot product
    print("Dot product: ");
    print_number(v_dot(0, 1));
}

main();

