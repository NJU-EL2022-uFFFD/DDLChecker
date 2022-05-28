import json
import time
import uuid

from flask import Blueprint, jsonify
from flask_sqlalchemy import Pagination
from sqlalchemy.orm import Query

from db import db
from routes.rules.community_rules import AddCourseRulesForCommunity, AddDDLRulesForCommunity, SubscribeCourseRules, \
    FetchDDLRule, ListCourseRulesForCommunity, ListDDLRulesForCommunity
from routes.rules.ddl_rules import ListDDLsRules
from routes.utils import get_context, check_data, make_response
from db.userSubs import UserSubscriptions
from db.ddl import Ddl
from db.sourceDdl import SourceDdl
from db.course import Course
from db.account import Account
from routes.utils import get_context_user, make_response

bp = Blueprint("community", __name__, url_prefix="/community")


@bp.route("/course/list", methods=["GET", "POST"])
def list_course():
    user, data = get_context_user()
    check_data(ListCourseRulesForCommunity, data)

    page = Course.query.paginate(data["page"], data["size"])
    course_count = page.total
    total_pages = page.pages
    courses = [i.to_dict() for i in page.items]
    for i in courses:
        i.update({"subscribed": True if i["course_uuid"] in map(lambda x: x.course_uuid,
                                                                user.subscriptions.all()) else False})

    return make_response(0, "OK", {"courses": courses, "course_count": course_count, "total_pages": total_pages})


@bp.route("/ddl/list", methods=["GET", "POST"])
def list_ddl():
    user, data = get_context_user()
    check_data(ListDDLRulesForCommunity, data)

    page = SourceDdl.query.paginate(data["page"], data["size"])
    source_ddl_count = page.total
    total_pages = page.pages
    source_ddls = [i.to_dict() for i in page.items]
    for i in source_ddls:
        i.update({"added": True if i["id"] in map(lambda x: x.source_ddl_id, user.ddls.all()) else False})

    return make_response(0, "OK", {"source_ddl_count": source_ddl_count, "source_ddls": source_ddls, "total_pages": total_pages})


@bp.route("/course/add", methods=["GET", "POST"])
def add_course():
    user, data = get_context_user()
    check_data(AddCourseRulesForCommunity, data)

    if Course.query.filter(
            Course.course_uuid == str(uuid.uuid5(uuid.UUID(data["platform_uuid"]), data["course_name"]))).count() != 0:
        return make_response(-1, "Course already exists, change another name.(nmsl)", {})

    course = Course(data["course_name"], str(uuid.uuid5(uuid.UUID(data["platform_uuid"]), data["course_name"])),
                    data["platform_uuid"], creator_id=user.id)

    db.session.add(course)
    sub = UserSubscriptions(user.id, course.course_uuid, data["platform_uuid"])
    db.session.add(sub)
    db.session.commit()

    return make_response(0, "OK", {"course_uuid": course.course_uuid})


@bp.route("/ddl/add", methods=["GET", "POST"])
def add_ddl():
    user, data = get_context_user()
    check_data(AddDDLRulesForCommunity, data)

    if Course.query.filter(Course.course_uuid == data["course_uuid"]).first() is None:
        return make_response(-1, "Course not found.(nmsl)", {})

    if SourceDdl.query.filter(SourceDdl.title == data['title'], SourceDdl.ddl_time == data['ddl_time']).count() >= 1:
        return make_response(-1, "Why do you add so many fucking same ddls! (nmsl)", {})

    ddl = SourceDdl(data["course_uuid"], data["platform_uuid"], data["title"], data["content"], data["tag"],
                    data["ddl_time"], time.time() * 1000, creator_id=user.id)
    db.session.add(ddl)

    db.session.commit()

    return make_response(0, "OK", {"id": ddl.id})


@bp.route("/course/subscribe", methods=["GET", "POST"])
def subscribe_course():
    user, data = get_context_user()
    check_data(SubscribeCourseRules, data)

    course = Course.query.filter(Course.course_uuid == data["course_uuid"]).first()
    if course is None:
        return make_response(-1, "Course not exists(nmsl).", {})

    sub = UserSubscriptions(user.id, data["course_uuid"], course.platform_uuid)

    if user.subscriptions.filter(UserSubscriptions.course_uuid == data['course_uuid']).first() is not None:
        return make_response(-1, "Subscription already exists.(nmsl)", {})

    # todo: 马上为用户分配ddl

    db.session.add(sub)
    db.session.commit()

    return make_response(0, "OK", {"id": sub.id})


@bp.route("/course/unsubscribe", methods=["GET", "POST"])
def unsubscribe_course():
    user, data = get_context_user()
    check_data(SubscribeCourseRules, data)

    sub = user.subscriptions.filter(UserSubscriptions.course_uuid == data['course_uuid'],
                                    UserSubscriptions.userid == user.id).first()
    if sub is None:
        return make_response(-1, "Subscription not exists.(What's wrong with you?)(nmsl)", {})

    db.session.delete(sub)
    db.session.commit()

    return make_response(0, "OK", {"id": sub.id})


@bp.route("/ddl/fetch")
def fetch_ddl():
    user, data = get_context_user()
    check_data(FetchDDLRule, data)

    source_ddl = SourceDdl.query.get(data['id'])

    if source_ddl is None:
        return make_response(-1, "SourceDdl not exists.(nmsl)", {})

    if Ddl.query.filter(Ddl.source_ddl_id == data['id']).first() is not None:
        return make_response(-1, "SourceDdl already added.(nmsl)", {})

    ddl = Ddl(user.id, source_ddl.title, source_ddl.ddl_time, int(time.time() * 1000), source_ddl.content,
              source_ddl.tag, source_ddl.course_uuid, source_ddl.platform_uuid, source_ddl.id)

    db.session.add(ddl)
    db.session.commit()

    return make_response(0, "OK", {"id": ddl.id})
