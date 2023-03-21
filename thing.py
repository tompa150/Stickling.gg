def main():
    bus = [
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
    ]
    user_choice = False
    while user_choice != "0":
        print_menu
        user_choice = input("Ange ett val: ")
        if user_choice == "1":
            print_bus(bus)
        elif user_choice == "2":
            pass
        elif user_choice == "3":
            pass
        elif user_choice == "4":
            pass
        elif user_choice == "0":
            pass
        else:
            print("Du valde inte ett giltigt alternativ. Försök igen")

def print_bus(bus):
    for i, row in enumerate(bus, start=1):
        print(f"{i:<2}"+": ", end = "")
        for seat in row:
            print(f"{'-':^3}", end = "")
        print("")

def print_menu():
    print("n\"")
    print("Detta är menyn:")
    print("1. Visa bussen")
    print("2. Boka en plats")
    print("3. Avboka en plats")
    print("4. Se vem som bokat plats")
    print("0. Avsluta")


main()