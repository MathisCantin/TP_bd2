import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from interface import Ui_MainWindow
import tkinter as tk
from tkinter import messagebox
import mysql.connector

def dbcon():
    return mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        database='TP_Livre'
    )

def db_query(query, params=None, fetch=True, insert_id=False):
    try:
        connection = dbcon()
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            resultat = cursor.fetchall()
            connection.close()
            return resultat
        elif insert_id:
            connection.commit()
            last_id = cursor.lastrowid
            connection.close()
            return last_id
        else:
            connection.commit()
            connection.close()
    except mysql.connector.Error as error:
        print("Erreur de la bd:", error)
        messagebox.showerror("Error", f"Erreur de la bd: {error}")
        raise

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Assignation des fonctions
        self.selectionLivre()
        self.selected_livre_id = None
        self.selected_chapitre = None
        self.comboBoxLivre.activated.connect(self.chargerLivre)
        self.pushButtonDestination.clicked.connect(self.chargerChapitre)

        self.liste_actuel = None
        self.comboBoxChoixDispo.currentIndexChanged.connect(self.choixChange)
        self.pushButtonAjouter.clicked.connect(self.ajouterAuTableau)
        self.pushButtonEnlever.clicked.connect(self.retirerAuTableau)

        self.pushButtonPlusBourse.clicked.connect(self.retirerBourse)
        self.pushButtonMoinsBourse.clicked.connect(self.ajouterBourse)

        self.pushButtonMoinsHabilete.clicked.connect(self.retirerHabilete)
        self.pushButtonPlusHabilete.clicked.connect(self.ajouterHabilete)

        self.pushButtonMoinsEndurance.clicked.connect(self.retirerEndurance)
        self.pushButtonPlusEndurance.clicked.connect(self.ajouterEndurance)

        self.charger_sauvegarde()
        self.pushButtonSauvegarder.clicked.connect(self.sauvegarder)
        self.pushButtonCharger.clicked.connect(self.charger)
        self.pushButtonSupprimer.clicked.connect(self.supprimer)

        self.table_mapping = {
                "listWidgetDisciplines": ("discipline_kai", "discipline_choix"),
                "listWidgetArmes": ("arme", "arme_choix"),
                "listWidgetObjets": ("objet", None),
                "listWidgetObjetsSpec": ("objet_spec", None),
                "listWidgetRepas": ("repas", None)
            }

    #Charger livre et chapitre
    def selectionLivre(self):
        query = "SELECT titre FROM livre"
        resultat = db_query(query)
        titles = [title[0] for title in resultat]
        self.comboBoxLivre.addItems(titles)


    def chargerLivre(self):
        selected_livre = self.comboBoxLivre.currentText()
        query = "SELECT id, prologue, prologue_texte FROM livre WHERE titre = %s"
        resultat = db_query(query, (selected_livre,))
        
        if resultat:
            id, prologue, prologue_text = resultat[0]

            self.selected_livre_id = id
            self.labelNumChap.setText(f"Prologue: {prologue}")
            self.textEditTexte.setPlainText(prologue_text)

            self.comboBoxDestination.clear()
            self.comboBoxDestination.addItem("1")
        else:
            self.labelNumChap.setText("Prologue: inconnu")
            self.textEditTexte.setPlainText("Le texte du prologue n'a pas été trouver.")


    def chargerChapitre(self, chapitre=False):
        if chapitre is False:
            self.selected_chapitre = self.comboBoxDestination.currentText()
        else:
            self.selected_chapitre = chapitre

        if self.selected_livre_id and self.selected_chapitre != "":
            query_chapitre = "SELECT texte FROM chapitre WHERE id_livre = %s AND no_chapitre = %s"
            chapitre_text = db_query(query_chapitre, (self.selected_livre_id, self.selected_chapitre,))
            
            self.labelNumChap.setText(f"Chapter: {self.selected_chapitre}")

            if chapitre_text:
                self.textEditTexte.setPlainText(chapitre_text[0][0])

            self.chapitreChoix(self.selected_chapitre)

    def chapitreChoix(self, selected_chapitre):
        query_chapitre_lien = "SELECT no_chapitre_destination FROM lien_chapitre " \
                              "INNER JOIN chapitre ON lien_chapitre.no_chapitre_origine = chapitre.id " \
                              "WHERE lien_chapitre.no_chapitre_origine = %s AND chapitre.id_livre = %s"
        
        chapitre_lien = db_query(query_chapitre_lien, (selected_chapitre, self.selected_livre_id))

        self.comboBoxDestination.clear()
        if chapitre_lien:
            chapitres = [str(chapitre[0]) for chapitre in chapitre_lien]
            self.comboBoxDestination.addItems(chapitres)

    #Gestion fiche du personnage
    def ajouterAuTableau(self):
        if self.liste_actuel is not None:
            element = self.lineEditNomObjet.text()

            if element == "":
                element = self.comboBoxAjouter.currentText()

            existe = False
            for index in range(self.liste_actuel.count()):
                if self.liste_actuel.item(index).text() == element:
                    existe = True
                    break

            if not existe:
                self.liste_actuel.addItem(element)

    def retirerAuTableau(self):
        if self.liste_actuel:
            current_row = self.liste_actuel.currentRow()
            if current_row >= 0:
                self.liste_actuel.takeItem(current_row)

    def choixChange(self):
        self.lineEditNomObjet.setText("")
        self.comboBoxAjouter.clear()

        choix = self.comboBoxChoixDispo.currentText()

        queries = {
            "Disciplines": "SELECT titre FROM discipline_choix",
            "Armes": "SELECT titre FROM arme_choix"
        }

        query = queries.get(choix)

        if query:
            resultats = db_query(query)
            if resultats:
                titles = [resultat[0] for resultat in resultats]
                self.comboBoxAjouter.addItems(titles)

        list_widgets = {
            "Disciplines": self.listWidgetDisciplines,
            "Armes": self.listWidgetArmes,
            "Objets": self.listWidgetObjets,
            "Objets Spéc.": self.listWidgetObjetsSpec,
            "Repas": self.listWidgetRepas
        }

        if choix in list_widgets:
            self.liste_actuel = list_widgets[choix]
        else:
            self.liste_actuel = None

        visible = choix in ["Disciplines", "Armes"]
        self.comboBoxAjouter.setVisible(visible)
        self.lineEditNomObjet.setVisible(not visible)

    #Bourse, habilete et endurance
    def retirerBourse(self):
        nombre = int(self.labelBourse.text().split(': ')[1])
        texte = f'Bourse: {nombre + 1}'
        self.labelBourse.setText(texte)

    def ajouterBourse(self):
        nombre = int(self.labelBourse.text().split(': ')[1])
        if nombre > 0:
            texte = f'Bourse: {nombre - 1}'
            self.labelBourse.setText(texte)

    def retirerHabilete(self):
        nombre = int(self.labelHabilete.text().split(': ')[1])
        if nombre > 0:
            texte = f'Habilete: {nombre - 1}'
            self.labelHabilete.setText(texte)

    def ajouterHabilete(self):
        nombre = int(self.labelHabilete.text().split(': ')[1])
        texte = f'Habilete: {nombre + 1}'
        self.labelHabilete.setText(texte)

    def retirerEndurance(self):
        nombre = int(self.labelEndurance.text().split(': ')[1])
        if nombre > 0:
            texte = f'Endurance: {nombre - 1}'
            self.labelEndurance.setText(texte)

    def ajouterEndurance(self):
        nombre = int(self.labelEndurance.text().split(': ')[1])
        texte = f'Endurance: {nombre + 1}'
        self.labelEndurance.setText(texte)

    #Systeme de sauvegarde
    def charger_sauvegarde(self):
        try:
            query = "SELECT titre FROM sauvegarde"
            resultats = db_query(query)
            self.comboBoxCharger.clear()
            self.comboBoxCharger.addItem("Sélectionner sauvegarde")
            if resultats:
                titre = [resultat[0] for resultat in resultats]
                self.comboBoxCharger.addItems(titre)
        except Exception as e:
            print("Erreur de chargement des sauvegardes:", e)
            messagebox.showerror("Error", f"Erreur de chargement des sauvegardes: {e}")

    def sauvegarder(self):
        try:
            titre = self.lineEditNomSauvegarde.text()
            if titre:
                query_sauvegarde = "SELECT id, id_fiche_personnage FROM sauvegarde WHERE titre = %s"
                sauvegarde = db_query(query_sauvegarde, (titre,))

                if sauvegarde:
                    sauvegarde_id, fiche_perso_id = sauvegarde[0]

                    self.delete_inventaire(fiche_perso_id)
                    self.update_fiche_personnage(fiche_perso_id)
                else:
                    fiche_perso_id = self.insert_fiche_personnage()

                self.save_inventaire(fiche_perso_id)

                if sauvegarde:
                    query_update = "UPDATE sauvegarde SET id_chapitre = %s, id_fiche_personnage = %s WHERE id = %s"
                    db_query(query_update, (self.selected_chapitre, fiche_perso_id, sauvegarde_id), fetch=False)
                else:
                    query_insert = "INSERT INTO sauvegarde (titre, id_chapitre, id_fiche_personnage) VALUES (%s, %s, %s)"
                    db_query(query_insert, (titre, self.selected_chapitre, fiche_perso_id), fetch=False)

                self.charger_sauvegarde()
        except Exception as e:
            print("Erreur de sauvegarde: ", e)
            messagebox.showerror("Error", f"Erreur de sauvegarde: {e}")

    def delete_inventaire(self, fiche_perso_id):
        tables_to_clear = ['discipline_kai', 'arme', 'objet', 'objet_spec', 'repas']
        for table in tables_to_clear:
            query = f"DELETE FROM {table} WHERE id_fiche_personnage = %s"
            params = (fiche_perso_id,)
            db_query(query, params, fetch=False)

    def update_fiche_personnage(self, fiche_perso_id):
        bourse, habilete, endurance = self.bourseHabileteEndurance()

        query = "UPDATE fiche_personnage SET bourse = %s, habilete = %s, endurance = %s WHERE id = %s"
        params = (bourse, habilete, endurance, fiche_perso_id)
        db_query(query, params, fetch=False)


    def insert_fiche_personnage(self):
        bourse, habilete, endurance = self.bourseHabileteEndurance()
        
        query = "INSERT INTO fiche_personnage (bourse, habilete, endurance) VALUES (%s, %s, %s)"
        params = (bourse, habilete, endurance)
        last_insert_id = db_query(query, params, fetch=False, insert_id=True)
        return last_insert_id

    def bourseHabileteEndurance(self):
        bourse = int(self.labelBourse.text().split(': ')[1])
        habilete = int(self.labelHabilete.text().split(': ')[1])
        endurance = int(self.labelEndurance.text().split(': ')[1])
        return bourse, habilete, endurance

    def save_inventaire(self, fiche_perso_id):
        for nom_liste, mapping in self.table_mapping.items():
            nom_table, fk_table = mapping
            liste_actuel = getattr(self, nom_liste)
            elements_liste_actuel = [liste_actuel.item(i).text() for i in range(liste_actuel.count())]

            for element in elements_liste_actuel:
                if fk_table:
                    id_query = f"SELECT id FROM {fk_table} WHERE titre = %s"
                    adjusted_fk_table = fk_table  # Store the original table name
                    element_id = db_query(id_query, (element,))
                    
                    if element_id:
                        element = element_id[0][0]
                        adjusted_fk_table = adjusted_fk_table.replace("_choix", "")

                        query = f"INSERT INTO {nom_table} (id_{adjusted_fk_table}, id_fiche_personnage) VALUES (%s, %s)"
                        params = (element, fiche_perso_id)
                        db_query(query, params, fetch=False)
                else:
                    query = f"INSERT INTO {nom_table} (nom, id_fiche_personnage) VALUES (%s, %s)"
                    params = (element, fiche_perso_id)
                    db_query(query, params, fetch=False)

    def charger(self):
        try:
            sauvegarde_titre = self.comboBoxCharger.currentText()

            if sauvegarde_titre:
                query_sauvegarde = "SELECT id_fiche_personnage, no_chapitre, livre.titre FROM sauvegarde INNER JOIN chapitre ON chapitre.id = id_chapitre INNER JOIN livre ON livre.id = id_livre WHERE sauvegarde.titre = %s"
                resultat = db_query(query_sauvegarde, (sauvegarde_titre,))
                if resultat:
                    fiche_perso_id, no_chapitre, titre = resultat[0]

                    self.chargerStats(fiche_perso_id)
                    self.charger_inventaire(fiche_perso_id)

                    self.comboBoxLivre.setCurrentText(titre)
                    self.chargerLivre()

                    self.comboBoxDestination.setCurrentText(str(no_chapitre))
                    self.chargerChapitre(str(no_chapitre))
        except Exception as e:
            print("Erreur du chargement de la sauvegarde:", e)
            messagebox.showerror("Error", f"Erreur du chargement de la sauvegarde: {e}")

    def chargerStats(self, fiche_perso_id):
        query = "SELECT bourse, endurance, habilete FROM fiche_personnage WHERE id = %s"
        character_data = db_query(query, (fiche_perso_id,))
        if character_data:
            bourse, endurance, habilete = character_data[0]

            self.labelBourse.setText(f"Bourse: {int(bourse)}")
            self.labelEndurance.setText(f"Endurance: {int(endurance)}")
            self.labelHabilete.setText(f"Habilité: {int(habilete)}")

    def charger_inventaire(self, fiche_perso_id):
        try:
            for nom_liste, (nom_table, fk_table) in self.table_mapping.items():
                liste_actuel = getattr(self, nom_liste)
                items_query = f"SELECT nom FROM {nom_table} WHERE id_fiche_personnage = %s"
                
                if fk_table:
                    adjusted_fk_table = fk_table.replace("_choix", "")
                    items_query = f"SELECT titre FROM {nom_table} t1 JOIN {fk_table} t2 ON t1.id_{adjusted_fk_table} = t2.id WHERE t1.id_fiche_personnage = %s"
                
                items = db_query(items_query, (fiche_perso_id,))
                
                liste_actuel.clear()
                for item in items:
                    liste_actuel.addItem(item[0])
        except Exception as e:
            print("Erreur du chargement de l'inventaire:", e)
            messagebox.showerror("Error", f"Erreur du chargement de l'inventaire: {e}")

    def supprimer(self):
        try:
            sauvegarde_titre = self.comboBoxCharger.currentText()
            if sauvegarde_titre:
                query_sauvegarde = "SELECT id_fiche_personnage FROM sauvegarde WHERE sauvegarde.titre = %s"
                resultat = db_query(query_sauvegarde, (sauvegarde_titre,))

                if resultat:
                    fiche_perso_id = resultat[0][0]

                    query_delete_sauvegarde = "DELETE FROM sauvegarde WHERE id_fiche_personnage = %s"
                    db_query(query_delete_sauvegarde, (fiche_perso_id,), fetch=False)

                    query_delete_fiche = "DELETE FROM fiche_personnage WHERE id = %s"
                    db_query(query_delete_fiche, (fiche_perso_id,), fetch=False)

                    self.charger_sauvegarde()
        except mysql.connector.Error as error:
            print("Erreur lors de la suppression:", error)
            messagebox.showerror("Error", f"Erreur lors de la suppression: {error}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
