#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
# Add bc of error
import collections
collections.Callable = collections.abc.Callable
# Add Migrate 
from flask_migrate import Migrate
# Add to count shows
from sqlalchemy import func
# Add to get time
from datetime import datetime
# Importing SQLAlchemyError for handling database interaction errors
from sqlalchemy.exc import SQLAlchemyError
# Used for triggering HTTP errors
from flask import abort 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database >> done!

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

    id = db.Column(db.Integer, primary_key=True)
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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data. >> done!
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # get all distinct city and state pairs
    locations = db.session.query(Venue.city, Venue.state).distinct()

    data = []
    for location in locations:
        # for each pair, query the database for venues in the city/state
        venues = db.session.query(Venue.id, Venue.name).filter(Venue.city == location[0], Venue.state == location[1])
        venue_data = []
        for venue in venues:
            # calculate the number of upcoming shows for each venue
            num_upcoming_shows = db.session.query(func.count(Show.id)).filter(Show.venue_id == venue[0], Show.start_time > datetime.now()).scalar()
            venue_data.append({
                "id": venue[0],
                "name": venue[1],
                "num_upcoming_shows": num_upcoming_shows,
            })

        data.append({
            "city": location[0],
            "state": location[1],
            "venues": venue_data,
        })

    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive. >> done!
  # seach for Hop should return "The Musical Hop". >> done!
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" >> done!
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

    response = {
        "count": len(venues),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len([show for show in venue.shows if show.start_time > datetime.now()]),
        } for venue in venues]
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id >> done!

  venue = Venue.query.get(venue_id)

  if not venue:
    return render_template('errors/404.html')

  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()


  past_shows = []
  for show in past_shows_query:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    })

  upcoming_shows = []
  for show in upcoming_shows_query:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    })

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead >> done!
  # TODO: modify data to be the data object returned from db insertion >> done!

  # creating a new VenueForm instance from the form data
  form = VenueForm(request.form, meta={'csrf': False})

  if form.validate():
    try:
      # creating a new Venue instance
      venue = Venue()
      
      for field in form.data:
        if field == 'genres':
          # modifying data to be the data object returned from db insertion
          setattr(venue, field, form.data.get(field))
        elif field == 'seeking_talent':
          setattr(venue, field, True if form.data.get(field) in ('y', True, 't', 'True') else False)
        elif field == 'website_link':  # add this condition
          setattr(venue, 'website', form.data.get(field))  # set 'website' attribute of venue
        else:
          setattr(venue, field, form.data.get(field))  

      # adding the new venue to the session
      db.session.add(venue)
      
      # commit all changes
      db.session.commit()
      
      # on successful db insert, flash success
      flash('Venue ' + form.data['name'] + ' was successfully listed!')  
    except ValueError as e:
      print(e)
      
      # rollback the session in case of error
      db.session.rollback()
      
      # TODO: on unsuccessful db insert, flash an error instead. >> done!
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
      return render_template('pages/home.html')
    finally:
      # close the session
      db.session.close()
      
    return redirect(url_for('venues'))
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    return redirect(url_for('venues'))

# @app.route('/venues/<venue_id>', methods=['DELETE'])
@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using >> done!
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage >> done!

  if request.form.get('_method_delete') == 'DELETE':
    # try to delete the venue from the database
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully deleted.')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
    finally:
        db.session.close()
    
    # redirect to the homepage
    return redirect(url_for('index'))



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database >> done!

  # Query all artists from the database
  artist_query = Artist.query.all()

  # Create a list of dictionaries with id and name for each artist
  data = [{"id": artist.id, "name": artist.name} for artist in artist_query]

  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # get search term from form
  search_term = request.form.get('search_term', '')
  
  # query the database using ilike for case-insensitive partial string match
  artist_query = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))

  # format the data
  response={
    "count": artist_query.count(),
    "data": [{"id": artist.id, "name": artist.name} for artist in artist_query]
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id >> done!
     # get artist with given id from database
    artist = Artist.query.get(artist_id)
    
    if not artist:
        return render_template('errors/404.html'), 404

    # get current time
    now = datetime.now()

    # get all shows for this artist and separate them into past and upcoming shows
    shows = Show.query.filter_by(artist_id=artist_id).all()
    past_shows = []
    upcoming_shows = []
    for show in shows:
        venue = Venue.query.get(show.venue_id)
        show_info = {
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.start_time)
        }
        if show.start_time > now:
            upcoming_shows.append(show_info)
        else:
            past_shows.append(show_info)

    # create the data dict
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if artist:
    form.name.data = artist.name
    form.city.data = artist.city
    form.genres.data = artist.genres
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link
      
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  
  else:
    abort(404)  # Artist not found


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  if artist:
    artist.name = request.form['name']
    artist.city = request.form['city']
    genres_list = request.form.getlist('genres')
    artist.genres = genres_list
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.website = request.form['website_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue = True if request.form['seeking_venue'] == 'y' else False
    artist.seeking_description = request.form['seeking_description']
    artist.image_link = request.form['image_link']
    db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))
  
  else:
    abort(404) # Venue not found


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue:
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link
    # TODO: populate form with values from venue with ID <venue_id> >> done!
    return render_template('forms/edit_venue.html', form=form, venue=venue)

  else:
    abort(404) # Venue not found


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    if venue:
      venue.name = request.form['name']
      venue.genres = request.form.getlist('genres')
      venue.address = request.form['address']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.phone = request.form['phone']
      venue.website = request.form['website_link']
      venue.facebook_link = request.form['facebook_link']
      venue.seeking_talent = request.form['seeking_talent'] == 'y'
      venue.seeking_description = request.form['seeking_description']
      venue.image_link = request.form['image_link']

      db.session.commit()

    else:
      abort(404) # Venue not found

  except Exception as e:
    db.session.rollback()
    print(e)

  finally:
    db.session.close()
  # TODO: take values from the form submitted, and update existing >> done!
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead >> done!
  # TODO: modify data to be the data object returned from db insertion >> done!

  # creating a new ArtistForm instance from the form data
  form = ArtistForm(request.form, meta={'csrf': False})

  if form.validate():
    try:
      # creating a new Artist instance
      artist = Artist()
      
      for field in form.data:
        if field == 'genres':
          setattr(artist, field, form.data.get(field))
        elif field == 'seeking_venue':
          setattr(artist, field, True if form.data.get(field) in ('y', True, 't', 'True') else False)
        elif field == 'website_link':  # add this condition
          setattr(artist, 'website', form.data.get(field))  # set 'website' attribute of artist
        else:
          setattr(artist, field, form.data.get(field))  

      # adding the new artist to the session
      db.session.add(artist)
      
      # commit all changes
      db.session.commit()
      
      # on successful db insert, flash success
      flash('Artist ' + form.data['name'] + ' was successfully listed!')  
    except ValueError as e:
      print(e)
      
      # rollback the session in case of error
      db.session.rollback()
      
      # TODO: on unsuccessful db insert, flash an error instead. >> done!
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
      return render_template('pages/home.html')
    finally:
      # close the session
      db.session.close()
      
    return redirect(url_for('artists'))
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    return redirect(url_for('artists'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data. >> done!
  shows_query = Show.query.all()

  data = []
  for show in shows_query:
    show_data = {
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": str(show.start_time)  # convert to string as JSON does not support datetime object
    }
    data.append(show_data)

  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()

  artists = Artist.query.all()  # get all artists
  artist_choices = [(a.id, a.name) for a in artists]  # create choice tuples
  form.artist_id.choices = artist_choices  # set choices for artist_id

  venues = Venue.query.all()  # get all venues
  venue_choices = [(str(v.id), v.name) for v in venues]  # create choice tuples
  form.venue_id.choices = venue_choices  # set choices for venue_id
  
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead >> done!

  # creating a new ShowForm instance from the form data
  form = ShowForm(request.form, meta={'csrf': False})

  artists = Artist.query.all()  # get all artists
  artist_choices = [(str(a.id), a.name) for a in artists]  # create choice tuples
  form.artist_id.choices = artist_choices  # set choices for artist_id

  venues = Venue.query.all()  # get all venues
  venue_choices = [(str(v.id), v.name) for v in venues]  # create choice tuples
  form.venue_id.choices = venue_choices  # set choices for venue_id

  if form.validate():
    try:
      # creating a new Show instance
      show = Show()
      
      # populate show attributes with form data
      for field in form.data:
        setattr(show, field, form.data.get(field))  

      # adding the new show to the session
      db.session.add(show)
      
      # commit all changes
      db.session.commit()
      
      # on successful db insert, flash success
      flash('Show was successfully listed!')  
    except Exception as e:
      print(e)
      
      # rollback the session in case of error
      db.session.rollback()
      
      # TODO: on unsuccessful db insert, flash an error instead. >> done!
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Show could not be listed.')
      return render_template('pages/home.html')
    finally:
      # close the session
      db.session.close()
      
    return redirect(url_for('shows'))
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    return redirect(url_for('shows'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
