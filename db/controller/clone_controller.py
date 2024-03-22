from db.model.clone_model import CloneModel

class CloneController:
    def __init__(self):
        self.model = CloneModel()

    def update_voice_id_controller(self, user_id, voice_id):
        print("---- [update_voice_id_controller] ----")
        update_success = self.model.update_voice_id(user_id, voice_id)
        return update_success


    def delete_voice_id_controller(self, voice_id):
        print("---- [delete_voice_id_controller] ----")
        delete_success = self.model.delete_voice_id(voice_id)
        return delete_success