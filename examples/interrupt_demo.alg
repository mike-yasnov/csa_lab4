// Interrupt (trap) demo

var counter = 0;

function timer_handler() {
    counter = counter + 1;
    print("INTERRUPT ");
}

function main() {
    print("Interrupt demo start\n");
    // IRQ0 -> timer_handler
    set_interrupt_handler(0, timer_handler);
    enable_interrupts();

    // Busy loop
    var i = 0;
    while (i < 5) {
        i = i + 1;
    }

    print("Interrupts processed: ");
    print_number(counter);
}

main();

