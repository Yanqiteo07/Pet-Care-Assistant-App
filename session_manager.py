class Session:
    current_user = None

    @classmethod
    def set_user(cls, username):
        cls.current_user = username

    @classmethod
    def get_user(cls):
        return cls.current_user if cls.current_user else "Guest"

    @classmethod
    def get_user_file(cls, base_filename):

        user = cls.get_user()
        safe_user = "".join(x for x in user if x.isalnum())
        return f"{safe_user}_{base_filename}"


active_session = Session()