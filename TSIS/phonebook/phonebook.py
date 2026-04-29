from connect import connect
import csv
import json


def run_sql_file(filename):
    conn = connect()
    cur = conn.cursor()

    file = open(filename, "r")
    sql = file.read()
    file.close()

    cur.execute(sql)
    conn.commit()

    cur.close()
    conn.close()
    print(filename, "done")


def setup_database():
    run_sql_file("schema.sql")
    run_sql_file("procedures.sql")


def get_group_id(group_name):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO groups(name)
        VALUES(%s)
        ON CONFLICT(name) DO NOTHING;
    """, (group_name,))

    cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
    group_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return group_id


def get_contact_id(name):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT id FROM contacts WHERE name = %s;", (name,))
    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return row[0]
    return None


def add_contact():
    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday YYYY-MM-DD: ")
    group_name = input("Group: ")
    phone = input("Phone: ")
    phone_type = input("Type home/work/mobile: ")

    group_id = get_group_id(group_name)

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO contacts(name, email, birthday, group_id)
        VALUES(%s, %s, %s, %s)
        RETURNING id;
    """, (name, email, birthday, group_id))

    contact_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO phones(contact_id, phone, type)
        VALUES(%s, %s, %s);
    """, (contact_id, phone, phone_type))

    conn.commit()
    print("Contact added")

    cur.close()
    conn.close()


def show_contacts():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            c.name,
            c.email,
            c.birthday,
            g.name,
            c.date_added,
            COALESCE(string_agg(p.phone || ' (' || p.type || ')', ', '), '')
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.date_added
        ORDER BY c.id;
    """)

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def update_contact():
    name = input("Name to update: ")
    contact_id = get_contact_id(name)

    if contact_id is None:
        print("Contact not found")
        return

    email = input("New email: ")
    birthday = input("New birthday YYYY-MM-DD: ")
    group_name = input("New group: ")

    group_id = get_group_id(group_name)

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        UPDATE contacts
        SET email = %s, birthday = %s, group_id = %s
        WHERE id = %s;
    """, (email, birthday, group_id, contact_id))

    conn.commit()
    cur.close()
    conn.close()

    print("Updated")


def delete_contact():
    name = input("Name to delete: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("DELETE FROM contacts WHERE name = %s;", (name,))

    conn.commit()
    cur.close()
    conn.close()

    print("Deleted")


def add_phone_console():
    name = input("Contact name: ")
    phone = input("Phone: ")
    phone_type = input("Type home/work/mobile: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("CALL add_phone(%s, %s, %s);", (name, phone, phone_type))
    
    conn.commit()
    print("Phone added")

    cur.close()
    conn.close()


def move_to_group_console():
    name = input("Contact name: ")
    group_name = input("New group: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("CALL move_to_group(%s, %s);", (name, group_name))

    conn.commit()
    cur.close()
    conn.close()

    print("Moved")


def search_contacts_console():
    query = input("Search: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s);", (query,))
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def filter_by_group():
    group_name = input("Group: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name ILIKE %s;
    """, (group_name,))

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def search_by_email():
    email = input("Email part: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, email, birthday
        FROM contacts
        WHERE email ILIKE %s;
    """, ("%" + email + "%",))

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def sort_contacts():
    print("1 - name")
    print("2 - birthday")
    print("3 - date added")

    choice = input("Choose: ")

    if choice == "1":
        order_by = "name"
    elif choice == "2":
        order_by = "birthday"
    elif choice == "3":
        order_by = "date_added"
    else:
        print("Wrong choice")
        return

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, email, birthday, date_added
        FROM contacts
        ORDER BY """ + order_by + ";")

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def pagination_console():
    page = 0
    limit = 3

    while True:
        offset = page * limit

        conn = connect()
        cur = conn.cursor()

        cur.execute("SELECT * FROM get_contacts_page(%s, %s);", (limit, offset))
        rows = cur.fetchall()

        cur.close()
        conn.close()

        print("Page", page + 1)

        for row in rows:
            print(row)

        print("next / prev / quit")
        command = input("Choose: ")

        if command == "next":
            page += 1
        elif command == "prev":
            if page > 0:
                page -= 1
            else:
                print("First page")
        elif command == "quit":
            break
        else:
            print("Wrong command")

def export_to_json():
    filename = input("JSON file name: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.id;
    """)

    contacts = cur.fetchall()
    data = []

    for contact in contacts:
        contact_id = contact[0]

        cur.execute("""
            SELECT phone, type
            FROM phones
            WHERE contact_id = %s;
        """, (contact_id,))

        phones = cur.fetchall()

        item = {
            "name": contact[1],
            "email": contact[2],
            "birthday": str(contact[3]) if contact[3] else "",
            "group": contact[4],
            "phones": []
        }

        for phone in phones:
            item["phones"].append({
                "phone": phone[0],
                "type": phone[1]
            })

        data.append(item)

    cur.close()
    conn.close()

    file = open(filename, "w")
    json.dump(data, file, indent=4)
    file.close()

    print("Exported")


def import_from_json():
    filename = input("JSON file name: ")

    file = open(filename, "r")
    data = json.load(file)
    file.close()

    for item in data:
        name = item["name"]
        email = item["email"]
        birthday = item["birthday"]
        group_name = item["group"]
        phones = item["phones"]

        contact_id = get_contact_id(name)

        if contact_id is not None:
            print("Duplicate:", name)
            action = input("skip or overwrite: ")

            if action == "skip":
                continue

            if action == "overwrite":
                group_id = get_group_id(group_name)

                conn = connect()
                cur = conn.cursor()

                cur.execute("""
                    UPDATE contacts
                    SET email = %s, birthday = %s, group_id = %s
                    WHERE id = %s;
                """, (email, birthday, group_id, contact_id))

                cur.execute("DELETE FROM phones WHERE contact_id = %s;", (contact_id,))

                for ph in phones:
                    cur.execute("""
                        INSERT INTO phones(contact_id, phone, type)
                        VALUES(%s, %s, %s);
                    """, (contact_id, ph["phone"], ph["type"]))

                conn.commit()
                cur.close()
                conn.close()

        else:
            group_id = get_group_id(group_name)

            conn = connect()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES(%s, %s, %s, %s)
                RETURNING id;
            """, (name, email, birthday, group_id))

            new_id = cur.fetchone()[0]

            for ph in phones:
                cur.execute("""
                    INSERT INTO phones(contact_id, phone, type)
                    VALUES(%s, %s, %s);
                """, (new_id, ph["phone"], ph["type"]))

            conn.commit()
            cur.close()
            conn.close()

    print("Imported")


def import_from_csv():
    filename = input("CSV file name: ")

    file = open(filename, "r")
    reader = csv.DictReader(file)

    for row in reader:
        name = row["name"]
        email = row["email"]
        birthday = row["birthday"]
        group_name = row["group"]
        phone = row["phone"]
        phone_type = row["type"]

        contact_id = get_contact_id(name)

        if contact_id is None:
            group_id = get_group_id(group_name)

            conn = connect()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES(%s, %s, %s, %s)
                RETURNING id;
            """, (name, email, birthday, group_id))

            contact_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES(%s, %s, %s);
            """, (contact_id, phone, phone_type))

            conn.commit()
            cur.close()
            conn.close()

        else:
            conn = connect()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES(%s, %s, %s);
            """, (contact_id, phone, phone_type))

            conn.commit()
            cur.close()
            conn.close()

    file.close()
    print("Imported from CSV")


def menu():
    while True:
        print()
        print("1 - setup database")
        print("2 - add contact")
        print("3 - show contacts")
        print("4 - update contact")
        print("5 - delete contact")
        print("6 - add phone")
        print("7 - move to group")
        print("8 - search contacts")
        print("9 - filter by group")
        print("10 - search by email")
        print("11 - sort contacts")
        print("12 - pagination")
        print("13 - export to json")
        print("14 - import from json")
        print("15 - import from csv")
        print("0 - exit")

        choice = input("Choose: ")

        if choice == "1":
            setup_database()
        elif choice == "2":
            add_contact()
        elif choice == "3":
            show_contacts()
        elif choice == "4":
            update_contact()
        elif choice == "5":
            delete_contact()
        elif choice == "6":
            add_phone_console()
        elif choice == "7":
            move_to_group_console()
        elif choice == "8":
            search_contacts_console()
        elif choice == "9":
            filter_by_group()
        elif choice == "10":
            search_by_email()
        elif choice == "11":
            sort_contacts()
        elif choice == "12":
            pagination_console()
        elif choice == "13":
            export_to_json()
        elif choice == "14":
            import_from_json()
        elif choice == "15":
            import_from_csv()
        elif choice == "0":
            break
        else:
            print("Wrong choice")


if __name__ == "__main__":
    menu()