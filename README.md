# ETSI DSDB — Data Model & Interactive ER Diagram

Modèle de données complet et visualiseur relationnel interactif à deux couches pour la base de données **DSDB** (*Directory Services Database*) d'ETSI, généré à l'aide de **`super-er-diagram`**.

🌐 **Visualiseur en ligne** : [https://tnm.etsi.org/DSDB_scheme/](https://tnm.etsi.org/DSDB_scheme/)

---

## 📊 Métriques du Schéma

* **Tables analysées** : 208 tables
* **Relations de clés étrangères (FK)** : 128
* **Domaines métier modélisés** : 7
* **Moteur de base de données source** : Microsoft SQL Server (172.27.2.40)
* **Système de visualisation** : Canvas SVG interactif + Panneau d'inspection détaillée

---

## 🏛️ Les 7 Domaines Métier

1. **`organizations` — Organisations & Adhésion (Bleu)** : Membres, catégories d'adhésion, déclarations financières (ECRT), classes de cotisation (UoC), adresses multiples et contacts officiels.
   * *Tables clés* : `ORGANISATION`, `Orga_Status`, `Organisation_Address`, `Organisation_Person_Contact`, `Orga_Declaration`, `Organisation_Corporate_OP`.
2. **`persons` — Personnes & Délégations (Violet)** : Délégués, experts, présidents, mandats de représentation et inscriptions aux comités.
   * *Tables clés* : `PERSON`, `PERSON_IN_LIST`, `PERSON_LIST`, `Person_Representing_Organisation`, `PERSON_PRIVACY`.
3. **`technical_bodies` — Organes Techniques (Émeraude)** : Comités techniques (TC), sous-comités (SC), groupes de travail (WG) et groupes de spécification industrielle (ISG).
   * *Tables clés* : `Body` / `TAB_TB`, `BodyFamily`, `BodyType`, `BodyState`, `TB_DESCENDANT`.
4. **`meetings` — Réunions & Événements (Ambre)** : Assemblées générales, sessions de travail physiques/hybrides, feuilles de présence et quorum de vote.
   * *Tables clés* : `MEETINGS`, `MTG_USERS_PRESENCE`, `MTG_USERS_PRESENCE_REP_ORGS_STATUS`, `ROOM_REQUEST`.
5. **`work_programme` — Programme de Normalisation (Rouge)** : Normes et spécifications (TS, TR, EN, ES, GS) et contributions documentaires.
   * *Tables clés* : `WORK_ITEM`, `Contribution_Notification`.
6. **`referentials` — Référentiels & Nomenclatures (Gris)** : Codes pays ISO, bâtiments du campus ETSI, types de contacts, barèmes UoC.
   * *Tables clés* : `TAB_COUNTRY`, `TAB_BUILDING`, `TAB_CONTACT_TYPE`, `Tab_UoC`.
7. **`audit_logs` — Historique & Traçabilité (Ardoise)** : Journaux d'audit et historiques de modifications.

---

## 🚀 Utilisation Locale

### Lancement direct
* Sous Windows : Double-cliquez sur `Lancer_Modele_DSDB.bat`
* Ou ouvrez directement `viewer/index.html` dans votre navigateur.

### Via serveur local HTTP
```bash
cd viewer
python -m http.server 8085
```
Accédez ensuite à [http://localhost:8085](http://localhost:8085).

---

## 🔄 Mise à jour du Modèle

```bash
# 1. Extraire le snapshot du schéma depuis SQL Server
python build_schema.py

# 2. Enrichir et appliquer la configuration métier
python enrich_config.py

# 3. Régénérer le visualiseur web
super-er-diagram generate --from-json schema.json --out viewer
```
