from app.models.models import ContentModel

#   Gets the content based on the ID using the model
#   Returns the dictionary with the content or none is it's not found
def get_content(content_id):
    return ContentModel.get_content(content_id)