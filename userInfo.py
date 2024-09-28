class UserData:
    def __init__(self, income, gender, race,
                  major, university, location):
        self.__income = income
        self.__gender = gender
        self.__race = race
        self.__major = major
        self.__university = university
        self.__location = location

    def get_income(self):
        return self.__income

    def get_gender(self):
        return self.__gender

    def get_race(self):
        return self.__race

    def get_major(self):
        return self.__major

    def get_university(self):
        return self.__university

    def get_location(self):
        return self.__location
    
    def set_income(self, income):
        self.__income = income

    def set_gender(self, gender):
        self.__gender = gender

    def set_race(self, race):
        self.__race = race

    def set_major(self, major):
        self.__major = major

    def set_university(self, university):
        self.__university = university

    def set_location(self, location):
        self.__location = location


        