from collections import UserDict
from typing import Callable
from datetime import datetime, timedelta

# Класи
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Номер телефону має містити рівно 10 цифр.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Не вірний формат дати, використовуйте DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
        return False

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return True
        return False

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones)

        if self.birthday is not None:
            bday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}"
        else:
            bday_str = ""

        return f"Contact name: {self.name.value}, phones: {phones_str}{bday_str}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today()
        next_week = today + timedelta(days=7)
        result = []
        for record in self.data.values():
            if record.birthday:
                bday_this_year = record.birthday.value.replace(year=today.year)
                if today <= bday_this_year <= next_week:
                    result.append(f"🎂 Привітати: {record.name.value} ({bday_this_year.strftime('%d.%m')})")
        return result

# Декоратор для обробки помилок
def input_error(func: Callable):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "❌ Помилка: контакт не знайдено."
        except ValueError:
            return "❌ Помилка: введіть ім'я та телефон (10 цифр) через пробіл."
        except IndexError:
            return "❌ Помилка: введіть аргументи для команди."
    return inner


# Додати контакт
@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
    return f"✅ Контакт {name} додано або оновлено."

# Змінити існуючий контакт
@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    if record.edit_phone(old_phone, new_phone):
        return f"🔁 Телефон {old_phone} змінено на {new_phone}."
    return "❌ Телефон не знайдено."

# Показати телефон за ім'ям
@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    phones = ", ".join(p.value for p in record.phones)
    return f"📱 Телефони {name}: {phones}"

@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(bday)
    return f"🎂 День народження для {name} додано."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record or not record.birthday:
        return "❌ День народження не вказано"
    return f"🎂 День народження {name}: {record.birthday.value.strftime('%d.%m.%Y')}"

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "📍 Немає днів народжень на наступному тижні"
    return "\n".join(upcoming)


# Показати всі контакти
def show_all(book):
    if not book.data:
        return "Контактів поки немає."
    return "\n".join(str(record) for record in book.values())

def show_birthdays(book):
    result = book.get_upcoming_birthdays()
    return "\n".join(result) if result else "Немає привітань на цьому тижні."

#MAIN
def main():
    book = AddressBook()
    print("📞 Ласкаво просимо в помічник-бота!")

    while True:
        user_input = input("Введіть команду: ").strip()
        if not user_input:
            continue

        cmd, *args = user_input.split()
        command = cmd.lower()

        if command in ["close", "exit"]:
            print("👋 До побачення!")
            break
        elif command == "hello":
            print("Привіт! Як я можу вам допомогти?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "show-bday":
            print(show_birthday(args, book))
        elif command == "add-bday":
            print(add_birthday(args, book))
        elif command == "all":
            print(show_all(book))
        else:
            print("❓ Невідома команда. Спробуйте ще раз.")


if __name__ == "__main__":
    main()
