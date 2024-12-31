import json
from math import ceil

import frappe


def execute():
	layouts = frappe.get_all("CRM Fields Layout", fields=["name", "layout", "type"])

	for layout in layouts:
		old_layout = layout.layout
		new_layout = get_new_layout(old_layout, layout.type)

		frappe.db.set_value("CRM Fields Layout", layout.name, "layout", new_layout)


def get_new_layout(old_layout, type):
	if isinstance(old_layout, str):
		old_layout = json.loads(old_layout)
	new_layout = []
	already_converted = False

	starts_with_sections = False

	if not old_layout[0].get("sections"):
		starts_with_sections = True

	if starts_with_sections:
		old_layout = [{"sections": old_layout}]

	for tab in old_layout:
		new_tab = tab.copy()
		new_tab["sections"] = []
		for section in tab.get("sections"):
			if "contacts" in section:
				new_tab["sections"].append(section)
				continue
			if isinstance(section.get("columns"), list):
				already_converted = True
				break
			column_count = section.get("columns") or 3
			if type == "Side Panel":
				column_count = 1
			fields = section.get("fields") or []

			new_section = section.copy()

			if "fields" in new_section:
				new_section.pop("fields")
			new_section["columns"] = []

			if len(fields) == 0:
				new_section["columns"].append({"fields": []})
				new_tab["sections"].append(new_section)
				continue

			if len(fields) == 1 and column_count > 1:
				new_section["columns"].append({"fields": fields[0]})
				new_section["columns"].append({"fields": []})
				new_tab["sections"].append(new_section)
				continue

			fields_per_column = ceil(len(fields) / column_count)
			for i in range(column_count):
				new_column = {
					"fields": fields[i * fields_per_column: (i + 1) * fields_per_column]
				}
				new_section["columns"].append(new_column)
			new_tab["sections"].append(new_section)
		new_layout.append(new_tab)

	if starts_with_sections:
		new_layout = new_layout[0].get("sections")

	if already_converted:
		return json.dumps(old_layout)
	return json.dumps(new_layout)
