from db.model.story_model import StoryModel

class StoryController:
    def __init__(self):
        self.model = StoryModel()

    def insert_story_controller(self, data):
        self.model.insert_story(data)

