import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import random
import string
from datetime import datetime
from tkinter import scrolledtext
import csv

# ==================== КЛАССЫ (как в предыдущем задании) ====================

class Client:
    """Класс для представления клиента компании."""
    
    def __init__(self, name: str, cargo_weight: float, is_vip: bool = False):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Имя клиента должно быть непустой строкой")
        
        if not isinstance(cargo_weight, (int, float)) or cargo_weight <= 0:
            raise ValueError("Вес груза должен быть положительным числом")
        
        if not isinstance(is_vip, bool):
            raise ValueError("is_vip должен быть булевым значением")
        
        self.name = name.strip()
        self.cargo_weight = float(cargo_weight)
        self.is_vip = is_vip
        self.is_loaded = False
    
    def to_dict(self):
        """Конвертирует объект в словарь."""
        return {
            'name': self.name,
            'cargo_weight': self.cargo_weight,
            'is_vip': self.is_vip,
            'is_loaded': self.is_loaded
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создает объект из словаря."""
        client = cls(data['name'], data['cargo_weight'], data['is_vip'])
        client.is_loaded = data.get('is_loaded', False)
        return client
    
    def __str__(self):
        vip_status = "VIP" if self.is_vip else "Обычный"
        status = "✓ Загружен" if self.is_loaded else "✗ Не загружен"
        return f"{self.name} | Груз: {self.cargo_weight} т | {vip_status} | {status}"


class Vehicle:
    """Базовый класс для транспортного средства."""
    
    def __init__(self, capacity: float):
        if not isinstance(capacity, (int, float)) or capacity <= 0:
            raise ValueError("Грузоподъемность должна быть положительным числом")
        
        self.vehicle_id = self._generate_id()
        self.capacity = float(capacity)
        self.current_load = 0.0
        self.clients_list = []
    
    def _generate_id(self):
        return 'VHC-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def load_cargo(self, client):
        if not isinstance(client, Client):
            raise TypeError("Параметр должен быть объектом класса Client")
        
        if client.is_loaded:
            raise ValueError(f"Груз клиента '{client.name}' уже загружен")
        
        new_load = self.current_load + client.cargo_weight
        
        if new_load > self.capacity:
            raise ValueError(
                f"Превышена грузоподъемность! "
                f"Требуется: {client.cargo_weight} т, "
                f"Доступно: {self.capacity - self.current_load:.2f} т"
            )
        
        self.current_load = new_load
        self.clients_list.append(client)
        client.is_loaded = True
        return True
    
    def unload_cargo(self, client_name: str = None):
        if not self.clients_list:
            return []
        
        if client_name:
            for i, client in enumerate(self.clients_list):
                if client.name == client_name:
                    self.current_load -= client.cargo_weight
                    removed = self.clients_list.pop(i)
                    removed.is_loaded = False
                    return [removed]
            return []
        else:
            removed = self.clients_list.copy()
            for client in removed:
                client.is_loaded = False
            self.clients_list.clear()
            self.current_load = 0.0
            return removed
    
    def get_available_capacity(self):
        return self.capacity - self.current_load
    
    def get_load_percentage(self):
        return (self.current_load / self.capacity * 100) if self.capacity > 0 else 0
    
    def to_dict(self):
        """Конвертирует объект в словарь."""
        return {
            'vehicle_id': self.vehicle_id,
            'capacity': self.capacity,
            'current_load': self.current_load,
            'clients_list': [c.name for c in self.clients_list],
            'type': self.__class__.__name__
        }
    
    def __str__(self):
        load_percent = self.get_load_percentage()
        return (f"[{self.vehicle_id}] "
                f"Грузоподъемность: {self.capacity} т | "
                f"Загружено: {self.current_load:.1f} т ({load_percent:.1f}%) | "
                f"Клиентов: {len(self.clients_list)}")


class Train(Vehicle):
    """Класс поезда."""
    
    def __init__(self, capacity: float, number_of_cars: int):
        super().__init__(capacity)
        if not isinstance(number_of_cars, int) or number_of_cars <= 0:
            raise ValueError("Количество вагонов должно быть положительным целым числом")
        
        self.number_of_cars = number_of_cars
        self.vehicle_id = 'TRN-' + self.vehicle_id.split('-')[1]
    
    def to_dict(self):
        data = super().to_dict()
        data['number_of_cars'] = self.number_of_cars
        return data
    
    def __str__(self):
        base = super().__str__()
        return f"Поезд ({self.number_of_cars} вагонов) | " + base


class Airplane(Vehicle):
    """Класс самолета."""
    
    def __init__(self, capacity: float, max_altitude: float):
        super().__init__(capacity)
        if not isinstance(max_altitude, (int, float)) or max_altitude <= 0:
            raise ValueError("Максимальная высота должна быть положительным числом")
        
        self.max_altitude = float(max_altitude)
        self.vehicle_id = 'AIR-' + self.vehicle_id.split('-')[1]
    
    def to_dict(self):
        data = super().to_dict()
        data['max_altitude'] = self.max_altitude
        return data
    
    def __str__(self):
        base = super().__str__()
        return f"Самолет (до {self.max_altitude} м) | " + base


class TransportCompany:
    """Класс транспортной компании."""
    
    def __init__(self, name: str = "Моя транспортная компания"):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Название компании должно быть непустой строкой")
        
        self.name = name.strip()
        self.vehicles = []
        self.clients = []
    
    def add_vehicle(self, vehicle):
        if not isinstance(vehicle, (Vehicle, Train, Airplane)):
            raise TypeError("Параметр должен быть объектом класса Vehicle или его наследника")
        
        for v in self.vehicles:
            if v.vehicle_id == vehicle.vehicle_id:
                raise ValueError(f"Транспорт с ID {vehicle.vehicle_id} уже существует")
        
        self.vehicles.append(vehicle)
        return True
    
    def remove_vehicle(self, vehicle_id: str):
        for i, vehicle in enumerate(self.vehicles):
            if vehicle.vehicle_id == vehicle_id:
                vehicle.unload_cargo()
                return self.vehicles.pop(i)
        raise ValueError(f"Транспорт с ID {vehicle_id} не найден")
    
    def add_client(self, client):
        if not isinstance(client, Client):
            raise TypeError("Параметр должен быть объектом класса Client")
        
        for c in self.clients:
            if c.name == client.name:
                raise ValueError(f"Клиент с именем '{client.name}' уже существует")
        
        self.clients.append(client)
        return True
    
    def remove_client(self, client_name: str):
        for i, client in enumerate(self.clients):
            if client.name == client_name:
                if client.is_loaded:
                    for vehicle in self.vehicles:
                        if client in vehicle.clients_list:
                            vehicle.unload_cargo(client_name)
                            break
                return self.clients.pop(i)
        raise ValueError(f"Клиент с именем '{client_name}' не найден")
    
    def get_unloaded_clients(self):
        return [client for client in self.clients if not client.is_loaded]
    
    def get_available_vehicles(self):
        return [vehicle for vehicle in self.vehicles if vehicle.get_available_capacity() > 0]
    
    def optimize_cargo_distribution(self):
        """Оптимизирует распределение грузов."""
        for vehicle in self.vehicles:
            vehicle.unload_cargo()
        
        vip_clients = sorted(
            [c for c in self.clients if c.is_vip],
            key=lambda x: x.cargo_weight,
            reverse=True
        )
        regular_clients = sorted(
            [c for c in self.clients if not c.is_vip],
            key=lambda x: x.cargo_weight,
            reverse=True
        )
        
        all_clients = vip_clients + regular_clients
        used_vehicles = []
        
        for client in all_clients:
            loaded = False
            
            for vehicle in used_vehicles:
                try:
                    vehicle.load_cargo(client)
                    loaded = True
                    break
                except ValueError:
                    continue
            
            if not loaded:
                for vehicle in self.vehicles:
                    if vehicle not in used_vehicles:
                        try:
                            vehicle.load_cargo(client)
                            used_vehicles.append(vehicle)
                            loaded = True
                            break
                        except ValueError:
                            continue
        
        return used_vehicles
    
    def get_statistics(self):
        total_capacity = sum(v.capacity for v in self.vehicles)
        total_load = sum(v.current_load for v in self.vehicles)
        total_clients_loaded = sum(len(v.clients_list) for v in self.vehicles)
        total_vip = sum(1 for c in self.clients if c.is_vip)
        
        return {
            'company_name': self.name,
            'vehicles_count': len(self.vehicles),
            'clients_count': len(self.clients),
            'vip_clients': total_vip,
            'total_capacity': total_capacity,
            'total_load': total_load,
            'load_percentage': (total_load / total_capacity * 100) if total_capacity > 0 else 0,
            'clients_loaded': total_clients_loaded,
            'clients_unloaded': len(self.get_unloaded_clients())
        }
    
    def save_to_file(self, filename):
        """Сохраняет данные компании в файл."""
        data = {
            'company_name': self.name,
            'clients': [c.to_dict() for c in self.clients],
            'vehicles': [v.to_dict() for v in self.vehicles],
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filename):
        """Загружает данные компании из файла."""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.name = data['company_name']
        self.clients = [Client.from_dict(c) for c in data['clients']]
        
        self.vehicles = []
        for v_data in data['vehicles']:
            if v_data['type'] == 'Train':
                vehicle = Train(v_data['capacity'], v_data['number_of_cars'])
            elif v_data['type'] == 'Airplane':
                vehicle = Airplane(v_data['capacity'], v_data['max_altitude'])
            else:
                vehicle = Vehicle(v_data['capacity'])
            
            vehicle.vehicle_id = v_data['vehicle_id']
            vehicle.current_load = v_data['current_load']
            
            for client_name in v_data['clients_list']:
                for client in self.clients:
                    if client.name == client_name:
                        vehicle.clients_list.append(client)
                        client.is_loaded = True
                        break
            
            self.vehicles.append(vehicle)
    
    def __str__(self):
        stats = self.get_statistics()
        return (f"{self.name}\n"
                f"Транспорт: {stats['vehicles_count']} | "
                f"Клиенты: {stats['clients_count']} (VIP: {stats['vip_clients']})\n"
                f"Загружено: {stats['clients_loaded']} грузов")


# ==================== ГРАФИЧЕСКИЙ ИНТЕРФЕЙС ====================

class AddClientWindow(tk.Toplevel):
    """Окно добавления/редактирования клиента."""
    
    def __init__(self, parent, company, client=None):
        super().__init__(parent)
        self.parent = parent
        self.company = company
        self.client = client
        
        if client:
            self.title("Редактирование клиента")
        else:
            self.title("Добавление клиента")
        
        self.geometry("400x250")
        self.resizable(False, False)
        
        # Центрирование окна
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        """Центрирует окно на экране."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Создает виджеты окна."""
        # Фрейм для полей ввода
        input_frame = ttk.Frame(self, padding="20")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Поле для имени
        ttk.Label(input_frame, text="Имя клиента:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(input_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.name_entry.focus()
        
        # Поле для веса груза
        ttk.Label(input_frame, text="Вес груза (тонны):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.weight_var = tk.StringVar()
        self.weight_entry = ttk.Entry(input_frame, textvariable=self.weight_var, width=30)
        self.weight_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Чекбокс для VIP статуса
        self.vip_var = tk.BooleanVar(value=False)
        self.vip_check = ttk.Checkbutton(input_frame, text="VIP клиент", variable=self.vip_var)
        self.vip_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Если редактируем существующего клиента, заполняем поля
        if self.client:
            self.name_var.set(self.client.name)
            self.weight_var.set(str(self.client.cargo_weight))
            self.vip_var.set(self.client.is_vip)
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(self, padding="10")
        button_frame.grid(row=1, column=0, sticky=(tk.E, tk.W))
        
        ttk.Button(button_frame, text="Сохранить", command=self.save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Подсказки
        self.name_entry.bind("<FocusIn>", lambda e: self.parent.show_tooltip("Введите имя клиента (только буквы, минимум 2 символа)"))
        self.weight_entry.bind("<FocusIn>", lambda e: self.parent.show_tooltip("Введите вес груза (положительное число, максимум 10000 тонн)"))
        
        # Настройка сетки
        input_frame.columnconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Бинды клавиш
        self.bind('<Return>', lambda e: self.save())
        self.bind('<Escape>', lambda e: self.destroy())
    
    def validate_input(self):
        """Проверяет корректность введенных данных."""
        name = self.name_var.get().strip()
        weight = self.weight_var.get().strip()
        
        # Проверка имени
        if not name:
            messagebox.showerror("Ошибка", "Имя клиента не может быть пустым!")
            self.name_entry.focus()
            return False
        
        if len(name) < 2:
            messagebox.showerror("Ошибка", "Имя клиента должно содержать минимум 2 символа!")
            self.name_entry.focus()
            return False
        
        # Проверка веса
        try:
            weight_val = float(weight)
            if weight_val <= 0:
                messagebox.showerror("Ошибка", "Вес груза должен быть положительным числом!")
                self.weight_entry.focus()
                return False
            if weight_val > 10000:
                messagebox.showerror("Ошибка", "Вес груза не может превышать 10000 тонн!")
                self.weight_entry.focus()
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Вес груза должен быть числом!")
            self.weight_entry.focus()
            return False
        
        return True
    
    def save(self):
        """Сохраняет клиента."""
        if not self.validate_input():
            return
        
        name = self.name_var.get().strip()
        weight = float(self.weight_var.get().strip())
        is_vip = self.vip_var.get()
        
        try:
            if self.client:
                # Обновляем существующего клиента
                self.client.name = name
                self.client.cargo_weight = weight
                self.client.is_vip = is_vip
            else:
                # Создаем нового клиента
                client = Client(name, weight, is_vip)
                self.company.add_client(client)
            
            self.parent.update_clients_table()
            self.parent.show_status("Клиент успешно сохранен")
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))


class AddVehicleWindow(tk.Toplevel):
    """Окно добавления транспортного средства."""
    
    def __init__(self, parent, company):
        super().__init__(parent)
        self.parent = parent
        self.company = company
        
        self.title("Добавление транспортного средства")
        self.geometry("450x300")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Создает виджеты окна."""
        # Фрейм для выбора типа транспорта
        type_frame = ttk.LabelFrame(self, text="Тип транспорта", padding="10")
        type_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        self.vehicle_type = tk.StringVar(value="Обычный транспорт")
        
        ttk.Radiobutton(type_frame, text="Обычный транспорт", 
                       variable=self.vehicle_type, value="Обычный транспорт").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(type_frame, text="Поезд", 
                       variable=self.vehicle_type, value="Поезд").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(type_frame, text="Самолет", 
                       variable=self.vehicle_type, value="Самолет").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Фрейм для параметров
        param_frame = ttk.LabelFrame(self, text="Параметры", padding="10")
        param_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Поле для грузоподъемности
        ttk.Label(param_frame, text="Грузоподъемность (тонны):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.capacity_var = tk.StringVar()
        self.capacity_entry = ttk.Entry(param_frame, textvariable=self.capacity_var, width=25)
        self.capacity_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.capacity_entry.focus()
        
        # Поле для дополнительных параметров
        self.extra_label = ttk.Label(param_frame, text="Количество вагонов:")
        self.extra_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.extra_var = tk.StringVar()
        self.extra_entry = ttk.Entry(param_frame, textvariable=self.extra_var, width=25)
        self.extra_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(self, padding="10")
        button_frame.grid(row=2, column=0, sticky=(tk.E, tk.W))
        
        ttk.Button(button_frame, text="Сохранить", command=self.save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Подсказки
        self.capacity_entry.bind("<FocusIn>", lambda e: self.parent.show_tooltip("Введите грузоподъемность (положительное число)"))
        
        # Настройка сетки
        param_frame.columnconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Бинды клавиш
        self.bind('<Return>', lambda e: self.save())
        self.bind('<Escape>', lambda e: self.destroy())
        
        # Привязка изменения типа транспорта
        self.vehicle_type.trace('w', self.on_type_change)
        self.on_type_change()
    
    def on_type_change(self, *args):
        """Обновляет метку для дополнительного параметра."""
        vehicle_type = self.vehicle_type.get()
        
        if vehicle_type == "Поезд":
            self.extra_label.config(text="Количество вагонов:")
            self.extra_var.set("")
        elif vehicle_type == "Самолет":
            self.extra_label.config(text="Максимальная высота (метры):")
            self.extra_var.set("")
        else:
            self.extra_label.config(text="Дополнительный параметр:")
            self.extra_var.set("")
    
    def validate_input(self):
        """Проверяет корректность введенных данных."""
        capacity = self.capacity_var.get().strip()
        extra = self.extra_var.get().strip()
        vehicle_type = self.vehicle_type.get()
        
        # Проверка грузоподъемности
        try:
            capacity_val = float(capacity)
            if capacity_val <= 0:
                messagebox.showerror("Ошибка", "Грузоподъемность должна быть положительным числом!")
                self.capacity_entry.focus()
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Грузоподъемность должна быть числом!")
            self.capacity_entry.focus()
            return False
        
        # Проверка дополнительных параметров
        if vehicle_type == "Поезд":
            try:
                extra_val = int(extra)
                if extra_val <= 0:
                    messagebox.showerror("Ошибка", "Количество вагонов должно быть положительным целым числом!")
                    self.extra_entry.focus()
                    return False
            except ValueError:
                messagebox.showerror("Ошибка", "Количество вагонов должно быть целым числом!")
                self.extra_entry.focus()
                return False
        
        elif vehicle_type == "Самолет":
            try:
                extra_val = float(extra)
                if extra_val <= 0:
                    messagebox.showerror("Ошибка", "Максимальная высота должна быть положительным числом!")
                    self.extra_entry.focus()
                    return False
            except ValueError:
                messagebox.showerror("Ошибка", "Максимальная высота должна быть числом!")
                self.extra_entry.focus()
                return False
        
        return True
    
    def save(self):
        """Сохраняет транспортное средство."""
        if not self.validate_input():
            return
        
        capacity = float(self.capacity_var.get().strip())
        vehicle_type = self.vehicle_type.get()
        
        try:
            if vehicle_type == "Обычный транспорт":
                vehicle = Vehicle(capacity)
            elif vehicle_type == "Поезд":
                cars = int(self.extra_var.get().strip())
                vehicle = Train(capacity, cars)
            else:  # Самолет
                altitude = float(self.extra_var.get().strip())
                vehicle = Airplane(capacity, altitude)
            
            self.company.add_vehicle(vehicle)
            self.parent.update_vehicles_table()
            self.parent.show_status(f"Транспортное средство {vehicle.vehicle_id} добавлено")
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))


class ResultsWindow(tk.Toplevel):
    """Окно отображения результатов распределения."""
    
    def __init__(self, parent, used_vehicles, statistics):
        super().__init__(parent)
        self.parent = parent
        
        self.title("Результаты распределения грузов")
        self.geometry("800x600")
        
        self.transient(parent)
        self.grab_set()
        
        self.used_vehicles = used_vehicles
        self.statistics = statistics
        
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Создает виджеты окна."""
        # Панель статистики
        stats_frame = ttk.LabelFrame(self, text="Статистика распределения", padding="10")
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        stats_text = f"""
        Всего клиентов: {self.statistics['clients_count']}
        VIP клиентов: {self.statistics['vip_clients']}
        Использовано транспорта: {len(self.used_vehicles)}
        Общая грузоподъемность: {self.statistics['total_capacity']:.1f} т
        Загружено всего: {self.statistics['total_load']:.1f} т
        Эффективность загрузки: {self.statistics['load_percentage']:.1f}%
        Загружено грузов: {self.statistics['clients_loaded']}
        Незагруженных грузов: {self.statistics['clients_unloaded']}
        """
        
        ttk.Label(stats_frame, text=stats_text, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)
        
        # Таблица с результатами
        table_frame = ttk.LabelFrame(self, text="Распределение грузов", padding="10")
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Создаем Treeview
        columns = ("Транспорт", "Грузоподъемность", "Загружено", "Процент", "Клиенты")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        # Настраиваем заголовки
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        # Добавляем данные
        for vehicle in self.used_vehicles:
            clients_list = ", ".join([c.name for c in vehicle.clients_list])
            values = (
                vehicle.vehicle_id,
                f"{vehicle.capacity} т",
                f"{vehicle.current_load:.1f} т",
                f"{vehicle.get_load_percentage():.1f}%",
                clients_list
            )
            self.tree.insert("", tk.END, values=values)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещаем виджеты
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(self, padding="10")
        button_frame.grid(row=2, column=0, sticky=(tk.E, tk.W))
        
        ttk.Button(button_frame, text="Экспорт в CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Экспорт в JSON", command=self.export_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Закрыть", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Настройка сетки
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
    
    def export_csv(self):
        """Экспортирует результаты в CSV файл."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Записываем статистику
                    writer.writerow(["Статистика распределения грузов"])
                    writer.writerow(["Параметр", "Значение"])
                    writer.writerow(["Всего клиентов", self.statistics['clients_count']])
                    writer.writerow(["VIP клиентов", self.statistics['vip_clients']])
                    writer.writerow(["Использовано транспорта", len(self.used_vehicles)])
                    writer.writerow(["Общая грузоподъемность", f"{self.statistics['total_capacity']:.1f} т"])
                    writer.writerow(["Загружено всего", f"{self.statistics['total_load']:.1f} т"])
                    writer.writerow(["Эффективность загрузки", f"{self.statistics['load_percentage']:.1f}%"])
                    writer.writerow(["Загружено грузов", self.statistics['clients_loaded']])
                    writer.writerow(["Незагруженных грузов", self.statistics['clients_unloaded']])
                    writer.writerow([])
                    
                    # Записываем распределение по транспорту
                    writer.writerow(["Распределение по транспортным средствам"])
                    writer.writerow(["Транспорт", "Грузоподъемность", "Загружено", "Процент", "Клиенты"])
                    
                    for vehicle in self.used_vehicles:
                        clients_list = ", ".join([c.name for c in vehicle.clients_list])
                        writer.writerow([
                            vehicle.vehicle_id,
                            f"{vehicle.capacity} т",
                            f"{vehicle.current_load:.1f} т",
                            f"{vehicle.get_load_percentage():.1f}%",
                            clients_list
                        ])
                
                messagebox.showinfo("Успех", f"Результаты успешно экспортированы в {filename}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {e}")
    
    def export_json(self):
        """Экспортирует результаты в JSON файл."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if filename:
            try:
                data = {
                    'timestamp': datetime.now().isoformat(),
                    'statistics': self.statistics,
                    'distribution': []
                }
                
                for vehicle in self.used_vehicles:
                    vehicle_data = {
                        'vehicle_id': vehicle.vehicle_id,
                        'capacity': vehicle.capacity,
                        'current_load': vehicle.current_load,
                        'load_percentage': vehicle.get_load_percentage(),
                        'clients': [c.name for c in vehicle.clients_list]
                    }
                    data['distribution'].append(vehicle_data)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Успех", f"Результаты успешно экспортированы в {filename}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {e}")


class MainApplication(tk.Tk):
    """Главное окно приложения."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Система управления транспортной компанией")
        self.geometry("1200x700")
        
        self.company = TransportCompany()
        
        self.create_menu()
        self.create_widgets()
        self.create_status_bar()
        
        self.center_window()
        
        # Создаем демо-данные для тестирования
        self.create_demo_data()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_menu(self):
        """Создает меню приложения."""
        menubar = tk.Menu(self)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Сохранить данные", command=self.save_data)
        file_menu.add_command(label="Загрузить данные", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # Меню "Экспорт"
        export_menu = tk.Menu(menubar, tearoff=0)
        export_menu.add_command(label="Экспорт результатов", command=self.export_results, state=tk.DISABLED)
        menubar.add_cascade(label="Экспорт", menu=export_menu)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)
        
        self.config(menu=menubar)
        self.export_menu = export_menu
    
    def create_widgets(self):
        """Создает основные виджеты приложения."""
        # Панель управления
        control_frame = ttk.LabelFrame(self, text="Управление", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=10, pady=10, columnspan=2)
        
        # Кнопки управления
        ttk.Button(control_frame, text="Добавить клиента", command=self.add_client,
                  width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Добавить транспорт", command=self.add_vehicle,
                  width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Удалить клиента", command=self.delete_client,
                  width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Удалить транспорт", command=self.delete_vehicle,
                  width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Распределить грузы", command=self.optimize_distribution,
                  width=20, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        # Таблица клиентов
        clients_frame = ttk.LabelFrame(self, text="Клиенты", padding="10")
        clients_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 5), pady=10)
        
        # Создаем Treeview для клиентов
        self.clients_tree = ttk.Treeview(clients_frame, columns=("Имя", "Вес груза", "VIP статус", "Статус"), 
                                        show="headings", height=15)
        
        # Настраиваем заголовки
        columns = [("Имя", 200), ("Вес груза", 100), ("VIP статус", 100), ("Статус", 100)]
        for col, width in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=width)
        
        # Добавляем скроллбар
        clients_scrollbar = ttk.Scrollbar(clients_frame, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=clients_scrollbar.set)
        
        # Размещаем виджеты
        self.clients_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        clients_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Бинд двойного клика для редактирования
        self.clients_tree.bind("<Double-1>", self.edit_client)
        
        # Таблица транспортных средств
        vehicles_frame = ttk.LabelFrame(self, text="Транспортные средства", padding="10")
        vehicles_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 10), pady=10)
        
        # Создаем Treeview для транспорта
        self.vehicles_tree = ttk.Treeview(vehicles_frame, columns=("ID", "Тип", "Грузоподъемность", "Загружено", "Процент"), 
                                         show="headings", height=15)
        
        # Настраиваем заголовки
        columns = [("ID", 150), ("Тип", 100), ("Грузоподъемность", 100), ("Загружено", 100), ("Процент", 80)]
        for col, width in columns:
            self.vehicles_tree.heading(col, text=col)
            self.vehicles_tree.column(col, width=width)
        
        # Добавляем скроллбар
        vehicles_scrollbar = ttk.Scrollbar(vehicles_frame, orient=tk.VERTICAL, command=self.vehicles_tree.yview)
        self.vehicles_tree.configure(yscrollcommand=vehicles_scrollbar.set)
        
        # Размещаем виджеты
        self.vehicles_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vehicles_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Настройка сетки
        clients_frame.rowconfigure(0, weight=1)
        clients_frame.columnconfigure(0, weight=1)
        vehicles_frame.rowconfigure(0, weight=1)
        vehicles_frame.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        # Стилизация
        style = ttk.Style()
        style.configure("Accent.TButton", font=('TkDefaultFont', 10, 'bold'))
    
    def create_status_bar(self):
        """Создает статусную строку."""
        self.status_var = tk.StringVar()
        self.status_var.set("Готово")
        
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Панель для подсказок
        self.tooltip_var = tk.StringVar()
        tooltip_bar = ttk.Label(self, textvariable=self.tooltip_var, relief=tk.SUNKEN, anchor=tk.W)
        tooltip_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    def create_demo_data(self):
        """Создает демонстрационные данные."""
        try:
            # Добавляем клиентов
            clients = [
                Client("Иван Петров", 3.5),
                Client("Мария Сидорова", 2.1, True),
                Client("Алексей Иванов", 4.2),
                Client("Ольга Смирнова", 1.8, True),
                Client("Дмитрий Кузнецов", 2.7)
            ]
            
            for client in clients:
                self.company.add_client(client)
            
            # Добавляем транспорт
            vehicles = [
                Vehicle(5.0),
                Train(10.0, 5),
                Airplane(8.0, 10000)
            ]
            
            for vehicle in vehicles:
                self.company.add_vehicle(vehicle)
            
            self.update_clients_table()
            self.update_vehicles_table()
            self.show_status("Демонстрационные данные загружены")
            
        except Exception as e:
            print(f"Ошибка при создании демо-данных: {e}")
    
    def show_tooltip(self, text):
        """Показывает подсказку."""
        self.tooltip_var.set(text)
    
    def show_status(self, text):
        """Показывает статус."""
        self.status_var.set(text)
    
    def update_clients_table(self):
        """Обновляет таблицу клиентов."""
        # Очищаем таблицу
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
        
        # Добавляем клиентов
        for client in self.company.clients:
            vip_status = "VIP" if client.is_vip else "Нет"
            loaded_status = "Загружен" if client.is_loaded else "Не загружен"
            self.clients_tree.insert("", tk.END, values=(
                client.name,
                f"{client.cargo_weight} т",
                vip_status,
                loaded_status
            ))
    
    def update_vehicles_table(self):
        """Обновляет таблицу транспортных средств."""
        # Очищаем таблицу
        for item in self.vehicles_tree.get_children():
            self.vehicles_tree.delete(item)
        
        # Добавляем транспорт
        for vehicle in self.company.vehicles:
            vehicle_type = vehicle.__class__.__name__
            if vehicle_type == "Train":
                vehicle_type = "Поезд"
            elif vehicle_type == "Airplane":
                vehicle_type = "Самолет"
            else:
                vehicle_type = "Транспорт"
            
            self.vehicles_tree.insert("", tk.END, values=(
                vehicle.vehicle_id,
                vehicle_type,
                f"{vehicle.capacity} т",
                f"{vehicle.current_load:.1f} т",
                f"{vehicle.get_load_percentage():.1f}%"
            ))
    
    def add_client(self):
        """Открывает окно добавления клиента."""
        AddClientWindow(self, self.company)
    
    def edit_client(self, event):
        """Редактирует выбранного клиента."""
        selection = self.clients_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.clients_tree.item(item)['values']
        client_name = values[0]
        
        # Находим клиента
        for client in self.company.clients:
            if client.name == client_name:
                AddClientWindow(self, self.company, client)
                break
    
    def delete_client(self):
        """Удаляет выбранного клиента."""
        selection = self.clients_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите клиента для удаления")
            return
        
        item = selection[0]
        values = self.clients_tree.item(item)['values']
        client_name = values[0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить клиента '{client_name}'?"):
            try:
                self.company.remove_client(client_name)
                self.update_clients_table()
                self.show_status(f"Клиент '{client_name}' удален")
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))
    
    def add_vehicle(self):
        """Открывает окно добавления транспортного средства."""
        AddVehicleWindow(self, self.company)
    
    def delete_vehicle(self):
        """Удаляет выбранное транспортное средство."""
        selection = self.vehicles_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите транспортное средство для удаления")
            return
        
        item = selection[0]
        values = self.vehicles_tree.item(item)['values']
        vehicle_id = values[0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить транспортное средство '{vehicle_id}'?"):
            try:
                self.company.remove_vehicle(vehicle_id)
                self.update_vehicles_table()
                self.show_status(f"Транспортное средство '{vehicle_id}' удалено")
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))
    
    def optimize_distribution(self):
        """Оптимизирует распределение грузов."""
        if not self.company.clients:
            messagebox.showwarning("Предупреждение", "Нет клиентов для распределения")
            return
        
        if not self.company.vehicles:
            messagebox.showwarning("Предупреждение", "Нет транспортных средств")
            return
        
        try:
            used_vehicles = self.company.optimize_cargo_distribution()
            statistics = self.company.get_statistics()
            
            # Обновляем таблицы
            self.update_clients_table()
            self.update_vehicles_table()
            
            # Активируем меню экспорта
            self.export_menu.entryconfig(0, state=tk.NORMAL)
            
            # Показываем результаты
            ResultsWindow(self, used_vehicles, statistics)
            
            self.show_status("Распределение грузов выполнено успешно")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при распределении грузов: {e}")
    
    def export_results(self):
        """Экспортирует результаты распределения."""
        if not hasattr(self, 'last_used_vehicles'):
            messagebox.showwarning("Предупреждение", "Сначала выполните распределение грузов")
            return
        
        # Открываем окно экспорта
        ResultsWindow(self, self.last_used_vehicles, self.company.get_statistics())
    
    def save_data(self):
        """Сохраняет данные в файл."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if filename:
            try:
                self.company.save_to_file(filename)
                messagebox.showinfo("Успех", f"Данные успешно сохранены в {filename}")
                self.show_status(f"Данные сохранены в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")
    
    def load_data(self):
        """Загружает данные из файла."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if filename:
            try:
                self.company.load_from_file(filename)
                self.update_clients_table()
                self.update_vehicles_table()
                messagebox.showinfo("Успех", f"Данные успешно загружены из {filename}")
                self.show_status(f"Данные загружены из {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке: {e}")
    
    def show_about(self):
        """Показывает окно 'О программе'."""
        about_text = """
        Лабораторная работа №12
        Вариант: Транспортная компания
        
        Разработчик: [Ваше ФИО]
        
        Описание: Система управления транспортной компанией
        с оптимизацией распределения грузов.
        
        Функции:
        - Управление клиентами и транспортом
        - Оптимизация распределения грузов
        - Визуализация результатов
        - Экспорт данных
        """
        
        messagebox.showinfo("О программе", about_text)


# ==================== ЗАПУСК ПРИЛОЖЕНИЯ ====================

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()