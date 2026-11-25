import yaml
import os

config_path = r"C:\Users\rudel\.gemini\antigravity\scratch\dsdb-er-diagram\super-er-diagram.config.yaml"

with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Define domains
domains = {
    "organizations": {
        "name": "Organisations & Adhésion",
        "short": "ORGA",
        "color": "#2563eb"
    },
    "persons": {
        "name": "Personnes & Délégations",
        "short": "PERS",
        "color": "#7c3aed"
    },
    "technical_bodies": {
        "name": "Organes Techniques (TBs)",
        "short": "TB",
        "color": "#059669"
    },
    "meetings": {
        "name": "Réunions & Événements",
        "short": "MTG",
        "color": "#d97706"
    },
    "work_programme": {
        "name": "Programme de Normalisation (WPM)",
        "short": "WPM",
        "color": "#dc2626"
    },
    "referentials": {
        "name": "Référentiels & Nomenclatures",
        "short": "REF",
        "color": "#4b5563",
        "neutral": True
    },
    "audit_logs": {
        "name": "Historique & Logs d'Audit",
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

# Domain classification rules
def classify_table(name, role_guess):
    n = name.upper()
    
    # 1. Audit & Logs
    if "LOG" in n or "HISTORY" in n or "DELETE" in n or "HIST" in n or n.startswith("OLD"):
        desc = f"Journal d'audit et historique pour {name.replace('_LOGS','').replace('__LOGS','').replace('_HISTORY','')}"
        return "audit_logs", "log", desc
        
    # 2. Work Programme
    if n in ["WORK_ITEM", "CONTRIBUTION_NOTIFICATION"] or "DELIV" in n or "WKI" in n:
        if n == "WORK_ITEM":
            return "work_programme", "hub", "Spécifications et normes techniques (TS, TR, EN, ES, GS)"
        return "work_programme", "tx", "Notification et soumission de contributions techniques"

    # 3. Technical Bodies
    if n.startswith("BODY") or n.startswith("TB_") or n in ["BODIESMEETINGTYPES"]:
        if n == "BODY":
            return "technical_bodies", "hub", "Comités techniques, groupes de travail et partenariats (TBs, WGs, ISGs)"
        elif n in ["BODYFAMILY", "BODYTYPE", "BODYSTATE"]:
            return "technical_bodies", "master", f"Nomenclature de classification des organes: {name}"
        elif n in ["TB_DESCENDANT", "TB_MEETING_PROFILE"]:
            return "technical_bodies", "child", f"Hiérarchie ou profil d'organe technique: {name}"
        elif n in ["BODYTYPEFAMILY", "BODIESMEETINGTYPES"]:
            return "technical_bodies", "join", f"Association de typologie d'organe: {name}"
        return "technical_bodies", "child", f"Paramètres de l'organe technique: {name}"

    # 4. Meetings & Events
    if n.startswith("MEETING") or n.startswith("MTG_") or n.startswith("ROOM") or n in ["EVENTS", "ATTENDANCE_GROUP_FEE", "REG_NOT_CONFIRMED"]:
        if n == "MEETINGS":
            return "meetings", "hub", "Sessions, assemblées générales et réunions de travail"
        elif n == "MTG_USERS_PRESENCE":
            return "meetings", "tx", "Émargement, présence physique et distancielle des délégués"
        elif n == "MTG_USERS_PRESENCE_REP_ORGS_STATUS":
            return "meetings", "child", "Calcul des droits de représentation et quorum de séance"
        elif n.startswith("ROOM_REQUEST"):
            return "meetings", "tx", "Réservations logistiques des salles et équipements"
        elif n in ["ROOM", "ROOM_LAYOUT"]:
            return "meetings", "master", "Référentiel des salles et configurations de réunion"
        elif n in ["MEETING_TB", "MEETING_PT", "MEETING_RESPONSIBLE", "MTG_CONTACT"]:
            return "meetings", "join", f"Liaison meeting / ressource: {name}"
        elif n == "EVENTS":
            return "meetings", "hub", "Événements institutionnels majeurs et ateliers"
        return "meetings", "child", f"Détail de gestion des réunions: {name}"

    # 5. Persons & Contacts
    if n.startswith("PERSON") or n.startswith("PERS_") or n in ["TELDIR", "MERGED_PERSON"]:
        if n == "PERSON":
            return "persons", "hub", "Délégués, représentants d'adhérents, présidents et experts"
        elif n == "PERSON_IN_LIST":
            return "persons", "join", "Inscriptions aux listes de diffusion et collèges de comités"
        elif n in ["PERSON_LIST", "PERSON_GROUP"]:
            return "persons", "master", "Listes de distribution et groupes de contacts"
        elif n == "PERSON_PRIVACY":
            return "persons", "child", "Préférences de confidentialité et consentement RGPD"
        return "persons", "child", f"Données complémentaires sur les personnes: {name}"

    # 6. Organizations
    if n.startswith("ORGA") or n.startswith("ORGANISATION") or n.startswith("SAGE") or n in ["EMAIL_DOMAIN_NAME", "EXCESS_CONTRIBUTION", "WITHDRAWAL_REQUESTS", "SHARING_DATA"]:
        if n == "ORGANISATION":
            return "organizations", "hub", "Membres, entreprises, universités et partenaires de l'ETSI"
        elif n == "ORGA_STATUS":
            return "organizations", "tx", "Statut d'adhésion officiel, catégorie, classe contributive et droits de vote"
        elif n == "ORGANISATION_ADDRESS":
            return "organizations", "child", "Adresses postales, sièges sociaux et adresses de facturation"
        elif n in ["ORGANISATION_PERSON_CONTACT", "PERSON_REPRESENTING_ORGANISATION"]:
            return "organizations", "join", "Mandats de représentation et contacts officiels d'organisations"
        elif n == "ORGA_DECLARATION":
            return "organizations", "tx", "Déclarations de chiffre d'affaires (ECRT) pour le calcul de cotisation"
        elif n in ["ORGANISATION_CORPORATE_OP", "TAB_CORPORATE_OP"]:
            return "organizations", "child", "Liaison groupes d'entreprises et partenaires organisationnels (OP)"
        elif n.startswith("SAGE"):
            return "organizations", "child", "Données d'interfaçage comptable et facturation Sage"
        elif n in ["ORGA_IN_LIST", "ORGA_LIST"]:
            return "organizations", "join", "Rattachement d'organisations à des listes institutionnelles"
        return "organizations", "child", f"Données d'adhésion de l'organisation: {name}"

    # 7. Reference Data / Taxonomies (TAB_*)
    if n.startswith("TAB_") or n.startswith("TAB") or n in ["CALENDAR", "COMMON_FIELD", "VATVALIDATIONMASK"]:
        if n == "TAB_COUNTRY":
            desc = "Référentiel des pays ISO, régions, appartenance UE / CEPT / EFTA"
        elif n == "TAB_BUILDING":
            desc = "Bâtiments du campus ETSI (Sophia Antipolis)"
        elif n == "TAB_CONTACT_TYPE":
            desc = "Types de contacts (Officiel, Vote, Finance)"
        elif n == "TAB_UOC":
            desc = "Barème financier des Unités de Cotisation (UoC)"
        else:
            desc = f"Nomenclature de référence: {name}"
        return "referentials", "master", desc

    # Default
    return "referentials", role_guess or "master", f"Table de référence ou support: {name}"

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

print("Updated super-er-diagram.config.yaml with 7 domains, roles, and French descriptions.")
