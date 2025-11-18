from api_6sem_back_end.repositories.user_repository import UserRepository


class UserService:

    @staticmethod
    def create_user(data: dict):
        email = data.get("email")
        password = data.get("password")

        user_data = {
            "email": email,
            "isActive": True,
            "login": {
                "username": email,
                "password": password
            },
            "name": data.get("name"),
            "role": data.get("role"),
            "department": data.get("department", "-")
        }

        return UserRepository.create_user(user_data)