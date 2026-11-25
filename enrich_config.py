import yaml
import os

config_path = r"C:\Users\rudel\.gemini\antigravity\scratch\dsdb-er-diagram\super-er-diagram.config.yaml"

with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Define domains in English
domains = {
    "organizations": {
        "name": "Organizations & Membership",
        "short": "ORGA",
        "color": "#2563eb"
    },
    "persons": {
        "name": "Persons & Delegations",
        "short": "PERS",
        "color": "#7c3aed"
    },
    "technical_bodies": {
        "name": "Technical Bodies (TBs)",
        "short": "TB",
        "color": "#059669"
    },
    "meetings": {
        "name": "Meetings & Events",
        "short": "MTG",
        "color": "#d97706"
    },
    "work_programme": {
        "name": "Work Programme (WPM)",
        "short": "WPM",
        "color": "#dc2626"
    },
    "referentials": {
        "name": "Reference Data & Taxonomies",
        "short": "REF",
        "color": "#4b5563",
        "neutral": True
    },
    "audit_logs": {
        "name": "Audit Logs & History",
        "short": "LOG",
        "color": "#64748b",
        "neutral": True
    }
}

config["title"] = "ETSI DSDB — Directory Services Database"
config["domains"] = domains
config["columns"] = [
    ["organizations", "persons"],
    ["technical_bodies", "meetings"],
    ["work_programme", "referentials", "audit_logs"]
]
config["hiddenFkColumns"] = []

# Domain classification rules in English
def classify_table(name, role_guess):
    n = name.upper()
    
    # 1. Audit & Logs
    if "LOG" in n or "HISTORY" in n or "DELETE" in n or "HIST" in n or n.startswith("OLD"):
        desc = f"Audit log and change history for {name.replace('_LOGS','').replace('__LOGS','').replace('_HISTORY','')}"
        return "audit_logs", "log", desc
        
    # 2. Work Programme
    if n in ["WORK_ITEM", "CONTRIBUTION_NOTIFICATION"] or "DELIV" in n or "WKI" in n:
        if n == "WORK_ITEM":
            return "work_programme", "hub", "Technical specifications and European standards (TS, TR, EN, ES, GS)"
        return "work_programme", "tx", "Technical contribution notification and upload records"

    # 3. Technical Bodies
    if n.startswith("BODY") or n.startswith("TB_") or n in ["BODIESMEETINGTYPES"]:
        if n == "BODY":
            return "technical_bodies", "hub", "Technical committees, working groups, task forces and ISGs"
        elif n in ["BODYFAMILY", "BODYTYPE", "BODYSTATE"]:
            return "technical_bodies", "master", f"Classification taxonomy for technical bodies: {name}"
        elif n in ["TB_DESCENDANT", "TB_MEETING_PROFILE"]:
            return "technical_bodies", "child", f"Technical body hierarchy tree or profile: {name}"
        elif n in ["BODYTYPEFAMILY", "BODIESMEETINGTYPES"]:
            return "technical_bodies", "join", f"Body type mapping and meeting association: {name}"
        return "technical_bodies", "child", f"Technical body parameters: {name}"

    # 4. Meetings & Events
    if n.startswith("MEETING") or n.startswith("MTG_") or n.startswith("ROOM") or n in ["EVENTS", "ATTENDANCE_GROUP_FEE", "REG_NOT_CONFIRMED"]:
        if n == "MEETINGS":
            return "meetings", "hub", "General Assemblies, technical committee sessions and hybrid meetings"
        elif n == "MTG_USERS_PRESENCE":
            return "meetings", "tx", "Participant presence records and check-ins"
        elif n == "MTG_USERS_PRESENCE_REP_ORGS_STATUS":
            return "meetings", "child", "Representation rights and quorum computation for voting sessions"
        elif n.startswith("ROOM_REQUEST"):
            return "meetings", "tx", "Meeting room bookings and technical equipment logistics"
        elif n in ["ROOM", "ROOM_LAYOUT"]:
            return "meetings", "master", "Room inventory and layout configurations"
        elif n in ["MEETING_TB", "MEETING_PT", "MEETING_RESPONSIBLE", "MTG_CONTACT"]:
            return "meetings", "join", f"Meeting to technical committee/resource mapping: {name}"
        elif n == "EVENTS":
            return "meetings", "hub", "Major corporate events and workshops"
        return "meetings", "child", f"Meeting logistics details: {name}"

    # 5. Persons & Contacts
    if n.startswith("PERSON") or n.startswith("PERS_") or n in ["TELDIR", "MERGED_PERSON"]:
        if n == "PERSON":
            return "persons", "hub", "Delegates, member representatives, committee chairs and technical experts"
        elif n == "PERSON_IN_LIST":
            return "persons", "join", "Subscriptions to technical body rosters and distribution lists"
        elif n in ["PERSON_LIST", "PERSON_GROUP"]:
            return "persons", "master", "Distribution lists and expert roster definitions"
        elif n == "PERSON_PRIVACY":
            return "persons", "child", "GDPR privacy preferences and consents"
        return "persons", "child", f"Person profile metadata: {name}"

    # 6. Organizations
    if n.startswith("ORGA") or n.startswith("ORGANISATION") or n.startswith("SAGE") or n in ["EMAIL_DOMAIN_NAME", "EXCESS_CONTRIBUTION", "WITHDRAWAL_REQUESTS", "SHARING_DATA"]:
        if n == "ORGANISATION":
            return "organizations", "hub", "Member companies, universities, public authorities and partners"
        elif n == "ORGA_STATUS":
            return "organizations", "tx", "Official membership status, category, contribution units (UoC) and voting weights"
        elif n == "ORGANISATION_ADDRESS":
            return "organizations", "child", "Headquarters, billing (Sage) and shipping postal addresses"
        elif n in ["ORGANISATION_PERSON_CONTACT", "PERSON_REPRESENTING_ORGANISATION"]:
            return "organizations", "join", "Official contact roles and accredited delegate representation mandates"
        elif n == "ORGA_DECLARATION":
            return "organizations", "tx", "Turnover declarations (ECRT) used to calculate annual contribution fee"
        elif n in ["ORGANISATION_CORPORATE_OP", "TAB_CORPORATE_OP"]:
            return "organizations", "child", "Corporate groups and Organizational Partners (ARIB, ATIS, CCSA, TTA, TTC)"
        elif n.startswith("SAGE"):
            return "organizations", "child", "Sage accounting and billing integration"
        elif n in ["ORGA_IN_LIST", "ORGA_LIST"]:
            return "organizations", "join", "Organization roster and committee list memberships"
        return "organizations", "child", f"Organization membership details: {name}"

    # 7. Reference Data / Taxonomies (TAB_*)
    if n.startswith("TAB_") or n.startswith("TAB") or n in ["CALENDAR", "COMMON_FIELD", "VATVALIDATIONMASK"]:
        if n == "TAB_COUNTRY":
            desc = "ISO country codes, regions, EU / CEPT / EFTA membership flags"
        elif n == "TAB_BUILDING":
            desc = "ETSI campus buildings (Sophia Antipolis)"
        elif n == "TAB_CONTACT_TYPE":
            desc = "Official contact types (Official, Voting, Billing)"
        elif n == "TAB_UOC":
            desc = "Unit of Contribution (UoC) financial fee scale"
        else:
            desc = f"Reference taxonomy: {name}"
        return "referentials", "master", desc

    return "referentials", role_guess or "master", f"Reference lookup table: {name}"

# Apply classification to all tables
for tname, tinfo in config.get("tables", {}).items():
    current_role = tinfo.get("role", "master")
    dom, role, desc = classify_table(tname, current_role)
    tinfo["domain"] = dom
    tinfo["role"] = role
    tinfo["description"] = desc
    tinfo["label"] = tname

# Save updated config
with open(config_path, "w", encoding="utf-8") as f:
    yaml.dump(config, f, allow_unicode=True, sort_keys=False)

print("Updated DSDB super-er-diagram.config.yaml with English domains, roles, and descriptions.")
