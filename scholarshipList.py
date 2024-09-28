from scholarship import Scholarship

class ScholarshipList:
    def __init__(self):
        self.__data = set()

    def add_scholarship(self, new_scholarship: Scholarship) -> None:
        self.__data.add(new_scholarship)

    def remove_scholarship(self, target: Scholarship) -> bool:
        if target in self.__data:
            self.__data.remove(target)
            return True
        return False

    def get_scholarships(self) -> set:
        return self.__data