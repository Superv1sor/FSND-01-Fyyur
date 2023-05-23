from app import app, db, Venue, Artist, Show
from datetime import datetime

with app.app_context():
    # Generate MetaData instance for each table
    artist_meta = Artist.__table__
    venue_meta = Venue.__table__
    show_meta = Show.__table__

    # Explicitly drop each table in correct order
    show_meta.drop(db.engine, checkfirst=True)
    artist_meta.drop(db.engine, checkfirst=True)
    venue_meta.drop(db.engine, checkfirst=True)

    # Explicitly create each table
    artist_meta.create(db.engine, checkfirst=True)
    venue_meta.create(db.engine, checkfirst=True)
    show_meta.create(db.engine, checkfirst=True)

    # Add venues
    venue1 = Venue(
        id=1,
        name="The Musical Hop",
        genres=["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        address="1015 Folsom Street",
        city="San Francisco",
        state="CA",
        phone="123-123-1234",
        website="https://www.themusicalhop.com",
        facebook_link="https://www.facebook.com/TheMusicalHop",
        seeking_talent=True,
        seeking_description="We are on the lookout for a local artist to play every two weeks. Please call us.",
        image_link="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    )

    venue2 = Venue(
        id=2,
        name="The Dueling Pianos Bar",
        genres=["Classical", "R&B", "Hip-Hop"],
        address="335 Delancey Street",
        city="New York",
        state="NY",
        phone="914-003-1132",
        website="https://www.theduelingpianos.com",
        facebook_link="https://www.facebook.com/theduelingpianos",
        seeking_talent=False,
        image_link="https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    )

    venue3 = Venue(
        id=3,
        name="Park Square Live Music & Coffee",
        genres=["Rock n Roll", "Jazz", "Classical", "Folk"],
        address="34 Whiskey Moore Ave",
        city="San Francisco",
        state="CA",
        phone="415-000-1234",
        website="https://www.parksquarelivemusicandcoffee.com",
        facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        seeking_talent=False,
        image_link="https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    )

    db.session.add(venue1)
    db.session.add(venue2)
    db.session.add(venue3)


    # Add artists
    artist1 = Artist(id=4, 
        name="Guns N Petals", 
        city="San Francisco", 
        state="CA", 
        phone="326-123-5000", 
        genres=["Rock n Roll"], 
        website="https://www.gunsnpetalsband.com", 
        seeking_venue=True, 
        seeking_description="Looking for shows to perform at in the San Francisco Bay Area!", 
        image_link="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80", 
        facebook_link="https://www.facebook.com/GunsNPetals"
    )
                    
    artist2 = Artist(id=5, 
        name="Matt Quevedo", 
        city="New York", 
        state="NY", 
        phone="300-400-5000", 
        genres=["Jazz"], 
        image_link="https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80", 
        facebook_link="https://www.facebook.com/mattquevedo923251523"
    )
                    
    artist3 = Artist(id=6, 
        name="The Wild Sax Band", 
        city="San Francisco", 
        state="CA", 
        phone="432-325-5432", 
        genres=["Jazz", "Classical"], 
        image_link="https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
    )

    db.session.add(artist1)
    db.session.add(artist2)
    db.session.add(artist3)


    # Add shows
    show1 = Show(venue_id=1, artist_id=4, start_time=datetime.strptime('2019-05-21T21:30:00.000Z', '%Y-%m-%dT%H:%M:%S.%fZ'))
    show2 = Show(venue_id=3, artist_id=5, start_time=datetime.strptime('2019-06-15T23:00:00.000Z', '%Y-%m-%dT%H:%M:%S.%fZ'))
    show3 = Show(venue_id=3, artist_id=6, start_time=datetime.strptime('2035-04-01T20:00:00.000Z', '%Y-%m-%dT%H:%M:%S.%fZ'))
    show4 = Show(venue_id=3, artist_id=6, start_time=datetime.strptime('2035-04-08T20:00:00.000Z', '%Y-%m-%dT%H:%M:%S.%fZ'))
    show5 = Show(venue_id=3, artist_id=6, start_time=datetime.strptime('2035-04-15T20:00:00.000Z', '%Y-%m-%dT%H:%M:%S.%fZ'))
    
    db.session.add(show1)
    db.session.add(show2)
    db.session.add(show3)
    db.session.add(show4)
    db.session.add(show5)


    # Commit the transaction to save changes to the database
    db.session.commit()
