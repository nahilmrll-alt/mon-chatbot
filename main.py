class Livre:
    def __init__(self, titre, auteur, edition):
        self.titre = titre
        self.auteur = auteur
        self.edition = edition
        self.disponible = True

    def prendre_livre(self):
        if self.disponible:
            self.disponible = False
            return True
        return False


class Reservations:
    def __init__(self):
        self.reservations = {}

    def ajouter_reservation(self, livre, date_debut, date_fin):
        # Si le titre est déjà dans le dictionnaire, le livre est déjà réservé
        if livre.titre in self.reservations:
            print("Le livre est déjà réservé.")
            return False
        
        self.reservations[livre.titre] = [date_debut, date_fin]
        print("La réservation a été ajoutée avec succès.")
        return True

    def annuler_reservation(self, titre, date):
        if titre in self.reservations:
            if self.reservations[titre][0] == date:
                del self.reservations[titre]
                print("La réservation a été annulée avec succès.")
                return True
            else:
                print("Cette date n'est pas associée au début de la réservation.")
                return False
        print("Aucune réservation trouvée pour ce livre.")
        return False

    def afficher_reservation(self, titre):
        if titre in self.reservations:
            debut, fin = self.reservations[titre]
            print(f"Livre : {titre}")
            print(f"Début : {debut} - Fin : {fin}")


def main():
    livres = [
        Livre("Le Petit Prince", "Antoine de Saint-Exupéry", 1943),
        Livre("1984", "George Orwell", 1949)
    ]

    reservations = Reservations()

    while True:
        print("\n1. Ajouter un livre")
        print("2. Affecter un livre à une réservation")
        print("3. Annuler une réservation")
        print("4. Afficher les réservations")
        print("5. Quitter")

        choice = input("Sélectionnez une option : ")

        if choice == "1":
            titre = input("Entrez le titre du livre : ")
            auteur = input("Entrez l'auteur du livre : ")
            edition = int(input("Entrez la date d'édition : "))
            
            for livre in livres:
                if livre.titre.lower() == titre.lower():
                    print("Ce livre existe déjà dans votre liste.")
                    break
            else:
                nouveau_livre = Livre(titre, auteur, edition)
                livres.append(nouveau_livre)
                print(f"Le livre '{titre}' a été ajouté.")

        elif choice == "2":
            titre_recherche = input("Entrez le titre du livre à réserver : ")
            livre_trouve = False
            
            for livre in livres:
                if livre.titre.lower() == titre_recherche.lower():
                    livre_trouve = True
                    print(f"\nLivre trouvé : {livre.titre}")
                    print(f"Auteur : {livre.auteur}")
                    print(f"Édition : {livre.edition}")

                    debut = input("Entrez la date de début (AAAA-MM-DD) : ")
                    fin = input("Entrez la date finale (AAAA-MM-DD) : ")

                    reservations.ajouter_reservation(livre, debut, fin)
                    break
            
            if not livre_trouve:
                print("Ce livre n'a pas été trouvé dans votre liste.")

        elif choice == "3":
            titre_recherche = input("Entrez le titre du livre pour l'annulation : ")
            livre_trouve = False
            
            for livre in livres:
                if livre.titre.lower() == titre_recherche.lower():
                    livre_trouve = True
                    debut = input("Entrez la date de début de la réservation à annuler (AAAA-MM-DD) : ")
                    reservations.annuler_reservation(livre.titre, debut)
                    break
            
            if not livre_trouve:
                print("Ce livre n'a pas été trouvé dans votre liste.")

        elif choice == "4":
            if not reservations.reservations:
                print("Aucune réservation en cours.")
            else:
                print("\n--- Liste des Réservations ---")
                for titre in reservations.reservations.keys():
                    reservations.afficher_reservation(titre)

        elif choice == "5":
            print("Au revoir !")
            break

        else:
            print("Sélection incorrecte. S'il vous plaît, réessayez.")


if __name__ == "__main__":
    main()