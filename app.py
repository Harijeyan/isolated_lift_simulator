from flask import Flask,jsonify,request
import threading
app = Flask(__name__)
import time

inital = {
    "floor": 1,
    "eta": 0,
    "state": "IDLE",
    "direction": "NAN",
    "person": 0
}
moving_sec = 3
waiting = 4
# floors = [1,2,3,4,5,6,7,8,9,10]


def dropoff():
    inital["state"] = "DROPOFF"
    inital["person"] = 0
    print(time.time(), '\t', inital)
    time.sleep(waiting)


def pickup():
    inital["state"] = "PICKUP"
    inital["person"] = 1
    print(time.time(),'\t',inital)
    time.sleep(waiting)
    inital["state"] = "TO_DROPOFF"




def move_floor(pick):
    to = 0
    frm = 0
    if inital["direction"] == "UP":
        frm = inital["floor"]
        to = pick
    else:
        frm = pick
        to = inital["floor"]
    for i in range(frm,to):
        if inital["direction"] =="UP":
            inital["floor"] +=1
        else:
            inital["floor"] -= 1
        inital["eta"] -= 3
        print(time.time(),'\t',inital)
        time.sleep(moving_sec)


def eta_time(pick):
    between_floors = pick-inital["floor"]
    direction = "NAN"
    eta_estimation = 0
    if between_floors>=0 :
        direction = "UP"
        eta_estimation = between_floors*3
    else:
        direction= "DOWN"
        eta_estimation = -between_floors * 3
    inital["direction"] = direction
    inital["eta"] = eta_estimation
    return eta_estimation


def lift_process(pick,drop):
    inital["state"] = "TO_PICKUP"
    move_floor(pick)
    pickup()
    inital["state"] = "TO_DROPOFF"
    eta_time(drop)
    move_floor(drop)
    dropoff()
    inital["state"] = "IDLE"
    inital["direction"] ="NAN"
    print(time.time(), '\t', inital)


@app.route('/smartkent/liftsimulation/')
def lift_simulation():
    if inital["state"]=="IDLE":
        if request.args.get("fromFloor") and request.args.get("toFloor"):
            print(time.time(), '\t', inital)
            pickup_floor = int(request.args.get("fromFloor"))
            drop_floor = int(request.args.get("toFloor"))
            estimation = {"ETA": eta_time(pickup_floor)}
            download_thread = threading.Thread(target=lift_process, args=[pickup_floor, drop_floor])
            download_thread.start()
            return jsonify(estimation),200
        else:
            return jsonify({"error":"Required from floor and to floor params"}),400

    else:
        return jsonify({"error":"Lift busy"}),409


if __name__ == '__main__':
    app.run()
