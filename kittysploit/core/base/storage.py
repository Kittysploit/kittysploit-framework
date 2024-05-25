from typing import List, Any


class LocalStorage:
    @staticmethod
    def get_all() -> dict:
        """
        :return: list
        """
        return globals().keys()

    @staticmethod
    def add(name) -> None:
        """
        :param name: name
        :return: None
        """
        globals()[name] = None

    @staticmethod
    def set(name, value) -> None:
        """
        :param name: name
        :param value: value
        :return: None
        """
        globals()[name] = value

    @staticmethod
    def update(name, value) -> None:
        """
        :param name: name
        :param value: value
        :return: None
        """
        try:
            globals()[name].update(value)
        except Exception:
            pass

    @staticmethod
    def add_array(name, value) -> None:
        """
        :param name: name
        :param value: value
        :return: None
        """
        try:
            globals()[name].append(value)
        except Exception:
            pass

    @staticmethod
    def get_array(name, value) -> List:
        """
        :param name: name
        :param value: value
        :return: list
        """
        try:
            return globals()[name][value]
        except Exception:
            return []

    @staticmethod
    def set_array(name, value1, value2) -> None:
        """
        :param name: name
        :param value1: value1
        :param value2: value2
        :return: None
        """
        try:
            globals()[name][value1] = value2
        except Exception:
            pass

    @staticmethod
    def delete_element(name, value) -> None:
        """
        :param name: name
        :param value: value
        :return: None
        """
        try:
            del globals()[name][value]
        except Exception:
            pass

    @staticmethod
    def delete(name) -> None:
        """
        :param name: name
        :return: None
        """
        try:
            del globals()[name]
        except Exception:
            pass

    @staticmethod
    def get(name) -> Any:
        """
        :param name: name
        :return: value
        """
        try:
            return globals()[name]
        except Exception:
            return None
