import re
from collections import UserDict
from datetime import datetime, date


class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self):
        return str(self._value)


class Name(Field):
    @Field.value.setter
    def value(self, value):
        if 2 < len(value) < 15:
            self._value = value
        else:
            raise ValueError('Name must be from 3 to 15 characters')


class Phone(Field):

    @Field.value.setter
    def value(self, value):
        if value is None:
            self._value = value
        elif len(value) == 10 and value.isdigit():
            self._value = value
        else:
            raise ValueError


class Birthday(Field):

    @Field.value.setter
    def value(self, value: str):
        if value is None:
            self._value = value
        else:
            date_pattern = r'\d{2}\.\d{2}\.\d{4}'  # Регулярка формату дати "dd.mm.yyyy"
            if re.match(date_pattern, value):
                day, month, year = map(int, value.split('.'))
                # Валідація значень дня, місяця та року
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    max_day = 31
                elif month in [4, 6, 9, 11]:
                    max_day = 30
                elif month == 2:
                    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                        max_day = 29  # Високосний рік
                    else:
                        max_day = 28
                else:
                    raise ValueError('Wrong month')

                if 1 <= day <= max_day:
                    self._value = datetime(year, month, day).date()
                else:
                    raise ValueError('Incorrect day? month or year values')
            else:
                raise ValueError('Incorrect date format')

    def __str__(self):
        return f"{self._value.strftime('%d.%m.%Y')}"


class Record:
    def __init__(self, name, birthday=None):
        self.birthday = Birthday(birthday)
        self.name = Name(name)  # застосування асоціації під назваю композиція. Об'єкт Name існує поки є об'єкт Record
        self.phones = []

    def add_phone(self, number):
        if number in map(lambda num: num.value, self.phones):
            return 'has already'  # Якщо такий номер вже є у контакта
        else:
            self.phones.append(Phone(number))
            return 'has been added'

    def remove_phone(self, number):
        for p in self.phones:
            if number == p.value:
                self.phones.remove(p)
                return f'Phone number {self.name.value} has been removed'
        return f'{self.name.value} does not have this number'

    def edit_phone(self, old_number, new_number):
        for phone in self.phones:
            if phone.value == old_number:
                index = self.phones.index(phone)
                self.phones[index] = Phone(new_number)
                return
        raise ValueError

    def find_phone(self, num):
        for phone in self.phones:
            if phone.value == num:
                return phone

    def add_birthday(self, birthday):
        if self.birthday.value is None:
            self.birthday = Birthday(birthday)
            return 'added'
        else:
            return 'has already'

    def days_to_birthday(self):
        today = date.today()
        current_year = today.year
        if self.birthday.value < today:
            current_year += 1
        current_birthday = datetime(current_year, self.birthday.value.month, self.birthday.value.day).date()
        delta = current_birthday - today
        return delta.days

    def __str__(self):
        if self.birthday.value is not None:
            return (f"Name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, "
                    f"birthday: {self.birthday}, days to birthday: {self.days_to_birthday()}")
        return f"Name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, user):  # асоціація під назвою агригація
        self.data[user.name.value] = user

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data.keys():
            del self.data[name]

    def iterator(self, page_size):
        keys = list(self.data.keys())
        total_pages = (len(keys) + page_size - 1) // page_size

        for page_number in range(total_pages):
            start = page_number * page_size
            end = (page_number + 1) * page_size
            page = {k: self.data[k] for k in keys[start:end]}
            yield page

    def find_match(self, string):
        result = ''
        for record in self.data.values():
            if string.lower() in record.name.value.lower():
                result += f'{record}\n'

            for number in record.phones:
                if string in number.value:
                    result += f'{record}\n'

            if string in str(record.birthday.value):
                result += f'{record}\n'
        if result is None:
            return 'Nothing found'
        return result
