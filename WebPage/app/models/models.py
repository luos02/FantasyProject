class UserModel:
    @staticmethod
    def authenticate(username, password):
        # Static usernames
        users = {
            "Fabian": "1234",
            "admin": "admin",
        }
        return users.get(username) == password

class ContentModel:
    @staticmethod
    def get_content(content_id):
        content_data = {
            "subopcion1": {
                "title": "Subopción 1",
                "description": "Este es el contenido de la subopción 1."
            },
            "subopcion2": {
                "title": "Subopción 2",
                "description": "Este es el contenido de la subopción 2."
            },
            "subopcion3": {
                "title": "Subopción 3",
                "description": "Este es el contenido de la subopción 3."
            },
            "subopcion4": {
                "title": "Subopción 4",
                "description": "Este es el contenido de la subopción 4."
            }
        }
        return content_data.get(content_id)