from connect import connect


# 1. создать таблицу
def create_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50),
            phone VARCHAR(20)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Table created")


# 2. добавить контакт
def add_contact():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO phonebook (name, phone)
        VALUES (%s, %s);
    """, (name, phone))

    conn.commit()
    cur.close()
    conn.close()
    print("Contact added")


# 3. показать все контакты
def show_contacts():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM phonebook;")
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


# 4. обновить контакт
def update_contact():
    old_name = input("Enter name to update: ")
    new_phone = input("Enter new phone: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        UPDATE phonebook
        SET phone = %s
        WHERE name = %s;
    """, (new_phone, old_name))

    conn.commit()
    cur.close()
    conn.close()
    print("Updated")


# 5. удалить контакт
def delete_contact():
    name = input("Enter name to delete: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM phonebook
        WHERE name = %s;
    """ , (name,))

    conn.commit()
    cur.close()
    conn.close()
    print("Deleted")


# меню
def menu():
    while True:
        print("\n1 - Create table")
        print("2 - Add contact")
        print("3 - Show contacts")
        print("4 - Update contact")
        print("5 - Delete contact")
        print("0 - Exit")

        choice = input("Choose: ")

        if choice == "1":
            create_table()
        elif choice == "2":
            add_contact()
        elif choice == "3":
            show_contacts()
        elif choice == "4":
            update_contact()
        elif choice == "5":
            delete_contact()
        elif choice == "0":
            break
        else:
            print("Wrong choice")


if __name__ == "__main__":
    menu()