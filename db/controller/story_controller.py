from db.model.story_model import StoryModel

class StoryController:
    def __init__(self):
        self.model = StoryModel()

    def insert_and_select_story_controller(self, data):
        return self.model.insert_fairytale_info(data)

    def insert_video_controller(self, data):
        self.insert_video_controller(data)

