from flaskblog import create_app, db


app = create_app()

db.create_all()

if __name__ == '__main__':
    app.run()
