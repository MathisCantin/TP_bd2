DROP DATABASE IF EXISTS TP_Livre;
CREATE DATABASE TP_Livre;
USE TP_Livre;

DROP TABLE IF EXISTS livre;
CREATE TABLE livre (
	id INT PRIMARY KEY AUTO_INCREMENT,
	titre VARCHAR(30),
	prologue VARCHAR(30),
	prologue_texte TEXT
);

#changer le DEFAULT 1 si l'on veut ajouter d'autres livres que un
DROP TABLE IF EXISTS chapitre;
CREATE TABLE chapitre (
	id INT PRIMARY KEY AUTO_INCREMENT,
	no_chapitre INT,
	texte TEXT,
	id_livre INT DEFAULT 1,
    FOREIGN KEY (id_livre) REFERENCES livre(id)
);

DROP TABLE IF EXISTS lien_chapitre;
CREATE TABLE lien_chapitre (
    no_chapitre_origine INT,
    no_chapitre_destination INT,
    PRIMARY KEY (no_chapitre_origine, no_chapitre_destination),
    FOREIGN KEY (no_chapitre_origine) REFERENCES chapitre(id),
    FOREIGN KEY (no_chapitre_destination) REFERENCES chapitre(id)
);

DROP TABLE IF EXISTS fiche_personnage;
CREATE TABLE fiche_personnage (
	id INT PRIMARY KEY AUTO_INCREMENT,
	bourse FLOAT,
	habilete INT,
	endurance INT
);

DROP TABLE IF EXISTS discipline_choix;
CREATE TABLE discipline_choix (
	id INT PRIMARY KEY AUTO_INCREMENT,
	titre VARCHAR(30)
);

DROP TABLE IF EXISTS discipline_kai;
CREATE TABLE discipline_kai (
	id_discipline INT,
	id_fiche_personnage INT NOT NULL,
	PRIMARY KEY (id_discipline, id_fiche_personnage),
    FOREIGN KEY (id_discipline) REFERENCES discipline_choix(id),
    FOREIGN KEY (id_fiche_personnage) REFERENCES fiche_personnage(id)
);

DROP TABLE IF EXISTS arme_choix;
CREATE TABLE arme_choix (
	id INT PRIMARY KEY AUTO_INCREMENT,
	titre VARCHAR(30)
);

DROP TABLE IF EXISTS arme;
CREATE TABLE arme (
	id_arme INT,
	id_fiche_personnage INT NOT NULL,
	PRIMARY KEY (id_arme, id_fiche_personnage),
    FOREIGN KEY (id_arme) REFERENCES arme_choix(id),
    FOREIGN KEY (id_fiche_personnage) REFERENCES fiche_personnage(id)
);

DROP TABLE IF EXISTS objet;
CREATE TABLE objet (
	id INT PRIMARY KEY AUTO_INCREMENT,
	nom VARCHAR(30),
	id_fiche_personnage INT NOT NULL,
    FOREIGN KEY (id_fiche_personnage) REFERENCES fiche_personnage(id)
);

DROP TABLE IF EXISTS objet_spec;
CREATE TABLE objet_spec (
	id INT PRIMARY KEY AUTO_INCREMENT,
	nom VARCHAR(30),
	id_fiche_personnage INT NOT NULL,
    FOREIGN KEY (id_fiche_personnage) REFERENCES fiche_personnage(id)
);

DROP TABLE IF EXISTS repas;
CREATE TABLE repas (
	id INT PRIMARY KEY AUTO_INCREMENT,
	nom VARCHAR(30),
	id_fiche_personnage INT NOT NULL,
    FOREIGN KEY (id_fiche_personnage) REFERENCES fiche_personnage(id)
);

DROP TABLE IF EXISTS sauvegarde;
CREATE TABLE sauvegarde (
	id INT PRIMARY KEY AUTO_INCREMENT,
	titre VARCHAR(30),
	id_chapitre INT,
	id_fiche_personnage INT,
	FOREIGN KEY (id_chapitre) REFERENCES chapitre(id),
    FOREIGN KEY (id_fiche_personnage) REFERENCES fiche_personnage(id)
);

#DROP USER 'utilisateur'@'localhost';
CREATE USER 'utilisateur'@'localhost' IDENTIFIED BY 'mdp';

GRANT SELECT ON TP_Livre.livre TO 'utilisateur'@'localhost';
GRANT SELECT ON TP_Livre.chapitre TO 'utilisateur'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON TP_Livre.fiche_personnage TO 'utilisateur'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON TP_Livre.discipline_choix TO 'utilisateur'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON TP_Livre.discipline_kai TO 'utilisateur'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON TP_Livre.arme_choix TO 'utilisateur'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON TP_Livre.arme TO 'utilisateur'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON TP_Livre.objet TO 'utilisateur'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON TP_Livre.objet_spec TO 'utilisateur'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON TP_Livre.repas TO 'utilisateur'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON TP_Livre.sauvegarde TO 'utilisateur'@'localhost';

ALTER USER 'utilisateur'@'localhost'
WITH
	MAX_USER_CONNECTIONS 999
	MAX_QUERIES_PER_HOUR 999
	MAX_UPDATES_PER_HOUR 999
	MAX_CONNECTIONS_PER_HOUR 999;


DELIMITER $$
CREATE TRIGGER limite_discipline_kai
BEFORE INSERT ON discipline_kai
FOR EACH ROW
BEGIN
    DECLARE count_discipline_kai INT;
    SELECT COUNT(*) INTO count_discipline_kai FROM discipline_kai WHERE id_fiche_personnage = NEW.id_fiche_personnage;
    
    IF count_discipline_kai >= 5 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Un personnage ne peut avoir plus de 5 discplines';
    END IF;
END $$

CREATE TRIGGER limite_arme
BEFORE INSERT ON arme
FOR EACH ROW
BEGIN
    DECLARE count_arme INT;
    SELECT COUNT(*) INTO count_arme FROM arme WHERE id_fiche_personnage = NEW.id_fiche_personnage;
    
    IF count_arme >= 2 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Un personnage ne peut avoir plus de 2 armes';
    END IF;
END $$
DELIMITER ;
