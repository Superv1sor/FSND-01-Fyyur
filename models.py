from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate >> done!
    genres = db.Column(db.ARRAY(db.String(120))) # To store multiple genres
    website = db.Column(db.String(500)) # New field for the website link
    seeking_talent = db.Column(db.Boolean, default=False) # New field for 'Seeking Talent'
    seeking_description = db.Column(db.String(500)) # New field for 'Seeking Description'
    
    # Relationship with Artist model using Show model as secondary
    # artists = db.relationship('Artist', secondary='Show', backref=db.backref('venues', lazy=True))

    # Relationship with Show model. If a Venue is deleted, its associated Show instances are also deleted.
    shows = db.relationship('Show', backref='venue_shows', lazy=True, cascade='all, delete-orphan', overlaps="artists,venues")


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate >> done!
    genres = db.Column(db.ARRAY(db.String(120))) # To store multiple genres
    website = db.Column(db.String(500)) # New field for the website link
    seeking_venue = db.Column(db.Boolean, default=False) # New field for 'Looking for Venues'
    seeking_description = db.Column(db.String(500)) # New field for 'Seeking Description'

    # Relationship with Venue model using Show model as secondary
    # venues = db.relationship('Venue', secondary='Show', backref=db.backref('artists', lazy=True))

    shows = db.relationship('Show', backref='artist_shows', lazy=True, overlaps="venues")

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)  # Foreign Key reference to Artist model
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)  # Foreign Key reference to Venue model
    # Establish relationship with Artist and Venue models
    artist = db.relationship('Artist', overlaps="artist_shows,shows")  # 'shows' relationship in Artist model
    venue = db.relationship('Venue', overlaps="venue_shows,shows,venues")  # 'shows' relationship in Venue models
