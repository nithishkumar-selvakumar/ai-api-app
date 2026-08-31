- uv run python -m uvicorn main:app --reload
- uv add -r requirements.txt
- ollama list

## Files API

- `POST /api/files/upload` uploads multipart files with a `project_name` field.
- `GET /api/files/upload/{project_name}` lists the files uploaded for a project.
- `GET /api/files/upload/{project_name}/{filename}` downloads one file.

{
"email": {
"subject": "A data loss on the BFE side was reported to me following a CACID Transfer on AIB*AT Project, Program L",
"summary": {
"short_description": "A data loss on the BFE side was reported to me following a CACID Transfer on AIB*AT Project, Program L.",
"description": "Hello. A data loss on the BFE side was reported to me following a CACID transfer on the AIB\*AT project (Program L). When I checked the logs, there was no record of a CACID transfer being performed, and MSN 2140 was only updated from 'Rebuilt' to 'HoV' today. There are no other traces in the logs. However, the BFE manager confirms that a CACID transfer was executed and that this MSN was already set to 'HoV' prior to today. Could you please investigate this issue and, if possible, recover the missing data? Thank you"
},
"assignment_group": "AC_PROGRAMMES_INC_RG_MYFCO-IM_L3",
"state": "New",
"priority": {
"value": 4,
"label": "Low"
},
"requested_for": {
"name": "Cristina Raluca DELPECH",
"email": "cristina.c.delpech@airbus.com",
"country": "France"
},
"service": "myFCO",
"id": "AC_BS_PM00",
"service_offering": "MyFCO - Fleet management",
"base_item": null,
"category": "Data issue"
}
}
