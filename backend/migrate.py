import sqlite3

DB_PATH = "database/alsamadiya.db"


def ajouter_colonnes_annonces():

    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    # Colonnes actuellement présentes
    colonnes = {
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(annonces)"
        ).fetchall()
    }

    # Colonnes nécessaires à AL SAMADIYA IMMO PRO
    colonnes_a_ajouter = {

        "titre": "TEXT",
        "description": "TEXT",
        "categorie": "TEXT",
        "type_transaction": "TEXT",

        "prix": "REAL",
        "superficie": "REAL",
        "surface": "REAL",

        "region": "TEXT",
        "ville": "TEXT",
        "quartier": "TEXT",
        "localisation": "TEXT",
        "adresse": "TEXT",

        "latitude": "REAL",
        "longitude": "REAL",

        "nombre_chambres": "INTEGER",
        "nombre_salles_bain": "INTEGER",

        "meuble": "BOOLEAN",

        "telephone": "TEXT",
        "whatsapp": "TEXT",
        "email": "TEXT",

        "vues": "INTEGER DEFAULT 0",

        "premium": "BOOLEAN DEFAULT 0",

        "statut": "TEXT DEFAULT 'brouillon'",

        "paiement_confirme": "BOOLEAN DEFAULT 0",

        "date_creation": "DATETIME"
    }

    print("\n======================================")
    print(" MIGRATION AL SAMADIYA IMMO PRO")
    print("======================================\n")

    for nom_colonne, type_colonne in colonnes_a_ajouter.items():

        if nom_colonne not in colonnes:

            sql = (
                f"ALTER TABLE annonces "
                f"ADD COLUMN {nom_colonne} {type_colonne}"
            )

            try:
                cursor.execute(sql)
                print(f"[OK] Colonne ajoutée : {nom_colonne}")

            except sqlite3.OperationalError as erreur:
                print(
                    f"[ERREUR] {nom_colonne} : {erreur}"
                )

        else:
            print(f"[EXISTE] {nom_colonne}")

    db.commit()

    print("\n--------------------------------------")
    print("VERIFICATION DE LA TABLE ANNONCES")
    print("--------------------------------------")

    colonnes_finales = cursor.execute(
        "PRAGMA table_info(annonces)"
    ).fetchall()

    for colonne in colonnes_finales:
        print(
            f"- {colonne[1]} "
            f"({colonne[2]})"
        )

    db.close()

    print("\n======================================")
    print(" MIGRATION TERMINEE")
    print("======================================\n")


def creer_table_paiements():

    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paiements (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            utilisateur_id INTEGER NOT NULL,

            annonce_id INTEGER NOT NULL,

            montant REAL NOT NULL,

            operateur TEXT NOT NULL,

            reference TEXT UNIQUE NOT NULL,

            transaction_id TEXT,

            statut TEXT NOT NULL DEFAULT 'en_attente',

            mode_test BOOLEAN DEFAULT 1,

            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,

            date_confirmation DATETIME,

            FOREIGN KEY(utilisateur_id)
                REFERENCES utilisateurs(id),

            FOREIGN KEY(annonce_id)
                REFERENCES annonces(id)
        )
    """)

    db.commit()

    print("[OK] Table paiements vérifiée/créée.")

    db.close()


if __name__ == "__main__":

    ajouter_colonnes_annonces()

    creer_table_paiements()

    print("\nBASE DE DONNEES PRETE.")