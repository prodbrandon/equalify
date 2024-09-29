from datetime import date

class Scholarship:
    def __init__(self, id: int, name: str, gender: str, merit_based: bool,
                 ethnicity: str, university: str, location: str, reward: float, 
                 LGBT: bool, extras: str, due_date: date, essay_required: bool, description: str):
        self.__id = id
        self.__name = name
        self.__gender = gender
        self.__merit_based = merit_based
        self.__ethnicity = ethnicity
        self.__university = university
        self.__location = location
        self.__reward = reward
        self.__LGBT = LGBT
        self.__extras = extras
        self.__due_date = due_date
        self.__essay_required = essay_required
        self.__description = description

    def __hash__(self) -> int:
        return hash((self.__id, self.__name, self.__merit_based, 
                     self.__gender, self.__ethnicity, self.__university, 
                     self.__location, self.__reward, self.__LGBT, 
                     self.__extras, self.__due_date, self.__essay_required, self.__description))

    def __eq__(self, other: 'Scholarship') -> bool:
        if not isinstance(other, Scholarship):
            return NotImplemented
        return (
            self.__id == other.__id and
            self.__name == other.__name and
            self.__merit_based == other.__merit_based and
            self.__gender == other.__gender and
            self.__ethnicity == other.__ethnicity and
            self.__university == other.__university and
            self.__location == other.__location and
            self.__reward == other.__reward and
            self.__LGBT == other.__LGBT and
            self.__extras == other.__extras and
            self.__due_date == other.__due_date and
            self.__essay_required == other.__essay_required and
            self.__description == other.__description
        )

    def get_id(self) -> int:
        return self.__id

    def get_name(self) -> str:
        return self.__name

    def get_merit(self) -> bool:
        return self.__merit_based
    
    def get_ethnicity(self) -> str:
        return self.__ethnicity

    def get_gender(self) -> str:
        return self.__gender

    def get_university(self) -> str:
        return self.__university

    def get_location(self) -> str:
        return self.__location
    
    def get_LGBT(self) -> bool:
        return self.__LGBT
    
    def get_reward(self) -> float:
        return self.__reward

    def get_extras(self) -> str:
        return self.__extras

    def get_due_date(self) -> date:
        return self.__due_date
    
    def get_essay_required(self) -> bool:
        return self.__essay_required
    
    def get_description(self) -> str:
        return self.__description
    
    def set_id(self, id: int) -> None:
        self.__id = id

    def set_name(self, name: str) -> None:
        self.__name = name

    def set_gender(self, gender: str) -> None:
        self.__gender = gender

    def set_merit_based(self, merit_based: bool) -> None:
        self.__merit_based = merit_based

    def set_ethnicity(self, ethnicity: str) -> None:
        self.__ethnicity = ethnicity

    def set_university(self, university: str) -> None:
        self.__university = university

    def set_location(self, location: str) -> None:
        self.__location = location

    def set_reward(self, reward: float) -> None:
        self.__reward = reward

    def set_LGBT(self, LGBT: bool) -> None:
        self.__LGBT = LGBT

    def set_extras(self, extras: str) -> None:
        self.__extras = extras

    def set_due_date(self, due_date: date) -> None:
        self.__due_date = due_date

    def set_essay_required(self, essay_required: bool) -> None:
        self.__essay_required = essay_required
    
    def set_description(self, description: str) -> None:
        self.__description = description
