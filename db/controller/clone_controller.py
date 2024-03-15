from db.model.clone_model import CloneModel

class CloneController:
    def __init__(self):
        self.model = CloneModel()

    def update_voice_id_controller(self, user_id, voice_id):
        self.model.update_voice_id(user_id, voice_id)