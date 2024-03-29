from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId

from app.schemas.voyage import VoyageStatus


def set_return_value(res):
    if res:
        return str(res)
    else:
        return None


def find_voyage(db, voyage_id):
    found = db["voyage"].find_one({"_id": ObjectId(voyage_id)}, {"_id": 0})
    return found


def create_voyage(db, voyage):
    voyage = jsonable_encoder(voyage)
    value = db["voyage"].insert_one(voyage)
    return str(value.inserted_id)


def change_status(db, voyage_id, state):
    changes = {"status": state}
    db["voyage"].find_one_and_update({"_id": ObjectId(voyage_id)},
                                     {"$set": changes})


def change_status_possible(db, voyage_id, new, before):
    voyage = find_voyage(db, voyage_id)

    if not voyage:
        raise Exception("Voyage Not Found")

    voyage_status = voyage.get("status")
    if voyage_status != before:
        raise Exception("Can't Change To Voyage to that state.")
    change_status(db, voyage_id, new)


def set_starting_status(db, voyage_id):
    new_status = VoyageStatus.STARTING.value
    before_status = VoyageStatus.WAITING.value
    change_status_possible(db, voyage_id, new_status, before_status)


def set_arriving_status(db, voyage_id):
    new_status = VoyageStatus.ARRIVING.value
    before_status = VoyageStatus.STARTING.value
    change_status_possible(db, voyage_id, new_status, before_status)


def set_travelling_status(db, voyage_id):
    new_status = VoyageStatus.TRAVELLING.value
    before_status = VoyageStatus.ARRIVING.value
    change_status_possible(db, voyage_id, new_status, before_status)


def set_finished_status(db, voyage_id):
    new_status = VoyageStatus.FINISHED.value
    before_status = VoyageStatus.TRAVELLING.value
    change_status_possible(db, voyage_id, new_status, before_status)
    changes = {"end_time": datetime.utcnow()}
    db["voyage"].find_one_and_update({"_id": ObjectId(voyage_id)},
                                     {"$set": changes})


def set_stopped_status(db, voyage_id):
    new_status = VoyageStatus.STOPPED.value
    before_status = VoyageStatus.WAITING.value

    change_status_possible(db, voyage_id, new_status, before_status)

    changes = {"end_time": datetime.utcnow()}
    db["voyage"].find_one_and_update({"_id": ObjectId(voyage_id)},
                                     {"$set": changes})


def delete_voyage(db, voyage_id):
    db["voyage"].find_one_and_delete({"_id": ObjectId(voyage_id)})


def get_date_voyages(db, user_id, is_driver, is_daily):
    today = datetime.utcnow()
    before = datetime(today.year, today.month, 1, 0, 0, 0)
    if is_daily:
        before = today - timedelta(days=1)

    before = before.isoformat()

    id_parameter = "passenger_id"
    if is_driver:
        id_parameter = "driver_id"

    times = db.voyage.aggregate([
        {"$match": {"$and": [
            {"status": {"$eq": VoyageStatus.FINISHED.value}},
            {id_parameter: {"$eq": user_id}},
            {"start_time": {"$gte": before}}
            ]}
         },
        {"$count": "amount"}
    ])
    results = [date for date in times]

    if len(results) > 0:
        return results[0].get("amount")
    else:
        return 0


def get_seniority(db, id, is_driver):
    today = datetime.utcnow()
    id_parameter = "passenger_id"
    if is_driver:
        id_parameter = "driver_id"

    first_date = db.voyage.aggregate([
        {"$match": {id_parameter: {"$eq": id}}},
        {"$sort": {"start_time": 1}},
        {"$limit": 1}
    ])
    results = [date for date in first_date]
    if len(results) == 0:
        return 0

    first_date_str = results[0].get("start_time")

    first_date = datetime.fromisoformat(first_date_str)

    return (today - first_date).days


def get_last_voyages(db, id, is_driver, amount):
    id_parameter = "passenger_id"
    if is_driver:
        id_parameter = "driver_id"

    last_voyages = db.voyage.aggregate([
        {"$match": {id_parameter: {"$eq": id}}},
        {"$sort": {"start_time": -1}},
        {"$limit": amount}
    ])

    return_lists = [data for data in last_voyages]

    for item in return_lists:
        item.update({"id": str(item.pop("_id"))})

    return return_lists


def add_review(db, voyage_id, review):
    review = jsonable_encoder(review)
    db["voyage"].find_one_and_update({"_id": ObjectId(voyage_id)},
                                     {"$push": {"reviews": review}})


def add_complaint(db, voyage_id, complaint):
    complaint = jsonable_encoder(complaint)
    db["voyage"].find_one_and_update({"_id": ObjectId(voyage_id)},
                                     {"$push": {"complaints": complaint}})


def get_average_score(db, user_id, is_driver):
    id_parameter = "passenger_id"
    if is_driver:
        id_parameter = "driver_id"

    by_driver = not is_driver

    average_ret = db.voyage.aggregate([
                                {"$unwind": "$reviews"},
                                {"$match": {"$and": [
                                    {id_parameter: {"$eq": user_id}},
                                    {"reviews.by_driver": {"$eq": by_driver}}
                                    ]}},
                                {"$group": {
                                     "_id": {
                                        "user_id": "$"+id_parameter,
                                     },
                                     "promedio": {"$avg": '$reviews.score'}
                                     }}
    ])

    result = [data for data in average_ret]

    if len(result) == 0:
        return "No Calification"

    average = result[0].get("promedio")
    return average


def get_reviews(db, user_id, is_driver, count):
    id_parameter = "passenger_id"
    if is_driver:
        id_parameter = "driver_id"

    by_driver = not is_driver

    last_reviews = db.voyage.aggregate([
                                {"$unwind": "$reviews"},
                                {"$match": {"$and": [
                                    {id_parameter: {"$eq": user_id}},
                                    {"reviews.by_driver": {"$eq": by_driver}}
                                    ]}},
                                {"$sort": {"start_time": -1}},
                                {"$limit": count},
                                {"$project": {"reviews": 1, "_id": 0}}
    ])
    result = [data for data in last_reviews]
    return result


def get_number_voyages(db, user_id, is_driver):
    id_parameter = "passenger_id"
    if is_driver:
        id_parameter = "driver_id"

    count_voyages = db.voyage.aggregate([
                                {"$match":
                                    {id_parameter: {"$eq": user_id}}},
                                {"$count": "count"}
    ])
    result = [data for data in count_voyages]
    if len(result) == 0:
        return 0
    return result[0].get("count")


def get_current_voyage(db, user_id, is_driver):
    id_parameter = "passenger_id"
    if is_driver:
        id_parameter = "driver_id"

    last_voyage = db.voyage.aggregate([
        {"$match": {"$and": [
            {"status": {"$ne": VoyageStatus.FINISHED.value}},
            {"status": {"$ne": VoyageStatus.CANCELLED.value}},
            {"status": {"$ne": VoyageStatus.STOPPED.value}},
            {id_parameter: {"$eq": user_id}}
            ]}
         },
    ])

    result = [data for data in last_voyage]

    if len(result) == 0:
        raise Exception("Id Not Found In Any Voyage")

    id = result[0].get("_id")
    return str(id)


def get_history(db, id, is_driver):
    seniority = get_seniority(db, id, is_driver)
    daily = get_date_voyages(db, id, is_driver, True)
    monthly = get_date_voyages(db, id, is_driver, False)

    return seniority, daily, monthly


def get_all_complaints(db):
    complaints = db.voyage.find({"complaints":
                                {"$exists": True,
                                 "$not": {"$size": 0}}})
    result = []
    for data in complaints:
        print(data)
        id = str(data.get("_id"))
        voyage = {"id": id}
        for key, value in data.items():
            if key != "_id":
                voyage.update({key: value})
        result.append(voyage)
    return result


def update_price(db, id_voyage, price):
    changes = {"price": price}
    db["voyage"].find_one_and_update({"_id": ObjectId(id_voyage)},
                                     {"$set": changes})
