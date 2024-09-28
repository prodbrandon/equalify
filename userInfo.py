class UserData:
    def __init__(self, income: float, GPA: float, gender: str, ethnicity: str,
                 major: str, university: str, location: str):
        self.__GPA = GPA
        self.__income = income
        self.__gender = gender
        self.__ethnicity = ethnicity
        self.__major = major
        self.__university = university
        self.__location = location

    def get_income(self) -> float:
        return self.__income
    
    def get_gpa(self) -> float:
        return self.__GPA

    def get_gender(self) -> str:
        return self.__gender

    def get_ethnicity(self) -> str:
        return self.__ethnicity

    def get_major(self) -> str:
        return self.__major

    def get_university(self) -> str:
        return self.__university

    def get_location(self) -> str:
        return self.__location
    
    def set_income(self, income: float) -> None:
        if income < 0:
            raise ValueError("Income must be a non-negative value.")
        self.__income = income

    def set_income(self, GPA: float) -> None:
        if GPA < 0:
            raise ValueError("GPA must be a non-negative value.")
        self.__GPA = GPA

    def set_gender(self, gender: str) -> None:
        self.__gender = gender

    def set_ethnicity(self, ethnicity: str) -> None:
        self.__ethnicity = ethnicity

    def set_major(self, major: str) -> None:
        self.__major = major

    def set_university(self, university: str) -> None:
        self.__university = university

    def set_location(self, location: str) -> None:
        self.__location = location
