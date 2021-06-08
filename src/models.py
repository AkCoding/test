import enum

from src import db



class Status(str, enum.Enum):
    PENDING: str = 'pending'
    COMPLETED: str = 'complete'

    def __str__(self):
        return self.value

class Video(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    checkpoint_id = db.Column(db.Integer, unique=True, nullable=False)
    status = db.Column(db.Enum(Status), nullable=False, default="pending")
    download_status = db.Column(db.Enum(Status), nullable=False, default="pending")
    url = db.Column(db.String())
    transcript = db.Column(db.String())
    path = db.Column(db.String())
    api = db.Column(db.String(50))

