from abc import ABC, abstractmethod
from collections import UserDict
import json
import os

class UserInterface(ABC):
    @abstractmethod
    def display_message(self, message):
        pass

    @abstractmethod
    def display_contacts(self, contacts):
        pass

    @abstractmethod
    def display_error(self, error_message):
        pass

class ConsoleInterface(UserInterface):
    def display_message(self, message):
        print(message)

    def display_contacts(self, contacts):
        for contact in contacts:
            print(contact)

    def display_error(self, error_message):
        print(f"Error: {error_message}")

interface = ConsoleInterface()

class Record:
    def __init__(self, name):
        self.name = name
        self.phone = None

    def add_phone(self, value):
        self.phone = value

    def edit_phone(self, new_phone):
        if self.phone is not None:
            self.phone = new_phone
        else:
            raise ValueError("Phone number not found")

    def remove_phone(self):
        self.phone = None

    def __str__(self):
        return f"Name: {self.name}, Phone: {self.phone if self.phone else None}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name] = record

    def remove_record(self, name):
        del self.data[name]

    def search_by_name(self, name):
        name = name.lower()
        result = []
        for record in self.data.values():
            if record.name == name:
                result.append(record)
        return result

    def search_by_phone(self, phone):
        result = []
        for record in self.data.values():
            if record.phone == phone:
                result.append(record)
        return result

    def save_to_file(self, filename):
        data = []
        for record in self.data.values():
            data.append({
                'name': record.name,
                'phone': record.phone if record.phone else None
            })
        with open(filename, 'w') as file:
            json.dump(data, file)

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        self.data = {}
        for item in data:
            record = Record(item['name'])
            if item['phone']:
                record.add_phone(item['phone'])
            self.add_record(record)


def input_error(func):
    def wrapper(*args):
        try:
            result = func(*args)
        except Exception as e:
            interface.display_error(str(e))
            return None
        return result
    return wrapper


@input_error
def bot_hello():
    return "How can I help you?"

@input_error
def bot_add_contact(name, phone_number):
    name = name.lower()
    if name in dict_contacts:
        return "A contact with this name already exists."
    record = Record(name)
    record.add_phone(phone_number)
    dict_contacts.add_record(record)
    return "Contact details saved."

@input_error
def bot_change_phone(name, new_phone):
    name = name.lower()
    for record in dict_contacts.search_by_name(name):
        record.edit_phone(new_phone)
        return f"Phone number for {name} changed to {new_phone}."
    return "Contact with this name does not exist."

@input_error
def bot_get_phone(name):
    name = name.lower()
    for record in dict_contacts.search_by_name(name):
        return record.phone
    return "Contact with this name does not exist."

@input_error
def bot_show_all():
    if not dict_contacts.data:
        return "The contact list is empty."
    else:
        return "\n".join([str(record) for record in dict_contacts.data.values()])


if __name__ == "__main__":
    dict_contacts = AddressBook()
    if os.path.exists("data.json"):
        dict_contacts.load_from_file("data.json")    

    while True:
        command = input("Enter a command: ")

        match command:
            case "hello":
                interface.display_message(bot_hello())
            case "add":
                name = input("Enter the name: ")
                if name.lower() in dict_contacts:
                    interface.display_message("A contact with this name already exists.")
                    continue
                phone_number = input("Enter the phone number: ")
                interface.display_message(bot_add_contact(name, phone_number))
            case "change":
                name = input("Enter the name: ")
                new_phone = input("Enter the new phone number: ")
                interface.display_message(bot_change_phone(name, new_phone))
            case "get":
                name = input("Enter the name: ")
                interface.display_message(bot_get_phone(name))
            case "show":
                contacts = bot_show_all()
                if isinstance(contacts, str):
                    interface.display_error(contacts)
                else:
                    interface.display_contacts(contacts)
            case "exit":
                dict_contacts.save_to_file("data.json")
                interface.display_message("Goodbye!")
                break
            case _:
                interface.display_message("Invalid command. Please try again.")
