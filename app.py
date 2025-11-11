import json

appliances = []

def add_appliance():
    """Add a new appliance with basic info."""
    store_name = input("Store name: ")
    item_number = input("Store Item Number: ")
    brand = input("Brand: ")
    model = input("Model: ")
    serial = input("Serial: ")
    status = input("Status: ")
    appliances.append({
        'store_name': store_name,
        'item_number': item_number,
        'brand': brand,
        'model': model,
        'serial': serial,
        'status': status
    })
    print("Appliance added!\n")

def list_appliances():
    """List all appliances."""
    if not appliances:
        print("No appliances in inventory.\n")
        return
    for idx, app in enumerate(appliances, 1):
        print(f"{idx}. {app['store_name']} | {app['item_number']} | {app['brand']} | {app['model']} | {app['serial']} | {app['status']}")
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

def edit_appliance():
    """Edit the store name, brand, model, serial, item number, or status of an appliance."""
    item_number = input("Enter Store Item Number to edit: ")
    for app in appliances:
        if app['item_number'] == item_number:
            print(f"Current info: {app}")
            print("Leave blank to keep current value.")
            app['store_name'] = input(f"Store Name [{app['store_name']}]: ") or app ['store_name']
            app['brand'] = input(f"Brand [{app['brand']}]: ") or app['brand']
            app['model'] = input(f"Model [{app['model']}]: ") or app['model']
            app['serial'] = input(f"Serial [{app['serial']}]: ") or app['serial']
            app['item_number'] = input(f"Item number [{app['item_number']}]: ") or app['item_number']
            app['status'] = input(f"Status [{app['status']}]: ") or app['status']
            print("Appliance updated!\n")
            return
    print("Appliance not found.\n")

def search_appliance():
    """Search appliances by brand or store name."""
    term = input("Search by brand or store name: ").lower()
    results = [app for app in appliances
               if term in app['brand'].lower() or term in app['store_name'].lower()]
    if not results:
        print("No matches found.\n")
        return
    for app in results:
        print(f"{app['store_name']} | {app['item_number']} | {app['brand']} | {app['model']} | {app['serial']} | {app['status']}")
    print()

def remove_appliance():
    """Delete an appliance by item number."""
    item_number = input("Enter Store Item Number to remove: ")
    for i, app in enumerate(appliances):
        if app['item_number'] == item_number:
            del appliances[i]
            print("Appliance removed!\n")
            return
    print("Appliance not found.\n")

def quick_summary():
    """Print a summary of inventory by status."""
    summary = {}
    for app in appliances:
        status = app['status'].lower()
        summary[status] = summary.get(status, 0) + 1
    print("\nInventory Summary:")
    for status, count in summary.items():
        print(f"  {status.title()}: {count}")
    print()

def menu():
    while True:
        print("1. Add Appliance")
        print("2. List Appliances")
        print("3. Edit Appliance")
        print("4. Search for Appliance")
        print("5. Save")
        print("6. Load")
        print("7. Delete Appliance")
        print("8. Inventory Summary")
        print("9. Quit")
        choice = input("Select an option: ")
        if choice == '1':
            add_appliance()
        elif choice == '2':
            list_appliances()
        elif choice == '3':
            edit_appliance()
        elif choice == '4':
            search_appliance()
        elif choice == '5':
            save_to_file()
        elif choice == '6':
            load_from_file()
        elif choice == '7':
            remove_appliance()
        elif choice == '8':
            quick_summary()
        elif choice == '9':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.\n")

if __name__ == "__main__":
    menu()
     