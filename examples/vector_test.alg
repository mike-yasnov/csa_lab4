// Vector test using V_* instructions via builtins

function main() {
    print("Vector test V_*");

    // Vectors as static data
    var v1 = <| 1, 2, 3, 4 |>;
    var v2 = <| 5, 6, 7, 8 |>;

    // Load into vector registers 0 and 1, length 4
    v_load(v1, 4, 0);
    v_load(v2, 4, 1);

    // Addition: r2 = r0 + r1
    v_add(0, 1, 2);

    // Dot product r0 and r1
    print("dot(v1,v2)=");
    print_number(v_dot(0, 1));

    print("; sum r2[0]+...+r2[3]=");
    // Sum elements via vector unit
    print_number(v_sum(2));
}

main();