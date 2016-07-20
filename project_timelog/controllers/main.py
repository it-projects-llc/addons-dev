# -*- coding: utf-8 -*-
import datetime
import time
import openerp
from openerp import http
from openerp.http import request
from openerp.addons.base import res
import werkzeug

class Controller(openerp.addons.bus.bus.Controller):
    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            registry, cr, uid, context = request.registry, request.cr, request.session.uid, request.context
            channels.append((request.db, 'project.timelog', request.uid))
        return super(Controller, self)._poll(dbname, channels, last, options)

    @http.route('/timelog/init', type="json", auth="public")
    def init_timelog(self, **kwargs):
        current_user = request.env["res.users"].search([("id", "=", http.request.env.user.id)]) # current user
        current_user_active_task_id = current_user.active_task_id # activ task for current user
        current_user_active_work_id = current_user.active_work_id # activ subwork for current user

        stopline = request.env["project.task"].search([('id', '=', current_user_active_task_id)]) # stopline for current task

        # All logs
        all_timelog =  request.env["project.timelog"]

        # All logs for current user
        all_timelog_current_user = all_timelog.search([("user_id", "=", current_user.id)])

        # All logs for current user and current task
        all_timelog_current_user_and_task = all_timelog.search([("user_id", "=", current_user.id),("work_id.task_id", "=", current_user_active_task_id)])

        # All logs for other users and current task
        all_timelog_other_users = all_timelog.search([("user_id", "!=", current_user.id),("work_id.task_id", "=", current_user_active_task_id)])

        first_timelog =  all_timelog.search([("work_id", "=", current_user_active_work_id)])

        subwork = request.env["project.task.work"].search([("id", "=", current_user_active_work_id)]) # current user

        subwork_name = "None"
        if len(subwork) is not 0:
            subwork_name = subwork.name

        # 1. All time (today) in current work for current user
        first_init_time = 0
        if len(all_timelog_current_user) is not 0:
            if len(first_timelog)>0 and first_timelog[0].start_datetime is not False:
                date_object = datetime.datetime.strptime(first_timelog[0].start_datetime, "%Y-%m-%d %H:%M:%S")
                if date_object.day == datetime.datetime.now().day:
                    first_init_time = request.env["project.timelog"].sum_time(first_timelog)

        play_status = False
        if len(all_timelog_current_user) is not 0:
            if first_timelog[-1].end_datetime is False:
                play_status = True

        # 2. All time in current task for current user
        second_init_time = 0
        if len(all_timelog_current_user_and_task) is not 0:
            second_init_time = request.env["project.timelog"].sum_time(all_timelog_current_user_and_task)

        # 3. All the time for today 3.
        third_init_time = 0
        timelog_today = all_timelog.search([("user_id", "=", current_user.id), ("start_datetime", ">=", datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')), ("start_datetime", "<=", datetime.datetime.now().strftime('%Y-%m-%d 23:59:59'))])
        if len(timelog_today) is not 0:
            third_init_time = request.env["project.timelog"].sum_time(timelog_today)

        # 4. All time this week
        fourth_init_time = 0
        today = datetime.datetime.today()
        first_day_week = today - datetime.timedelta(7 - datetime.datetime.weekday(today))
        timelog_this_week = all_timelog.search([("user_id", "=", current_user.id), ("start_datetime", ">=", first_day_week.strftime('%Y-%m-%d 00:00:00')), ("start_datetime", "<=", datetime.datetime.now().strftime('%Y-%m-%d 23:59:59'))])
        if len(timelog_this_week) is not 0:
            fourth_init_time = request.env["project.timelog"].sum_time(timelog_this_week)

        desctiption_timer = []
        if len(all_timelog_other_users) != 0:
            all_timelog_other_users = all_timelog.search([("user_id", "!=", current_user.id),("work_id.task_id", "=", current_user_active_task_id)])
            for e in all_timelog_other_users:
                desctiption_timer.append(str(e.user_id.name))
                desctiption_timer.append(str(e.duration))

        timerstopline = 0
        if stopline.datetime_stopline is not False:
            timerstopline = str(stopline.datetime_stopline)

        config = request.env["ir.config_parameter"]
        convert_sec = 3600

        resultat = {
            'timer_status': play_status,
            'task_id': current_user_active_task_id,
            'work_id': current_user_active_work_id,
            "planned_hours": int(round(stopline.planned_hours*convert_sec,0)),
            "stopline": timerstopline,

            "init_first_timer": first_init_time,
            "init_second_timer": second_init_time,
            "init_third_timer": third_init_time,
            "init_fourth_timer": fourth_init_time,

            "time_subtasks": int(round(float(config.get_param("project_timelog.time_subtasks"))*convert_sec,0)),
            "time_warning_subtasks": int(round(float(config.get_param("project_timelog.time_warning_subtasks"))*convert_sec,0)),

            "normal_time_day": int(round(float(config.get_param("project_timelog.normal_time_day"))*convert_sec,0)),
            "good_time_day": int(round(float(config.get_param("project_timelog.good_time_day"))*convert_sec,0)),

            "normal_time_week": int(round(float(config.get_param("project_timelog.normal_time_week"))*convert_sec,0)),
            "good_time_week": int(round(float(config.get_param("project_timelog.good_time_week"))*convert_sec,0)),

            "name_first_timer": subwork_name,
            "description_second_timer": desctiption_timer,
        }

        return resultat

    @http.route('/timelog/stop_timer', type="json", auth="public")
    def stop_timer(self, timelog_id, **kwargs):
        last_timelog =  request.env["project.timelog"].search([("id", "=", timelog_id)])
        last_timelog.write({"end_datetime": datetime.datetime.now()})
        return True

