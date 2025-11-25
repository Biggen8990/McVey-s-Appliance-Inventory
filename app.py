"""
Appliance Inventory Management App

Console-based tool for tracking, editing, archiving, and reporting on appliance inventory across multiple stores.
Features include: duplicate prevention, advanced search/filter, status history, archiving/unarchiving, audit logging, CSV/JSON import/export, and backup/restore.

License: CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)
You may use, share, and reference this code for non-commercial purposes with attribution.
Commercial use of this software, in whole or in part, is prohibited without the express permission of the author.

Author: Justin McVey
Created: 2025
"""

import json
import csv
from datetime import datetime

appliances = []
audit_log = []
last_deleted = None

STATUS_OPTIONS = ["In", "Checked", "Parts Ordered", "Repaired", "Loaded" ]
def choose_status():
    print("\nSelect a status:")
    for idx, status in enumerate(STATUS_OPTIONS, 1):
        print(f"{idx}. {status}")
    while True:
        choice = input("Enter the status number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(STATUS_OPTIONS):
            return STATUS_OPTIONS[int(choice) - 1]
        print("Invalid choice, try again.")

def log_action(action, details):
    """Add an action to the audit log with timestamp."""
    audit_log.append({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'action': action,
        'details': details
    })

def get_required_input(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field is required. Please enter a value.")

def import_from_csv(filename="appliance_inventory.csv"):
    """Import appliances from a CSV file and add them to the inventory."""
    try:
        with open(filename, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                # Check for required keys and prevent duplicates
                if 'store_name' in row and 'item_number' in row:
                    if not any(
                        app['store_name'].lower() == row['store_name'].lower() and app['item_number'] == row['item_number']
                        for app in appliances
                    ):
                        # Optionally, add default status/history if missing
                        appliances.append({
                            'store_name': row['store_name'],
                            'item_number': row['item_number'],
                            'brand': row.get('brand', ''),
                            'model': row.get('model', ''),
                            'serial': row.get('serial', ''),
                            'status': row.get('status', ''),
                            'history': []
                        })
                        count += 1
            print(f"Imported {count} new appliances from '{filename}'.\n")
    except FileNotFoundError:
        print(f"File '{filename}' not found.\n")

def add_appliance():
    """Add a new appliance with basic info, preventing duplicates within the same store."""
    store_name = get_required_input("Store name: ")
    item_number = get_required_input("Store Item Number: ")
    #duplicate check
    for app in appliances:
        if app['store_name'].lower() == store_name.lower() and app['item_number'] == item_number:    #11-11-2025
            print("Error: An appliance with this store and item number already exists!\n")
            return
    brand = get_required_input("Brand: ")
    model = get_required_input("Model: ")
    serial = get_required_input("Serial: ")
    status = choose_status()
    notes = input("Notes/Comments (optional): ")
    log_action('add', f"{item_number} at {store_name}")
    appliances.append({
        'store_name': store_name,
        'item_number': item_number,
        'brand': brand,
        'model': model,
        'serial': serial,
        'status': status,
        'history': [(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status)],
        'notes' : notes,
        'archived': False
    })
    print("Appliance added!\n")

def list_appliances():
    """List all appliances."""
    if not appliances:
        print("No appliances in inventory.\n")
        return
    for idx, app in enumerate([a for a in appliances if not a.get('archived', False)], 1):
        print(f"{idx}. {app['store_name']} | {app['item_number']} | {app['brand']} | {app['model']} | {app['serial']} | {app['status']}")#J
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
    """Edit an appliance by store name and item number."""
    item_number = input("Enter Store Item Number to edit: ")
    store_name = input("Enter Store Name: ").strip().lower()
    for app in appliances:
        if app['item_number'] == item_number and app['store_name'].lower() == store_name:
            print(f"Current info: {app}")
            print("Leave blank to keep current value.")
            app['store_name'] = input(f"Store Name [{app['store_name']}]: ") or app['store_name']
            app['brand'] = input(f"Brand [{app['brand']}]: ") or app['brand']
            app['model'] = input(f"Model [{app['model']}]: ") or app['model']
            app['serial'] = input(f"Serial [{app['serial']}]: ") or app['serial']
            app['item_number'] = input(f"Item number [{app['item_number']}]: ") or app['item_number']
            app['notes'] = input(f"Notes/Comments [{app.get('notes', '')}]: ") or app.get('notes', '')
            print("Current Status:", app['status'])
            if input("Change status? (y/n): ").strip().lower() == 'y':
                new_status = choose_status()
                app['status'] = new_status
                if 'history' not in app:
                    app['history'] = []
                app['history'].append((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), new_status))
            print("Appliance updated!\n")
            log_action('edit', f"{item_number} at {app['store_name']}")
            return
    print("Appliance not found.\n")

def advanced_search():
    """Filter appliances by store, status, or brand (non-archived only)."""
    print("\nAdvanced Filter Options:")
    print("1. Filter by Store")
    print("2. Filter by Status")
    print("3. Filter by Brand")
    print("4. Back to Menu")
    choice = input("Select an option: ")
    if choice == '1':
        store = input("Enter the store name: ").strip().lower()
        results = [app for app in appliances if app['store_name'].lower() == store and not app.get('archived', False)]
    elif choice == '2':
        print("\nStatus Options:")
        for idx, status in enumerate(STATUS_OPTIONS, 1):
            print(f"{idx}. {status}")
        status_choice = input("Enter the status number: ")
        if status_choice.isdigit() and 1 <= int(status_choice) <= len(STATUS_OPTIONS):
            status = STATUS_OPTIONS[int(status_choice) - 1]
            results = [app for app in appliances if app['status'] == status and not app.get('archived', False)]
        else:
            print("Invalid choice.\n")
            return
    elif choice == '3':
        brand = input("Enter the brand: ").strip().lower()
        results = [app for app in appliances if app['brand'].lower() == brand and not app.get('archived', False)]
    else:
        return

    if not results:
        print("No matches found.\n")
        return
    for app in results:
        print(f"{app['store_name']} | {app['item_number']} | {app['brand']} | {app['model']} | {app['serial']} | {app['status']} | {app.get('notes', '')}")
    print()
   

def archive_appliance():
    """Archive an appliance by store name and item number."""
    item_number = input("Enter Store Item Number to archive: ")
    store_name = input("Enter Store Name: ").strip().lower()
    for app in appliances:
        if app['item_number'] == item_number and app['store_name'].lower() == store_name:
            app['archived'] = True
            log_action('archive', f"{item_number} at {app['store_name']}")
            print("Appliance archived! (It is now hidden from regular lists and reports)\n")
            return
    print("Appliance not found.\n")

def view_archived():
    """Show all archived appliances."""
    print("\nArchived Appliances:")
    archived = [a for a in appliances if a.get('archived', False)]
    if not archived:
        print("No archived appliances.\n")
        return
    for app in archived:
        print(f"{app['store_name']} | {app['item_number']} | {app['status']} | {app.get('notes', '')}")
    print()

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

def view_appliance_details():
    """Show all details and history for one appliance."""
    item_number = input("Enter Store Item Number to view: ")
    store_name = input("Enter Store name: ")
    for app in appliances:
        if app['item_number'] == item_number and app['store_name'].lower() == store_name.lower():
            print("\nDetailed Appliance Info:")
            print(f"Store: {app['store_name']}")
            print(f"Item Number: {app['item_number']}")
            print(f"Brand: {app['brand']}")
            print(f"Model: {app['model']}")
            print(f"Serial: {app['serial']}")
            print(f"Status: {app['status']}")
            print(f"Notes: {app.get('notes', '')}")
            # Show status history if available
            if 'history' in app:
                print("Status History:")
                for entry in app['history']:
                    if isinstance(entry, (tuple, list)) and len(entry) == 2:
                        timestamp, stat = entry
                        print((f" {timestamp}; {stat}"))
                    else:
                        print(f" {entry}")
            print()
            return
    print("Appliance not found.\n")

def export_to_csv(filename="appliance_inventory.csv"):
    """Export all appliances to a CSV file."""
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ['store_name', 'item_number', 'brand', 'model', 'serial', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for app in appliances:
            writer.writerow({
                'store_name': app['store_name'],
                'item_number': app['item_number'],
                'brand': app['brand'],
                'model': app['model'],
                'serial': app['serial'],
                'status': app['status']
            })
    print(f"Inventory exported to '{filename}'\n")

def export_audit_log(filename="audit_log.csv"):
    """Export the audit log to a CSV file."""
    if not audit_log:
        print("No audit log entries to export.\n")
        return
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ['timestamp', 'action', 'details']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in audit_log:
            writer.writerow(entry)
    print(f"Audit log exported to '{filename}'\n")

def backup_inventory():
    """Save appliances to a user-specified JSON backup file."""
    filename = input("Enter filename for backup (e.g., backup.json): ").strip()
    if not filename:
        print("Backup canceled.\n")
        return
    with open(filename, "w") as f:
        json.dump(appliances, f, indent=4)
    print(f"Backup saved as '{filename}'\n")

def restore_inventory():
    """Load appliances from a user-specified JSON backup file."""
    filename = input("Enter filename to restore from: ").strip()
    if not filename:
        print("Restore canceled.\n")
        return
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            appliances.clear()
            appliances.extend(data)
        print(f"Inventory restored from '{filename}'\n")
    except FileNotFoundError:
        print(f"File '{filename}' not found.\n")
        log_action('undo delete', f"{last_deleted['item_number']} at {last_deleted['store_name']}")

def view_audit_log():
    """Display the audit log (action history)."""
    if not audit_log:
        print("No actions logged yet.\n")
        return

    # Show the last log entry first, if you want:
    last_entry = audit_log[-1]
    print(f"Last log: {last_entry['timestamp']} - {last_entry['action']} - {last_entry['details']}\n")

    # Now print the full audit log:
    print("Full audit log/history:")
    for entry in audit_log:
        print(f"{entry['timestamp']}: {entry['action']} — {entry['details']}")
    print()

def bulk_archive():
    """Archive all appliances in a store with a specific status."""
    store_name = input("Enter Store Name: ").strip().lower()
    print("\nStatus Options:")
    for idx, status in enumerate(STATUS_OPTIONS, 1):
        print(f"{idx}. {status}")
    status_choice = input("Enter the status number to bulk archive: ")
    if not (status_choice.isdigit() and 1 <= int(status_choice) <= len(STATUS_OPTIONS)):
        print("Invalid choice.\n")
        return
    status = STATUS_OPTIONS[int(status_choice) - 1]
    count = 0
    for app in appliances:
        if (
            app['store_name'].lower() == store_name
            and app['status'] == status
            and not app.get('archived', False)
        ):
            app['archived'] = True
            count += 1
            log_action('archive', f"{app['item_number']} at {app['store_name']}")
    print(f"{count} appliances archived.\n")

def bulk_unarchive():
    """Restore all archived appliances in a store with a specific status."""
    store_name = input("Enter Store Name: ").strip().lower()
    print("\nStatus Options:")
    for idx, status in enumerate(STATUS_OPTIONS, 1):
        print(f"{idx}. {status}")
    status_choice = input("Enter the status number to restore: ")
    if not (status_choice.isdigit() and 1 <= int(status_choice) <= len(STATUS_OPTIONS)):
        print("Invalid choice.\n")
        return
    status = STATUS_OPTIONS[int(status_choice) - 1]
    count = 0
    for app in appliances:
        if (
            app['store_name'].lower() == store_name
            and app['status'] == status
            and app.get('archived', False)
        ):
            app['archived'] = False
            count += 1
            log_action('unarchive', f"{app['item_number']} at {app['store_name']}")
    print(f"{count} appliances restored from archive.\n")

def file_options_menu():
    while True:
        print("\nFile Options:")
        print("1. Save")
        print("2. Load")
        print("3. Export to CSV")
        print("4. Import from CSV")
        print("5. Backup Inventory")
        print("6. Restore Inventory")
        print("7. Export Audit Log to CSV")
        print("8. Archive Appliance")
        print("9. View Archived Appliances")
        print("10. Bulk Archive By Store/Status")
        print("11. Bulk Unarchive By Store/status")
        print("12. Back to Main Menu")
        choice = input("Select an option: ")
        if choice == '1':
            save_to_file()
        elif choice == '2':
            load_from_file()
        elif choice == '3':
            export_to_csv()
        elif choice == '4':
            import_from_csv()
        elif choice == '5':
            backup_inventory()
        elif choice == '6':
            restore_inventory()
        elif choice == '7':
            export_audit_log()
        elif choice == '8':
            archive_appliance()
        elif choice == '9':
            view_archived()
        elif choice == '10':
            bulk_archive()
        elif choice == '11':
            bulk_unarchive()
        elif choice == '12':
            break
        else:
            print("Invalid choice.\n")

def report_by_store():
    """Show all active (non-archived) appliances for a selected store, grouped by status with notes."""
    store = input("Enter store name to report: ").strip().lower()
    # Filter to non-archived appliances for the given store
    results = [app for app in appliances if app['store_name'].lower() == store and not app.get('archived', False)]
    if not results:
        print("No active appliances found for that store.\n")
        return
    # Group by status
    grouped = {}
    for app in results:
        stat = app['status']
        grouped.setdefault(stat, []).append(app)
    print(f"\nInventory for '{store.title()}':")
    for status in grouped:
        print(f"\nStatus: {status}")
        for app in grouped[status]:
            print(f"  Item: {app['item_number']} | Notes: {app.get('notes', '')}")
    print()

def unarchive_appliance():
    """Restore (unarchive) an appliance by store name and item number."""
    item_number = input("Enter Store Item Number to restore: ")
    store_name = input("Enter Store Name: ").strip().lower()
    for app in appliances:
        if (app['item_number'] == item_number 
            and app['store_name'].lower() == store_name 
            and app.get('archived', False)):
            app['archived'] = False
            log_action('unarchive', f"{item_number} at {app['store_name']}")
            print("Appliance has been restored from archive!\n")
            return
    print("Archived appliance not found.\n")

def menu():
    while True:
        print("1. Add Appliance")
        print("2. List Appliances")
        print("3. Edit Appliance")
        print("4. Search for Appliance")
        print("5. Inventory Summary")
        print("6. View Appliance Details")
        print("7. File Options")
        print("8. Store-Based Report")
        print("9. View Audit Log")
        print("10. Quit")
        choice = input("Select an option: ")
        if choice == '1':
            add_appliance()
        elif choice == '2':
            list_appliances()
        elif choice == '3':
            edit_appliance()
        elif choice == '4':
            advanced_search()
        elif choice == '5':
            quick_summary()
        elif choice == '6':
            view_appliance_details()
        elif choice == '7':
            file_options_menu()
        elif choice == '8':
            report_by_store()
        elif choice == '9':
            view_audit_log()
        elif choice == '10':
            print("Don't forget to save your work using File Options before quitting!")
            print("Goodbye!")
            break
        else:
            print("Invalid choice.\n")

if __name__ == "__main__":
    menu()
     