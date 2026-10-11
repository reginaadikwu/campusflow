from pathlib import Path

from campusflow.reports import generate_report
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_ticket,
    change_status,
    get_work_queue,
    reopen_ticket,
)


DATA_FILE = Path(__file__).resolve().parent / "data" / "tickets.json"


def display_ticket(ticket):
    for field, value in ticket.items():
        print(f"{field}: {value}")
    print("-" * 30)


def display_tickets(tickets):
    if not tickets:
        print("No tickets found.")
        return

    for ticket in tickets:
        display_ticket(ticket)


def create_from_input(tickets):
    title = input("Title: ")
    category = input("Category (Network/Hardware/Software/Other): ")
    urgency = input("Urgency (low/medium/high): ")
    affected_users = int(input("Number of affected users: "))

    ticket = create_ticket(
        tickets, title, category, urgency, affected_users
    )
    save_tickets(tickets, DATA_FILE)
    print(f"Created ticket {ticket['id']}.")


def show_report(tickets):
    report = generate_report(tickets)

    print(f"\nTotal tickets: {report['total']}")

    print("\nBy status:")
    for status, count in report["by_status"].items():
        print(f"  {status}: {count}")

    print("\nBy priority:")
    for priority, count in report["by_priority"].items():
        print(f"  {priority}: {count}")


def print_menu():
    print("""
=== CampusFlow Helpdesk ===
1. Create ticket
2. List all tickets
3. View ticket
4. Assign ticket
5. Change ticket status
6. Reopen resolved ticket
7. Show unresolved work queue
8. Show report
0. Exit
""")


def main():
    try:
        tickets = load_tickets(DATA_FILE)
    except (ValueError, OSError) as exc:
        print(f"Could not load saved tickets: {exc}")
        return

    actions = {
        "1": lambda: create_from_input(tickets),
        "2": lambda: display_tickets(tickets),
        "7": lambda: display_tickets(get_work_queue(tickets)),
        "8": lambda: show_report(tickets),
    }

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        try:
            if choice == "0":
                print("Goodbye!")
                break

            if choice in actions:
                actions[choice]()
                continue

            if choice == "3":
                ticket_id = input("Ticket ID: ").strip()
                ticket = next(
                    (t for t in tickets if t["id"] == ticket_id), None
                )
                if ticket is None:
                    raise KeyError(f"Ticket {ticket_id!r} was not found.")
                display_ticket(ticket)

            elif choice == "4":
                ticket_id = input("Ticket ID: ").strip()
                staff_name = input("Staff name: ")
                assign_ticket(tickets, ticket_id, staff_name)
                save_tickets(tickets, DATA_FILE)
                print("Ticket assigned.")

            elif choice == "5":
                ticket_id = input("Ticket ID: ").strip()
                new_status = input(
                    "New status (in_progress/resolved): "
                )
                change_status(tickets, ticket_id, new_status)
                save_tickets(tickets, DATA_FILE)
                print("Ticket status updated.")

            elif choice == "6":
                ticket_id = input("Ticket ID: ").strip()
                reopen_ticket(tickets, ticket_id)
                save_tickets(tickets, DATA_FILE)
                print("Ticket reopened.")

            else:
                print("Invalid menu option. Please choose again.")

        except (ValueError, KeyError, OSError) as exc:
            print(f"Error: {exc}")

        except (EOFError, KeyboardInterrupt):
            print("\nExiting CampusFlow.")
            break


if __name__ == "__main__":
    main()
