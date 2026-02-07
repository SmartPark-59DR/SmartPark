import tkinter as tk
from tkinter import messagebox
from abc import ABC, abstractmethod
import os
import re
import time
import math

"""Wykonał MS"""
"""Funkcja czytająca plik tekstowy z obsługą różnych kodowań"""

def encode(filename):
    if not os.path.exists(filename):
        return []
    encodings = ['utf-8', 'cp1250', 'cp1252', 'latin-1']
    for i in encodings:
        try:
            with open(filename, 'r', encoding=i) as f:
                return [line.rstrip("\n") for line in f]
        except UnicodeDecodeError:                             
            continue
        except Exception:
            continue
    try:
        with open(filename, 'r', encoding='utf-8', errors='replace') as f:
            return [line.rstrip("\n") for line in f]
    except Exception:
        return []

"""Wykonał MS"""
"""Klasa abstrakcyjna Vehicle reprezentująca pojazd"""

class Vehicle(ABC):
    """Wzorzec definiujący format numeru rejestracyjnego: 2-3 wielkie litery, potem 3-5 cyfr."""

    License_plate_number_pattern = r'^[A-Z]{2,3}[0-9]{3,5}$'

    def __init__(self, plate: str):
        plate = plate.strip().upper()
        if not self.validate_plate(plate):
            raise ValueError("Niepoprawny numer rejestracyjny")
        self._plate = plate                                     

    """Sprawdza czy plate pasuje do wzorca i zwraca True lub False"""
    @staticmethod                                              
    def validate_plate(plate: str) -> bool:
        return re.match(Vehicle.License_plate_number_pattern, plate) is not None

    """Metoda zwracająca numer rejestracyjny"""
    def get_plate(self) -> str:
        return self._plate

    """Metoda abstrakcyjna"""
    @abstractmethod
    def get_type(self) -> str:
        pass

    def __str__(self):
        return f"{self.get_plate()} ({self.get_type()})"

"""Wykonał JM"""
"""Klasa pojazdów"""
class Car(Vehicle):
    def get_type(self) -> str:
        return "Samochód osobowy"

"""Klasa pojazdów"""
class Motorcycle(Vehicle):
    def get_type(self) -> str:
        return "Motocykl"

"""Klasa pojazdów"""
class Van(Vehicle):
    def get_type(self) -> str:
        return "Samochód dostawczy"

"""Klasa pojazdów"""
class Inne(Vehicle):
    def get_type(self) -> str:
        return "Inne"

"""Wykonał MS"""
"""Fabryka obiektów"""
class VehicleFactory:
    _map = {
        "Samochód osobowy": Car,
        "Motocykl": Motorcycle,
        "Samochód dostawczy": Van,
        "Inne": Inne
    }

    """Metoda fabryki, której zadaniem jest utworzenie i zwrócenie obiektu odpowiedniego typu pojazdu na podstawie podanej nazwy"""
    @staticmethod
    def create(plate: str, type_name: str) -> Vehicle:
        cls = VehicleFactory._map.get(type_name)
        if cls is None:
            raise ValueError("Nieznany typ pojazdu")
        return cls(plate)


"""Wykonał JM"""
"""Warstwa dostępu do danych z plików tekstowych"""

"""Klasa zajmująca się plikiem plates.txt, w którym przechowywane są zarejestrowane numery i typy pojazdów"""
class PlateData:
    File = "plates.txt"

    """Metoda, która odczytuje dane z pliku i zwraca listę numerów rejestracyjnych wraz z ich typami pojazdu"""
    @staticmethod
    def get_all_plates():
        lines = encode(PlateData.File)
        plates = []
        for i in lines:
            if not i:
                continue
            parts = i.split(",", 1)
            if len(parts) == 2:
                plates.append((parts[0].strip(), parts[1].strip()))
        return plates

    """Metoda sprawdzająca czy dany numer rejestracyjny istnieje w zbiorze danych"""
    @staticmethod
    def plate_exists(plate: str) -> bool:
        return any(p[0] == plate for p in PlateData.get_all_plates())

    """Metoda dodająca nowy numer rejestracyjny do pliku z danymi, jeśli taki numer jeszcze nie istnieje"""
    @staticmethod
    def add_plate(plate: str, vehicle_type: str) -> bool:
        if PlateData.plate_exists(plate):
            return False
        with open(PlateData.File, "a", encoding="utf-8") as f:
            f.write(f"{plate},{vehicle_type}\n")
        return True


    """Metoda, która tworzy i zwraca słownik numerów rejestracyjncych wraz z przypisanymi typami pojazdów"""
    @staticmethod
    def get_plate_types():
        return {p: t for p, t in PlateData.get_all_plates()}

"""Wykonał JM"""
"""Klasa zajmująca się plikiem sessions.txt, która przechowuje aktywne sesje parkowania"""
class SessionsData:
    File = "sessions.txt"


    """Metoda służaca do zapisywania inforamcji o sesji parkowania do pliku"""
    @staticmethod
    def add_session(plate: str, vehicle_type: str, hours: int, start_time: float):
        with open(SessionsData.File, "a", encoding="utf-8") as f:
            f.write(f"{plate},{vehicle_type},{hours},{start_time}\n")

    """Metoda odczytuje zapisane sesje z pliku i zwraca listę słowników. Jeden słownik to jedna sesja"""
    @staticmethod
    def get_all_sessions():
        sessions = []
        lines = encode(SessionsData.File)
        for i in lines:
            if not i:
                continue
            parts = i.split(",")
            if len(parts) != 4:
                continue
            plate, vtype, hours, start = parts
            try:
                sessions.append({
                    "plate": plate,
                    "vehicle_type": vtype,
                    "hours": int(hours),
                    "start": float(start)
                })
            except ValueError:
                continue
        return sessions

    """Metoda służąca do wyszukiwania sesji na podstawie numeru rejestracyjnego"""
    @staticmethod
    def find_session_by_plate(plate: str):
        for i in SessionsData.get_all_sessions():
            if i["plate"] == plate:
                return i
        return None

    """Metoda usuwa sesję z pliku na podstawie numeru rejestracyjnego oraz zwraca informację o usuniętej sesji"""
    @staticmethod
    def remove_session_by_plate(plate: str):
        if not os.path.exists(SessionsData.File):
            return None
        removed = None
        remaining = []
        lines = encode(SessionsData.File)
        for i in lines:
            if not i:
                continue
            parts = i.split(",")
            if len(parts) != 4:
                continue
            p = parts[0]
            if removed is None and p == plate:
                try:
                    removed = {
                        "plate": parts[0],
                        "vehicle_type": parts[1],
                        "hours": int(parts[2]),
                        "start": float(parts[3])
                    }
                except ValueError:
                    removed = None
            else:
                remaining.append(i)
        with open(SessionsData.File, "w", encoding="utf-8") as f:
            for i in remaining:
                f.write(i + "\n")
        return removed

"""Wykonał JM"""
"""Klasa zajmująca się plikiem archive.txt, w którym zapisywane są zakończone parkowania"""
class ParkingArchive:
    File = "archive.txt"

    """Metoda służąca do archiwizowania rekordu parkowania do pliku danych"""
    @staticmethod
    def add_record(plate, vehicle_type, spot, hours, base_cost, penalty):
        with open(ParkingArchive.File, "a", encoding="utf-8") as f:
            f.write(f"{plate} ,{vehicle_type},{spot},{hours},{base_cost},{penalty}\n")

    """Metoda odczytuje zapisane rekordy parkowania z pliku i zmienia w uporządkowaną listę danych"""
    @staticmethod
    def get_all_records():
        lines = encode(ParkingArchive.File)
        records = []
        for i in lines:
            if not i:
                continue
            parts = i.split(",")
            if len(parts) == 6:
                records.append(parts)
        return records

    """Metoda służąca do czyszczenia archiwum parkowania"""
    @staticmethod
    def reset_archive():
        with open(ParkingArchive.File, "w", encoding="utf-8") as f:
            pass

"""Wykonał MS"""
"""Klasa reprezentująca logikę miejsc parkingowych, dostępność i statystyki obciążenia"""
class Parking:
    def __init__(self, capacity=10):
        self.__capacity = int(capacity)
        self.__spots = {i: None for i in range(1, self.__capacity + 1)}
        self.__daily_count = 0
        self._stats_file = "stats.txt"
        self._load_spots_from_file()

    """Publiczna właściwość tylko do odczytu, która udostępnia pojemność parkingu."""
    @property
    def capacity(self):
        return self.__capacity

    """Prywatna metoda klasy, która odczytuje plik ze stanem miejsc parkingowych i zapisuje je w słowniku"""
    def _load_spots_from_file(self):
        lines = encode("spot.txt")
        for i in lines:
            if not i:
                continue
            parts = i.split(",", 1)
            if len(parts) == 2:
                try:
                    spot = int(parts[0])
                    plate = parts[1].strip()
                    if 1 <= spot <= self.__capacity:
                        self.__spots[spot] = plate
                except ValueError:
                    continue

    """Prywatna metoda klasy, która zapisuje aktualny stan miejsc parkingowych do pliku"""
    def _save_spots_to_file(self):
        with open("spot.txt", "w", encoding="utf-8") as f:
            for spot, plate in self.__spots.items():
                if plate:
                    f.write(f"{spot},{plate}\n")

    """Metoda, która sprawdza czy dany numer rejestracyjny znajduje się aktualnie na parkingu"""
    def is_plate_parked(self, plate: str) -> bool:
        return plate in self.__spots.values()


    """Metoda, która przydziela pojazdowi wybrane miejsce parkingowe"""
    def assign_spot(self, spot: int, plate: str):
        if not (1 <= spot <= self.__capacity):
            return False, "Nieprawidłowy numer miejsca"
        if self.is_plate_parked(plate):
            return False, "Ten pojazd jest już zaparkowany"
        if self.__spots[spot] is None:
            self.__spots[spot] = plate
            self._save_spots_to_file()
            self.update_statistics(spot)
            self.__daily_count += 1
            return True, "Miejsce przydzielone"
        else:
            return False, "Wybrane miejsce jest zajęte"


    """Metoda, która zwalnia wybrane miejsce parkingowe"""
    def release_spot(self, spot: int):
        if not (1 <= spot <= self.__capacity):
            return False, "Nieprawidłowy numer miejsca"
        plate = self.__spots.get(spot)
        if plate:
            self.__spots[spot] = None
            self._save_spots_to_file()
            return True, plate
        return False, None


    """Metoda, która odczytuje numer rejestracyjny pojazdu na wybranym miejscu parkingowym"""
    def get_plate_at_spot(self, spot: int):
        if not (1 <= spot <= self.__capacity):
            return None
        return self.__spots.get(spot)


    """Metoda, która informuje o aktualnym stanie dostępności miejsc parkingowych"""
    def availability(self):
        return dict(self.__spots)


    """Metoda, która zwraca dzienną liczbę obsłużonych pojazdów"""
    def daily_report(self):
        return self.__daily_count


    """Metoda, która aktualizuje statystyki obciążenia miejsc parkingowych"""
    def update_statistics(self, spot: int):
        stats = {}
        lines = encode(self._stats_file)
        for i in lines:
            if not i:
                continue
            parts = i.split(",", 1)
            if len(parts) == 2:
                try:
                    s = int(parts[0])
                    c = int(parts[1])
                    stats[s] = c
                except ValueError:
                    continue
        stats[spot] = stats.get(spot, 0) + 1
        with open(self._stats_file, "w", encoding="utf-8") as f:
            for s in sorted(stats.keys()):
                f.write(f"{s},{stats[s]}\n")


    """Metoda, która wczytuje statystyki użycia miejsc parkingowych z pliku i zwraca jako słownik"""
    def load_statistics(self):
        stats = {}
        lines = encode(self._stats_file)
        for i in lines:
            if not i:
                continue
            parts = i.split(",", 1)
            if len(parts) == 2:
                try:
                    s = int(parts[0])
                    c = int(parts[1])
                    stats[s] = c
                except ValueError:
                    continue
        return stats

    """Metoda, która czyści plik ze statystykami"""
    def reset_statistics(self):
        with open(self._stats_file, "w", encoding="utf-8") as f:
            pass

"""Wykonał JM"""
"""Klasa odpowiedzialna za zarządzanie cennikiem opłat za parkowanie"""
class Pricing:
    """Konstruktor klasy, który inicjalizuje cennik opłat za parkowanie"""
    def __init__(self):
        self.__prices = {
            "Samochód osobowy": 5.0,
            "Motocykl": 3.0,
            "Samochód dostawczy": 8.0,
            "Inne": 10.0
        }

    """Metoda, która pobiera ceny parkowania dla określonego typu pojazdu"""
    def get_price(self, vehicle_type: str) -> float:
        return self.__prices.get(vehicle_type, 0.0)

    """Metoda, która zwraca kopię słownika z cennikiem parkowania"""
    def get_all_prices(self):
        return self.__prices.copy()

    """Metoda, która oblicza podstawowy koszt parkowania na podstawie typu pojazdu i liczby godzin parkowania"""
    def calculate_cost(self, vehicle_type: str, hours: int) -> float:
        return self.get_price(vehicle_type) * hours

""" Wykonał MS"""
"""Klasa reprezentująca pojedynczą sesję parkowania"""
class ParkingSession:
    """Konstruktor klasy, który inicjalizuje atrybuty obiektu - numer rejestracyjny, typ pojazdu, liczbę godzin parkowania,
    czas rozpoczęcia sesji"""
    def __init__(self, plate: str, vehicle_type: str, hours: int, start_time: float):
        self.plate = plate
        self.vehicle_type = vehicle_type
        self.hours = int(hours)
        self.start_time = float(start_time)

    """Metoda, która oblicza całkowity koszt prakowania wraz z ewentualną karą za przekroczenie umówionego czasu"""
    def calculate_total_cost(self, pricing: Pricing):
        elapsed_seconds = time.time() - self.start_time
        elapsed_hours = elapsed_seconds / 3600.0
        base_cost = pricing.calculate_cost(self.vehicle_type, self.hours)
        if elapsed_hours <= self.hours:
            return base_cost, 0.0
        extra_hours = math.ceil(elapsed_hours - self.hours)
        penalty = extra_hours * (2 * pricing.get_price(self.vehicle_type))
        return base_cost, penalty

"""Wykonał JM"""
"""Klasa łącząca logikę aplikacji z GUI"""
class SmartParkApp:
    """Konstruktor klasy, który inicjalizuje główny system parkingowy"""
    def __init__(self, capacity=10):
        self.parking = Parking(capacity)
        self.pricing = Pricing()
        self.plate_repo = PlateData
        self.session_repo = SessionsData
        self.archive = ParkingArchive

        """GUI głównego okna"""
        self.root = tk.Tk()
        self.root.title("SmartPark")
        self.root.geometry("350x480")
        tk.Label(self.root, text="SMARTPARK", font=("Arial", 16, "bold")).pack(pady=10)

        tk.Button(self.root, text="Zarejestruj pojazd", width=30, command=self.register_vehicle).pack(pady=5)
        tk.Button(self.root, text="Przydziel miejsce", width=30, command=self.assign_spot).pack(pady=5)
        tk.Button(self.root, text="Zwolnij miejsce", width=30, command=self.release_spot).pack(pady=5)
        tk.Button(self.root, text="Cennik", width=30, command=self.show_pricing).pack(pady=5)
        tk.Button(self.root, text="Sprawdź dostępność", width=30, command=self.check_availability).pack(pady=5)
        tk.Button(self.root, text="Raport dzienny", width=30, command=self.daily_report).pack(pady=5)
        tk.Button(self.root, text="Statystyki obciążenia miejsc", width=30, command=self.statistics).pack(pady=5)
        tk.Button(self.root, text="Archiwum parkowań", width=30, command=self.show_archive).pack(pady=5)

    """Metoda, która uruchamia główną pętlę Tkinter"""
    def run(self):
        self.root.mainloop()

    """Metoda klasy, która umożliwia rejestrację nowego pojazdu poprzez interfejs graficzny"""
    def register_vehicle(self):
        def save():
            plate = entry.get().strip().upper()
            vehicle_type_name = type_var.get()
            try:
                vehicle = VehicleFactory.create(plate, vehicle_type_name)
            except ValueError:
                messagebox.showerror("Błąd", "Niepoprawny numer rejestracyjny!\nPrzykład: WPL12345")
                return
            if not PlateData.add_plate(vehicle.get_plate(), vehicle.get_type()):
                messagebox.showerror("Duplikat", "Ten numer rejestracyjny jest już zarejestrowany!")
                return
            messagebox.showinfo("OK", "Pojazd zarejestrowany")
            window.destroy()

        window = tk.Toplevel(self.root)
        window.geometry("300x250")
        window.title("Rejestracja pojazdu")
        tk.Label(window, text="Numer rejestracyjny:").pack(pady=5)
        entry = tk.Entry(window)
        entry.pack(pady=5)
        tk.Label(window, text="Typ pojazdu:").pack(pady=5)
        type_var = tk.StringVar(value="Samochód osobowy")
        types = ["Samochód osobowy", "Motocykl", "Samochód dostawczy", "Inne"]
        tk.OptionMenu(window, type_var, *types).pack(pady=5)
        tk.Button(window, text="Zarejestruj", command=save).pack(pady=10)


    """Metoda klasy, która umożliwia przydzielenie miejsca parkingowego wybranemu pojazdowi"""
    def assign_spot(self):
        plates = PlateData.get_all_plates()
        if not plates:
            messagebox.showwarning("Brak pojazdów", "Brak zarejestrowanych pojazdów.\nNajpierw zarejestruj pojazd.")
            return

        window = tk.Toplevel(self.root)
        window.geometry("350x220")
        window.title("Przydziel miejsce")

        plate_labels = [f"{p} ({t})" for p, t in plates]
        plate_map = {f"{p} ({t})": p for p, t in plates}

        tk.Label(window, text="Numer rejestracyjny").pack()
        plate_var = tk.StringVar(value=plate_labels[0])
        tk.OptionMenu(window, plate_var, *plate_labels).pack()

        tk.Label(window, text="Numer miejsca").pack()
        spot_var = tk.StringVar(value="1")
        tk.OptionMenu(window, spot_var, *range(1, self.parking.capacity + 1)).pack()

        tk.Label(window, text="Czas parkowania (godziny)").pack()
        time_var = tk.StringVar(value="1")
        tk.OptionMenu(window, time_var, *[str(i) for i in range(1, 25)]).pack()

        def assign():
            label = plate_var.get()
            plate = plate_map[label]
            try:
                spot = int(spot_var.get())
                hours = int(time_var.get())
            except ValueError:
                messagebox.showerror("Błąd", "Nieprawidłowe wartości")
                return
            success, mess = self.parking.assign_spot(spot, plate)
            if not success:
                messagebox.showerror("Błąd", mess)
                return
            plate_types = PlateData.get_plate_types()
            vehicle_type = plate_types.get(plate, "Inne")
            start_time = time.time()
            SessionsData.add_session(plate, vehicle_type, hours, start_time)
            cost = self.pricing.calculate_cost(vehicle_type, hours)
            messagebox.showinfo("OK", f"{mess}\n\nTyp pojazdu: {vehicle_type}\nCzas parkowania: {hours} h\nKoszt: {cost} zł")
            window.destroy()

        tk.Button(window, text="Przydziel", command=assign).pack(pady=10)

    """Wykonał MS"""
    """Metoda klasy, która umożliwia zwolnienie miejsca parkingowego, rozliczenie opłaty i zapis do archiwum"""
    def release_spot(self):
        window = tk.Toplevel(self.root)
        window.geometry("300x240")
        window.title("Zwolnij miejsce")

        tk.Label(window, text="Wybierz miejsce").pack()
        spot_var = tk.StringVar(value="1")
        tk.OptionMenu(window, spot_var, *range(1, self.parking.capacity + 1)).pack(pady=10)


        preview_label = tk.Label(window, text="", justify="left")
        preview_label.pack(pady=5)

        def update_preview(*args):
            try:
                spot = int(spot_var.get())
            except (ValueError, TypeError):
                preview_label.config(text="Nieprawidłowy numer miejsca")
                return
            plate = self.parking.get_plate_at_spot(spot)
            if not plate:
                preview_label.config(text="Miejsce wolne")
            else:
                plate_types = PlateData.get_plate_types()
                vehicle_type = plate_types.get(plate, "Inne")
                preview_label.config(text=f"Numer rejestracyjny: {plate}\nTyp pojazdu: {vehicle_type}")


        try:
            spot_var.trace_add("write", update_preview)
        except AttributeError:
            spot_var.trace("w", update_preview)


        update_preview()

        def release():
            try:
                spot = int(spot_var.get())
            except ValueError:
                messagebox.showerror("Błąd", "Nieprawidłowy numer miejsca")
                return

            success, plate_or_mess = self.parking.release_spot(spot)
            if not success:
                messagebox.showerror("Błąd", "Miejsce jest wolne lub nieprawidłowe")
                window.destroy()
                return

            plate = plate_or_mess
            session = SessionsData.remove_session_by_plate(plate)
            if session is None:
                messagebox.showerror("Błąd", "Nie znaleziono sesji parkowania dla tego pojazdu")
                return

            ps = ParkingSession(session["plate"], session["vehicle_type"], session["hours"], session["start"])
            base_cost, penalty = ps.calculate_total_cost(self.pricing)
            total = base_cost + penalty


            self.archive.add_record(ps.plate, ps.vehicle_type, spot, ps.hours, base_cost, penalty)


            base_s = f"{base_cost:.2f}"
            penalty_s = f"{penalty:.2f}"
            total_s = f"{total:.2f}"

            if penalty > 0:

                mess = (f"Koszt podstawowy: {base_s} zł\n"
                        f"Kara za przekroczenie czasu: {penalty_s} zł\n"
                        f"Razem do zapłaty: {total_s} zł")
                messagebox.showinfo("Rozliczenie", mess)
            else:

                messagebox.showinfo("Zwolniono miejsce",
                                    f"Pojazd {ps.plate} został zwolniony.\n"
                                    f"Dziękujemy za skorzystanie z SmartPark!")

            window.destroy()

        tk.Button(window, text="Zwolnij", command=release).pack(pady=8)

    """Wykonał JM"""
    """Metoda, która umożliwia sprawdzenie i wyświetlenie aktualnej dostępności miejsc parkingowych"""
    def check_availability(self):
        status = ""
        for spot, plate in self.parking.availability().items():
            status += f"Miejsce {spot}: {'zajęte' if plate else 'wolne'}\n"
        messagebox.showinfo("Dostępność", status)

    """Metoda, która umożliwia wyświetlenie raportu dziennego. Wyświetla ilość zaparkowanych pojazdów
     od momentu uruchomienia programu"""
    def daily_report(self):
        count = self.parking.daily_report()
        messagebox.showinfo("Raport dzienny", f"Liczba zaparkowanych pojazdów (od uruchomienia): {count}")

    """Metoda, która umożliwia wyświetlenie statystyk obciążenia miejsc parkingowych oraz ich zresetowania"""
    def statistics(self):
        window = tk.Toplevel(self.root)
        window.title("Statystyki obciążenia miejsc")
        window.geometry("300x300")
        stats = self.parking.load_statistics()
        text = ""
        for i in range(1, self.parking.capacity + 1):
            text += f"Miejsce {i}: {stats.get(i, 0)}\n"
        label = tk.Label(window, text=text, justify="left")
        label.pack(pady=10)

        def reset():
            confirm = messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz wyzerować statystyki?")
            if not confirm:
                return
            self.parking.reset_statistics()
            messagebox.showinfo("Reset", "Statystyki zostały wyzerowane")
            window.destroy()
            self.statistics()

        tk.Button(window, text="Reset", command=reset).pack(pady=10)

    """Metoda, która umożliwia wyświetlenie aktualnego cennika opłat za parkowanie"""
    def show_pricing(self):
        prices = self.pricing.get_all_prices()
        text = "Cennik parkowania (zł/godzina):\n\n"
        for vehicle_type, price in prices.items():
            text += f"{vehicle_type}: {price} zł\n"
        messagebox.showinfo("Cennik", text)

    """Wykonał MS"""
    """Metoda, która umożliwia wyświetlenie archiwum wszystkich zakończonych parkowań 
    oraz umożliwia jego wyczyszczenie"""
    def show_archive(self):
        window = tk.Toplevel(self.root)
        window.title("Archiwum parkowań")
        window.geometry("800x500")
        records = self.archive.get_all_records()
        if not records:
            tk.Label(window, text="Brak danych w archiwum").pack(pady=20)
            return
        text = ""
        for i in records:
            plate, vtype, spot, hours, base, penalty = i
            total = float(base) + float(penalty)
            text += (f"Nr: {plate} | Typ: {vtype} | Miejsce: {spot} | "
                     f"Czas: {hours}h | Koszt: {base} zł | ")
            if float(penalty) > 0:
                text += f"Kara: {penalty} zł | "
            text += f"Razem: {total} zł\n\n"
        text_box = tk.Text(window, wrap="word")
        text_box.insert("1.0", text)
        text_box.config(state="disabled")
        text_box.pack(expand=True, fill="both", padx=10, pady=10)

        def reset_archive():
            confirm = messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz wyczyścić archiwum?")
            if not confirm:
                return
            self.archive.reset_archive()
            messagebox.showinfo("Reset", "Archiwum zostało wyczyszczone")
            window.destroy()
            self.show_archive()

        tk.Button(window, text="Reset archiwum", command=reset_archive).pack(pady=10)

"""Punkt startowy programu, w którym uruchamiana jest aplikacja"""
def main():
    app = SmartParkApp(capacity=10)
    app.run()

if __name__ == "__main__":

    main()

