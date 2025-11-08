import json

appliances = []

def add_appliance():
    """Add a new appliance with basic info."""
    store_name = input("Store name: ")
    item_number = input("Store Item Number: ")
    brand = input("Brand: ")
    model = input("Model: ")
    status = input("Status: ")
    appliances.append({
        'store_name': store_name,
        'item_number': item_number,
        'brand': brand,
        'model': model,
        'status': status
    })
    print("Appliance added!\n")

def list_appliances():
    """List all appliances."""
    if not appliances:
        print("No appliances in inventory.\n")
        return
    for idx, app in enumerate(appliances, 1):
        print(f"{idx}. {app['store_name']} | {app['item_number']} | {app['brand']} | {app['model']} | {app['status']}")
    print()

def save_to_file(filename="appliance_inventory.json"):
    """Save appliances to JSON."""
    with open(filename, "w") as f:
        json.dump(appliances, f, indent=4)
    print("Data saved!\n")

def load_from_file(filename="appliance_inventory.json"):
    """Load appliances from JSON file."""
    appliances.clear()
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            appliances.extend(data)
        print("Data loaded.\n")
    except FileNotFoundError:
        print("No saved file found. Starting empty.\n")

def menu():
    while True:
        print("1. Add Appliance")
        print("2. List Appliances")
        print("3. Save")
        print("4. Load")
        print("5. Quit")
        choice = input("Select an option: ")
        if choice == '1':
            add_appliance()
        elif choice == '2':
            list_appliances()
        elif choice == '3':
            save_to_file()
        elif choice == '4':
            load_from_file()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.\n")

if __name__ == "__main__":
    menu()