from flask import Flask
import os
from src.sentiment.sentiment_app import sentiment_blueprint
from src.auth import auth


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.register_blueprint(sentiment_blueprint)
app.register_blueprint(auth)
print(f"These are the valid URLs: {[str(p) for p in app.url_map.iter_rules()]}")

if __name__ == "__main__":
    # app.register_blueprint(sentiment_blueprint)
    print("======Here====")
    print(f"These are the valid URLs: {[str(p) for p in app.url_map.iter_rules()]}")
    app.run(debug=True)
