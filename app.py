from flask import Flask, render_template, redirect
import requests
import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cowin_app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
}


class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state_id = db.Column(db.Integer, unique=True, nullable=False)
    state_name = db.Column(db.String(40), unique=False, nullable=False)
    districts = db.relationship("District", backref="state_backref")

    def __repr__(self):
        return f"{self.state_id} - {self.state_name}"


class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    district_id = db.Column(db.Integer, unique=True, nullable=False)
    district_name = db.Column(db.String(40), unique=False, nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey("state.state_id"), nullable=False)

    def __repr__(self):
        return f"{self.district_id} - {self.district_name} - {self.state_id}"


# @app.route("/", methods=["GET"])
# def index():
#     return "Index Page"


@app.route("/getStates", methods=["GET"])
def getStates():
    response = requests.get(
        "https://cdn-api.co-vin.in/api/v2/admin/location/states", headers=headers
    )
    if response.status_code == 200:
        data = response.json()["states"]
        for each_state in data:
            state_object = State(
                state_id=each_state["state_id"], state_name=each_state["state_name"]
            )
            db.session.add(state_object)
            db.session.commit()
        return "States are inserted in DB"
        # return render_template("states.html", data=data)
    else:
        return "States does not inserted due to some technical issue"


@app.route("/getDistricts", methods=["GET"])
def getDistricts():
    all_states_array = State.query.all()
    for state in all_states_array:
        response = requests.get(
            f"https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state.state_id}",
            headers=headers,
        )
        if response.status_code == 200:
            response_districts_array = response.json()["districts"]
            for each_district in response_districts_array:
                district_object = District(
                    district_id=each_district["district_id"],
                    district_name=each_district["district_name"],
                    state_id=state.state_id
                )
                db.session.add(district_object)
                db.session.commit()
        else:
            return f"Districts are inserted for previous states but failed to insert for STATE-: {state.state_name} in DB"
    return "Districts are inserted in DB"
    # response = requests.get(f"https://cdn-api.co-vin.in/api/v2/admin/location/districts/{34}")
    # if response.status_code == 200:
    #     data = response.json()["districts"]
    #     for each_district in data:
    #         district_object = District(
    #             district_id=each_district["district_id"],
    #             district_name=each_district["district_name"],
    #             # state_id=each_state[""]
    #         )
    #         db.session.add(district_object)
    #         db.session.commit()
    #     return 'Districts are inserted in DB'
    # else:
    #     return 'Districts does not inserted due to some technical issue'


if __name__ == "__main__":
    app.run(debug=True, port=8000)
