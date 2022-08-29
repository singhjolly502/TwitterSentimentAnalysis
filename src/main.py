from sentiment.sentiment_app import sentiment_blueprint
from app import app

if __name__ == "__main__":
    app.register_blueprint(sentiment_blueprint)
    print("======Here====")
    print(f"These are the valid URLs: {[str(p) for p in app.url_map.iter_rules()]}")
    app.run(host='0.0.0.0', debug=True)
