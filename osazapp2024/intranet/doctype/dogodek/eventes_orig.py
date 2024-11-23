# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE


import json

import frappe
from frappe import _
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe.desk.doctype.notification_settings.notification_settings import (
	is_email_notifications_enabled_for_type,
)
from frappe.desk.reportview import get_filters_cond
from frappe.website.website_generator import WebsiteGenerator
from frappe.utils import (
	add_days,
	add_months,
	cint,
	cstr,
	date_diff,
	format_datetime,
	get_datetime_str,
	getdate,
	now_datetime,
	nowdate,
)
from frappe.utils.user import get_enabled_system_users
from frappe.model.document import Document



weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
communication_mapping = {
	"": "Dogodek",
	"Dogodek": "Dogodek",
	"Meeting": "Meeting",
	"Call": "Phone",
	"Sent/Received Email": "Email",
	"Other": "Other",
}

class Dogodek(Document):
	pass

class Mynekineki(Document):

	print("hello dogodek")
	def validate(self):
		self.route = str(self.name)
		if self.event_category == "Dogodek":
			self.color = "#4463F0"
		elif self.event_category == "Dnevi dejavnosti":
			self.color = "#ECAD4B"
	def set_status_of_dogodeks():
		dogodki = frappe.get_list("Dogodek", filters={"status": "Open"}, fields=["name", "ends_on", "repeat_till"])
		for dogodek in dogodki:
			if (dogodek.ends_on and getdate(dogodek.ends_on) < getdate(nowdate())) or (
				dogodek.repeat_till and getdate(dogodek.repeat_till) < getdate(nowdate())
			):
				frappe.db.set_value("Dogodek", dogodek.name, "status", "Closed")
	

   

class Dogodek(WebsiteGenerator):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING
 
	if TYPE_CHECKING:
		from frappe.desk.doctype.dogodek_participants.dogodek_participants import DogodekParticipants
		from frappe.types import DF

		add_video_conferencing: DF.Checka
		all_day: DF.Check
		color: DF.Color | None
		description: DF.TextEditor | None
		ends_on: DF.Datetime | None
		dogodek_category: DF.Literal["Dogodek", "Meeting", "Call", "Sent/Received Email", "Other"]
		dogodek_participants: DF.Table[DogodekParticipants]
		dogodek_type: DF.Literal["Private", "Public"]
		friday: DF.Check
		google_calendar: DF.Link | None
		google_calendar_dogodek_id: DF.Data | None
		google_calendar_id: DF.Data | None
		google_meet_link: DF.Data | None
		monday: DF.Check
		pulled_from_google_calendar: DF.Check
		repeat_on: DF.Literal["", "Daily", "Weekly", "Monthly", "Yearly"]
		repeat_this_dogodek: DF.Check
		repeat_till: DF.Date | None
		saturday: DF.Check
		send_reminder: DF.Check
		sender: DF.Data | None
		starts_on: DF.Datetime
		status: DF.Literal["Open", "Completed", "Closed", "Cancelled"]
		subject: DF.SmallText
		sunday: DF.Check
		sync_with_google_calendar: DF.Check
		thursday: DF.Check
		tuesday: DF.Check
		wednesday: DF.Check

	# end: auto-generated types
	def validate(self):
		if not self.starts_on:
			self.starts_on = now_datetime()

		# if start == end this scenario doesn't make sense i.e. it starts and ends at the same second!
		self.ends_on = None if self.starts_on == self.ends_on else self.ends_on

		if self.starts_on and self.ends_on:
			self.validate_from_to_dates("starts_on", "ends_on")

		if self.repeat_on == "Daily" and self.ends_on and getdate(self.starts_on) != getdate(self.ends_on):
			frappe.throw(_("Daily Dogodeks should finish on the Same Day."))

		if self.sync_with_google_calendar and not self.google_calendar:
			frappe.throw(_("Select Google Calendar to which dogodek should be synced."))

		if not self.sync_with_google_calendar:
			self.add_video_conferencing = 0

	def before_save(self):
		self.set_participants_email()

	def on_update(self):
		self.sync_communication()

	def on_trash(self):
		communications = frappe.get_all(
			"Communication", dict(reference_doctype=self.doctype, reference_name=self.name)
		)
		if communications:
			for communication in communications:
				frappe.delete_doc_if_exists("Communication", communication.name)

	def sync_communication(self):
		if self.dogodek_participants:
			for participant in self.dogodek_participants:
				filters = [
					["Communication", "reference_doctype", "=", self.doctype],
					["Communication", "reference_name", "=", self.name],
					["Communication Link", "link_doctype", "=", participant.reference_doctype],
					["Communication Link", "link_name", "=", participant.reference_docname],
				]
				if comms := frappe.get_all("Communication", filters=filters, fields=["name"], distinct=True):
					for comm in comms:
						communication = frappe.get_doc("Communication", comm.name)
						self.update_communication(participant, communication)
				else:
					meta = frappe.get_meta(participant.reference_doctype)
					if hasattr(meta, "allow_dogodeks_in_timeline") and meta.allow_dogodeks_in_timeline == 1:
						self.create_communication(participant)

	def create_communication(self, participant):
		communication = frappe.new_doc("Communication")
		self.update_communication(participant, communication)
		self.communication = communication.name

	def update_communication(self, participant, communication):
		communication.communication_medium = "Dogodek"
		communication.subject = self.subject
		communication.content = self.description if self.description else self.subject
		communication.communication_date = self.starts_on
		communication.sender = self.owner
		communication.sender_full_name = frappe.utils.get_fullname(self.owner)
		communication.reference_doctype = self.doctype
		communication.reference_name = self.name
		communication.communication_medium = (
			communication_mapping.get(self.dogodek_category) if self.dogodek_category else ""
		)
		communication.status = "Linked"
		communication.add_link(participant.reference_doctype, participant.reference_docname)
		communication.save(ignore_permissions=True)

	def add_participant(self, doctype, docname):
		"""Add a single participant to dogodek participants

		Args:
		        doctype (string): Reference Doctype
		        docname (string): Reference Docname
		"""
		self.append(
			"dogodek_participants",
			{
				"reference_doctype": doctype,
				"reference_docname": docname,
			},
		)

	def add_participants(self, participants):
		"""Add participant entry

		Args:
		        participants ([Array]): Array of a dict with doctype and docname
		"""
		for participant in participants:
			self.add_participant(participant["doctype"], participant["docname"])

	def set_participants_email(self):
		for participant in self.dogodek_participants:
			if participant.email:
				continue

			if participant.reference_doctype != "Contact":
				participant_contact = get_default_contact(
					participant.reference_doctype, participant.reference_docname
				)
			else:
				participant_contact = participant.reference_docname

			participant.email = (
				frappe.get_value("Contact", participant_contact, "email_id") if participant_contact else None
			)


@frappe.whitelist()
def delete_communication(dogodek, reference_doctype, reference_docname):
	deleted_participant = frappe.get_doc(reference_doctype, reference_docname)
	if isinstance(dogodek, str):
		dogodek = json.loads(dogodek)

	filters = [
		["Communication", "reference_doctype", "=", dogodek.get("doctype")],
		["Communication", "reference_name", "=", dogodek.get("name")],
		["Communication Link", "link_doctype", "=", deleted_participant.reference_doctype],
		["Communication Link", "link_name", "=", deleted_participant.reference_docname],
	]

	comms = frappe.get_list("Communication", filters=filters, fields=["name"])

	if comms:
		deletion = []
		for comm in comms:
			delete = frappe.get_doc("Communication", comm.name).delete()
			deletion.append(delete)

		return deletion

	return {}


def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	return f"""(`tabDogodek`.`dogodek_type`='Public' or `tabDogodek`.`owner`={frappe.db.escape(user)})"""


def has_permission(doc, user):
	if doc.dogodek_type == "Public" or doc.owner == user:
		return True

	return False


def send_dogodek_digest():
	today = nowdate()

	# select only those users that have dogodek reminder email notifications enabled
	users = [
		user
		for user in get_enabled_system_users()
		if is_email_notifications_enabled_for_type(user.name, "Dogodek Reminders")
	]

	for user in users:
		dogodeks = get_dogodeks(today, today, user.name, for_reminder=True)
		if dogodeks:
			frappe.set_user_lang(user.name, user.language)

			for e in dogodeks:
				e.starts_on = format_datetime(e.starts_on, "hh:mm a")
				if e.all_day:
					e.starts_on = "All Day"

			frappe.sendmail(
				recipients=user.email,
				subject=frappe._("Upcoming Dogodeks for Today"),
				template="upcoming_dogodeks",
				args={
					"dogodeks": dogodeks,
				},
				header=[frappe._("Dogodeks in Today's Calendar"), "blue"],
			)


@frappe.whitelist()
def get_dogodeks(start, end, user=None, for_reminder=False, filters=None) -> list[frappe._dict]:
	if not user:
		user = frappe.session.user

	if isinstance(filters, str):
		filters = json.loads(filters)

	filter_condition = get_filters_cond("Dogodek", filters, [])

	tables = ["`tabDogodek`"]
	if "`tabDogodek Participants`" in filter_condition:
		tables.append("`tabDogodek Participants`")

	dogodeks = frappe.db.sql(
		"""
		SELECT `tabDogodek`.name,
				`tabDogodek`.subject,
				`tabDogodek`.description,
				`tabDogodek`.color,
				`tabDogodek`.starts_on,
				`tabDogodek`.ends_on,
				`tabDogodek`.owner,
				`tabDogodek`.all_day,
				`tabDogodek`.dogodek_type,
				`tabDogodek`.repeat_this_dogodek,
				`tabDogodek`.repeat_on,
				`tabDogodek`.repeat_till,
				`tabDogodek`.monday,
				`tabDogodek`.tuesday,
				`tabDogodek`.wednesday,
				`tabDogodek`.thursday,
				`tabDogodek`.friday,
				`tabDogodek`.saturday,
				`tabDogodek`.sunday
				
		FROM {tables}
		WHERE (
				(
					(date(`tabDogodek`.starts_on) BETWEEN date(%(start)s) AND date(%(end)s))
					OR (date(`tabDogodek`.ends_on) BETWEEN date(%(start)s) AND date(%(end)s))
					OR (
						date(`tabDogodek`.starts_on) <= date(%(start)s)
						AND date(`tabDogodek`.ends_on) >= date(%(end)s)
					)
				)
				OR (
					date(`tabDogodek`.starts_on) <= date(%(start)s)
					AND `tabDogodek`.repeat_this_dogodek=1
					AND coalesce(`tabDogodek`.repeat_till, '3000-01-01') > date(%(start)s)
				)
			)
		{reminder_condition}
		{filter_condition}
		AND (
				`tabDogodek`.dogodek_type='Public'
				OR `tabDogodek`.owner=%(user)s
				OR EXISTS(
					SELECT `tabDocShare`.name
					FROM `tabDocShare`
					WHERE `tabDocShare`.share_doctype='Dogodek'
						AND `tabDocShare`.share_name=`tabDogodek`.name
						AND `tabDocShare`.user=%(user)s
				)
			)
		AND `tabDogodek`.status='Open'
		ORDER BY `tabDogodek`.starts_on""".format(
			tables=", ".join(tables),
			filter_condition=filter_condition,
			reminder_condition="AND coalesce(`tabDogodek`.send_reminder, 0)=1" if for_reminder else "",
		),
		{
			"start": start,
			"end": end,
			"user": user,
		},
		as_dict=1,
	)

	# process recurring dogodeks
	start = start.split(" ", 1)[0]
	end = end.split(" ", 1)[0]
	add_dogodeks = []
	remove_dogodeks = []

	def add_dogodek(e, date):
		new_dogodek = e.copy()

		enddate = (
			add_days(date, int(date_diff(e.ends_on.split(" ", 1)[0], e.starts_on.split(" ", 1)[0])))
			if (e.starts_on and e.ends_on)
			else date
		)

		new_dogodek.starts_on = date + " " + e.starts_on.split(" ")[1]
		new_dogodek.ends_on = new_dogodek.ends_on = enddate + " " + e.ends_on.split(" ")[1] if e.ends_on else None

		add_dogodeks.append(new_dogodek)

	for e in dogodeks:
		if e.repeat_this_dogodek:
			e.starts_on = get_datetime_str(e.starts_on)
			e.ends_on = get_datetime_str(e.ends_on) if e.ends_on else None

			dogodek_start, time_str = get_datetime_str(e.starts_on).split(" ")

			repeat = "3000-01-01" if cstr(e.repeat_till) == "" else e.repeat_till

			if e.repeat_on == "Yearly":
				start_year = cint(start.split("-", 1)[0])
				end_year = cint(end.split("-", 1)[0])

				# creates a string with date (27) and month (07) eg: 07-27
				dogodek_start = "-".join(dogodek_start.split("-")[1:])

				# repeat for all years in period
				for year in range(start_year, end_year + 1):
					date = str(year) + "-" + dogodek_start
					if (
						getdate(date) >= getdate(start)
						and getdate(date) <= getdate(end)
						and getdate(date) <= getdate(repeat)
					):
						add_dogodek(e, date)

				remove_dogodeks.append(e)

			if e.repeat_on == "Monthly":
				# creates a string with date (27) and month (07) and year (2019) eg: 2019-07-27
				year, month = start.split("-", maxsplit=2)[:2]
				date = f"{year}-{month}-" + dogodek_start.split("-", maxsplit=3)[2]

				# last day of month issue, start from prev month!
				try:
					getdate(date)
				except Exception:
					date = date.split("-")
					date = date[0] + "-" + str(cint(date[1]) - 1) + "-" + date[2]

				start_from = date
				for i in range(int(date_diff(end, start) / 30) + 3):
					if (
						getdate(date) >= getdate(start)
						and getdate(date) <= getdate(end)
						and getdate(date) <= getdate(repeat)
						and getdate(date) >= getdate(dogodek_start)
					):
						add_dogodek(e, date)

					date = add_months(start_from, i + 1)
				remove_dogodeks.append(e)

			if e.repeat_on == "Weekly":
				for cnt in range(date_diff(end, start) + 1):
					date = add_days(start, cnt)
					if (
						getdate(date) >= getdate(start)
						and getdate(date) <= getdate(end)
						and getdate(date) <= getdate(repeat)
						and getdate(date) >= getdate(dogodek_start)
						and e[weekdays[getdate(date).weekday()]]
					):
						add_dogodek(e, date)

				remove_dogodeks.append(e)

			if e.repeat_on == "Daily":
				for cnt in range(date_diff(end, start) + 1):
					date = add_days(start, cnt)
					if (
						getdate(date) >= getdate(dogodek_start)
						and getdate(date) <= getdate(end)
						and getdate(date) <= getdate(repeat)
					):
						add_dogodek(e, date)

				remove_dogodeks.append(e)

	for e in remove_dogodeks:
		dogodeks.remove(e)

	dogodeks = dogodeks + add_dogodeks

	for e in dogodeks:
		# remove weekday properties (to reduce message size)
		for w in weekdays:
			del e[w]

	return dogodeks


def delete_dogodeks(ref_type, ref_name, delete_dogodek=False):
	participations = frappe.get_all(
		"Dogodek Participants",
		filters={"reference_doctype": ref_type, "reference_docname": ref_name, "parenttype": "Dogodek"},
		fields=["parent", "name"],
	)

	if participations:
		for participation in participations:
			if delete_dogodek:
				frappe.delete_doc("Dogodek", participation.parent, for_reload=True)
			else:
				total_participants = frappe.get_all(
					"Dogodek Participants", filters={"parenttype": "Dogodek", "parent": participation.parent}
				)

				if len(total_participants) <= 1:
					frappe.db.delete("Dogodek", {"name": participation.parent})
					frappe.db.delete("Dogodek Participants", {"name": participation.name})


# Close dogodeks if ends_on or repeat_till is less than now_datetime
def set_status_of_dogodeks():
	dogodeks = frappe.get_list("Dogodek", filters={"status": "Open"}, fields=["name", "ends_on", "repeat_till"])
	for dogodek in dogodeks:
		if (dogodek.ends_on and getdate(dogodek.ends_on) < getdate(nowdate())) or (
			dogodek.repeat_till and getdate(dogodek.repeat_till) < getdate(nowdate())
		):
			frappe.db.set_value("Dogodek", dogodek.name, "status", "Closed")
