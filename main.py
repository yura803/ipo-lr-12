import random
import string

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
        self.is_loaded = False  # Новый атрибут для отслеживания загрузки
    
    def __str__(self):
        vip_status = "VIP" if self.is_vip else "Обычный"
        status = "✓ Загружен" if self.is_loaded else "✗ Не загружен"
        return f"{self.name} | Груз: {self.cargo_weight} т | {vip_status} | {status}"
    
    def __repr__(self):
        return f"Client('{self.name}', {self.cargo_weight}, {self.is_vip})"


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
        """Выгружает груз(ы) из транспортного средства."""
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
    
    def __str__(self):
        load_percent = self.get_load_percentage()
        return (f"[{self.vehicle_id}] "
                f"Грузоподъемность: {self.capacity} т | "
                f"Загружено: {self.current_load:.1f} т ({load_percent:.1f}%) | "
                f"Клиентов: {len(self.clients_list)}")
    
    def __repr__(self):
        return f"Vehicle('{self.vehicle_id}', {self.capacity})"


class Train(Vehicle):
    """Класс поезда."""
    
    def __init__(self, capacity: float, number_of_cars: int):
        super().__init__(capacity)
        if not isinstance(number_of_cars, int) or number_of_cars <= 0:
            raise ValueError("Количество вагонов должно быть положительным целым числом")
        
        self.number_of_cars = number_of_cars
        self.vehicle_id = 'TRN-' + self.vehicle_id.split('-')[1]
    
    def __str__(self):
        base = super().__str__()
        return f"🚂 Поезд ({self.number_of_cars} вагонов) | " + base


class Airplane(Vehicle):
    """Класс самолета."""
    
    def __init__(self, capacity: float, max_altitude: float):
        super().__init__(capacity)
        if not isinstance(max_altitude, (int, float)) or max_altitude <= 0:
            raise ValueError("Максимальная высота должна быть положительным числом")
        
        self.max_altitude = float(max_altitude)
        self.vehicle_id = 'AIR-' + self.vehicle_id.split('-')[1]
    
    def __str__(self):
        base = super().__str__()
        return f"✈️ Самолет (до {self.max_altitude} м) | " + base


class TransportCompany:
    """Класс транспортной компании."""
    
    def __init__(self, name: str):
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
                vehicle.unload_cargo()  # Выгружаем все грузы перед удалением
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
    
    def list_vehicles(self):
        return self.vehicles.copy()
    
    def list_clients(self):
        return self.clients.copy()
    
    def get_unloaded_clients(self):
        return [client for client in self.clients if not client.is_loaded]
    
    def get_available_vehicles(self):
        return [vehicle for vehicle in self.vehicles if vehicle.get_available_capacity() > 0]
    
    def optimize_cargo_distribution(self):
        """Оптимизирует распределение грузов."""
        # Сбрасываем все загрузки
        for vehicle in self.vehicles:
            vehicle.unload_cargo()
        
        # Сортируем клиентов: сначала VIP
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
            
            # Пытаемся загрузить в уже используемые транспортные средства
            for vehicle in used_vehicles:
                try:
                    vehicle.load_cargo(client)
                    loaded = True
                    break
                except ValueError:
                    continue
            
            # Если не поместилось, ищем новый транспорт
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
            
            if not loaded:
                print(f"⚠ Груз клиента '{client.name}' ({client.cargo_weight} т) не поместился")
        
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
    
    def __str__(self):
        stats = self.get_statistics()
        return (f"🏢 {self.name}\n"
                f"   Транспорт: {stats['vehicles_count']} | "
                f"Клиенты: {stats['clients_count']} (VIP: {stats['vip_clients']})\n"
                f"   Загружено: {stats['clients_loaded']} грузов")


# ==================== ФУНКЦИИ ДЛЯ МЕНЮ ====================

def print_header(title):
    """Выводит заголовок."""
    print("\n" + "═" * 60)
    print(f" {title}")
    print("═" * 60)

def print_subheader(title):
    """Выводит подзаголовок."""
    print(f"\n{'━' * 40}")
    print(f" {title}")
    print(f"{'━' * 40}")

def input_float(prompt, min_val=0.0):
    """Ввод числа с плавающей точкой с проверкой."""
    while True:
        try:
            value = float(input(prompt))
            if value <= min_val:
                print(f"Ошибка! Значение должно быть больше {min_val}")
                continue
            return value
        except ValueError:
            print("Ошибка! Введите число.")

def input_int(prompt, min_val=1):
    """Ввод целого числа с проверкой."""
    while True:
        try:
            value = int(input(prompt))
            if value < min_val:
                print(f"Ошибка! Значение должно быть не меньше {min_val}")
                continue
            return value
        except ValueError:
            print("Ошибка! Введите целое число.")

def input_bool(prompt):
    """Ввод булевого значения с проверкой."""
    while True:
        value = input(f"{prompt} (да/нет): ").lower()
        if value in ['да', 'д', 'yes', 'y']:
            return True
        elif value in ['нет', 'н', 'no', 'n']:
            return False
        else:
            print("Ошибка! Введите 'да' или 'нет'.")

def create_company():
    """Создает транспортную компанию."""
    print_header("СОЗДАНИЕ ТРАНСПОРТНОЙ КОМПАНИИ")
    
    while True:
        name = input("Введите название компании: ").strip()
        if name:
            try:
                return TransportCompany(name)
            except ValueError as e:
                print(f"Ошибка: {e}")
        else:
            print("Название не может быть пустым!")

def add_vehicle_menu(company):
    """Меню добавления транспортного средства."""
    print_header("ДОБАВЛЕНИЕ ТРАНСПОРТНОГО СРЕДСТВА")
    
    print("Выберите тип транспорта:")
    print("1. 🚚 Обычный транспорт")
    print("2. 🚂 Поезд")
    print("3. ✈️ Самолет")
    print("0. ↩️ Назад")
    
    choice = input("Ваш выбор: ")
    
    if choice == '0':
        return
    
    elif choice == '1':
        print_subheader("Создание обычного транспорта")
        capacity = input_float("Введите грузоподъемность (тонны): ", 0.1)
        try:
            vehicle = Vehicle(capacity)
            company.add_vehicle(vehicle)
            print(f"✅ Транспорт {vehicle.vehicle_id} успешно добавлен!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    elif choice == '2':
        print_subheader("Создание поезда")
        capacity = input_float("Введите грузоподъемность (тонны): ", 0.1)
        cars = input_int("Введите количество вагонов: ")
        try:
            vehicle = Train(capacity, cars)
            company.add_vehicle(vehicle)
            print(f"✅ Поезд {vehicle.vehicle_id} успешно добавлен!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    elif choice == '3':
        print_subheader("Создание самолета")
        capacity = input_float("Введите грузоподъемность (тонны): ", 0.1)
        altitude = input_float("Введите максимальную высоту полета (метры): ", 1)
        try:
            vehicle = Airplane(capacity, altitude)
            company.add_vehicle(vehicle)
            print(f"✅ Самолет {vehicle.vehicle_id} успешно добавлен!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    else:
        print("Неверный выбор!")

def add_client_menu(company):
    """Меню добавления клиента."""
    print_header("ДОБАВЛЕНИЕ КЛИЕНТА")
    
    name = input("Введите имя клиента: ").strip()
    while not name:
        print("Имя не может быть пустым!")
        name = input("Введите имя клиента: ").strip()
    
    weight = input_float("Введите вес груза (тонны): ", 0.1)
    is_vip = input_bool("Это VIP клиент?")
    
    try:
        client = Client(name, weight, is_vip)
        company.add_client(client)
        print(f"✅ Клиент '{name}' успешно добавлен!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def list_vehicles_menu(company):
    """Меню просмотра транспортных средств."""
    print_header("СПИСОК ТРАНСПОРТНЫХ СРЕДСТВ")
    
    vehicles = company.list_vehicles()
    
    if not vehicles:
        print("🚫 Транспортные средства отсутствуют")
        return
    
    print(f"Всего транспортных средств: {len(vehicles)}")
    print_subheader("Детальная информация")
    
    for i, vehicle in enumerate(vehicles, 1):
        print(f"\n{i}. {vehicle}")
        
        if vehicle.clients_list:
            print("   📦 Загруженные грузы:")
            for client in vehicle.clients_list:
                vip = " (VIP)" if client.is_vip else ""
                print(f"     • {client.name}{vip}: {client.cargo_weight} т")
        else:
            print("   📭 Нет загруженных грузов")

def list_clients_menu(company):
    """Меню просмотра клиентов."""
    print_header("СПИСОК КЛИЕНТОВ")
    
    clients = company.list_clients()
    
    if not clients:
        print("🚫 Клиенты отсутствуют")
        return
    
    print(f"Всего клиентов: {len(clients)}")
    print_subheader("Детальная информация")
    
    vip_clients = [c for c in clients if c.is_vip]
    regular_clients = [c for c in clients if not c.is_vip]
    
    if vip_clients:
        print("\n👑 VIP КЛИЕНТЫ:")
        for i, client in enumerate(vip_clients, 1):
            print(f"  {i}. {client}")
    
    if regular_clients:
        print("\n👤 ОБЫЧНЫЕ КЛИЕНТЫ:")
        for i, client in enumerate(regular_clients, 1):
            print(f"  {i}. {client}")

def manual_load_menu(company):
    """Меню ручной загрузки груза."""
    print_header("РУЧНАЯ ЗАГРУЗКА ГРУЗА")
    
    # Получаем незагруженных клиентов
    unloaded_clients = company.get_unloaded_clients()
    if not unloaded_clients:
        print("🚫 Нет клиентов с незагруженными грузами")
        return
    
    # Выбор клиента
    print("Выберите клиента для загрузки:")
    for i, client in enumerate(unloaded_clients, 1):
        vip = " (VIP)" if client.is_vip else ""
        print(f"{i}. {client.name}{vip}: {client.cargo_weight} т")
    
    try:
        client_choice = input_int("Номер клиента: ", 1) - 1
        if client_choice >= len(unloaded_clients):
            print("Неверный номер клиента!")
            return
        selected_client = unloaded_clients[client_choice]
    except:
        print("Ошибка ввода!")
        return
    
    # Получаем доступный транспорт
    available_vehicles = company.get_available_vehicles()
    if not available_vehicles:
        print("🚫 Нет доступного транспорта")
        return
    
    # Выбор транспорта
    print(f"\nВыберите транспорт для загрузки груза '{selected_client.name}':")
    for i, vehicle in enumerate(available_vehicles, 1):
        available = vehicle.get_available_capacity()
        print(f"{i}. {vehicle.vehicle_id} | Свободно: {available:.2f} т")
    
    try:
        vehicle_choice = input_int("Номер транспорта: ", 1) - 1
        if vehicle_choice >= len(available_vehicles):
            print("Неверный номер транспорта!")
            return
        selected_vehicle = available_vehicles[vehicle_choice]
    except:
        print("Ошибка ввода!")
        return
    
    # Попытка загрузки
    try:
        selected_vehicle.load_cargo(selected_client)
        print(f"✅ Груз клиента '{selected_client.name}' успешно загружен в {selected_vehicle.vehicle_id}!")
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")

def optimize_distribution_menu(company):
    """Меню оптимизации распределения грузов."""
    print_header("ОПТИМИЗАЦИЯ РАСПРЕДЕЛЕНИЯ ГРУЗОВ")
    
    if not company.clients:
        print("🚫 Нет клиентов для распределения")
        return
    
    if not company.vehicles:
        print("🚫 Нет транспортных средств")
        return
    
    print("Начинаем оптимизацию распределения...")
    print(f"• Клиентов: {len(company.clients)}")
    print(f"• Транспортных средств: {len(company.vehicles)}")
    
    input("\nНажмите Enter для продолжения...")
    
    used_vehicles = company.optimize_cargo_distribution()
    
    print_header("РЕЗУЛЬТАТЫ РАСПРЕДЕЛЕНИЯ")
    
    if not used_vehicles:
        print("🚫 Ни один груз не был загружен")
        return
    
    print(f"✅ Использовано транспортных средств: {len(used_vehicles)}")
    
    total_load = sum(v.current_load for v in used_vehicles)
    total_capacity = sum(v.capacity for v in used_vehicles)
    efficiency = (total_load / total_capacity * 100) if total_capacity > 0 else 0
    
    print(f"📊 Эффективность использования транспорта: {efficiency:.1f}%")
    
    print_subheader("Детализация по транспорту")
    
    for i, vehicle in enumerate(used_vehicles, 1):
        print(f"\n{i}. {vehicle}")
        if vehicle.clients_list:
            total_weight = sum(c.cargo_weight for c in vehicle.clients_list)
            vip_count = sum(1 for c in vehicle.clients_list if c.is_vip)
            print(f"   📦 Всего загружено: {total_weight} т")
            print(f"   👑 VIP клиентов: {vip_count}")
            print(f"   👤 Обычных клиентов: {len(vehicle.clients_list) - vip_count}")
    
    # Показать незагруженных клиентов
    unloaded = company.get_unloaded_clients()
    if unloaded:
        print_subheader("НЕЗАГРУЖЕННЫЕ ГРУЗЫ")
        print(f"⚠ Не загружены грузы {len(unloaded)} клиентов:")
        for client in unloaded:
            print(f"  • {client.name}: {client.cargo_weight} т")

def show_statistics_menu(company):
    """Меню показа статистики."""
    print_header("СТАТИСТИКА КОМПАНИИ")
    
    stats = company.get_statistics()
    
    print(f"🏢 Название компании: {stats['company_name']}")
    print(f"🚚 Транспортных средств: {stats['vehicles_count']}")
    print(f"👥 Клиентов: {stats['clients_count']} (VIP: {stats['vip_clients']})")
    print(f"📦 Общая грузоподъемность: {stats['total_capacity']:.2f} т")
    print(f"📊 Общая загрузка: {stats['total_load']:.2f} т")
    print(f"📈 Процент загрузки: {stats['load_percentage']:.1f}%")
    print(f"✅ Загружено грузов: {stats['clients_loaded']} из {stats['clients_count']}")
    print(f"⏳ Незагруженных грузов: {stats['clients_unloaded']}")
    
    # Детализация по транспорту
    if company.vehicles:
        print_subheader("ДЕТАЛИЗАЦИЯ ПО ТРАНСПОРТУ")
        for i, vehicle in enumerate(company.vehicles, 1):
            load_percent = vehicle.get_load_percentage()
            status = "📦 Загружен" if vehicle.current_load > 0 else "📭 Пуст"
            print(f"{i}. {vehicle.vehicle_id}: {vehicle.current_load:.1f}/{vehicle.capacity:.1f} т "
                  f"({load_percent:.1f}%) - {status}")

def unload_cargo_menu(company):
    """Меню выгрузки груза."""
    print_header("ВЫГРУЗКА ГРУЗА")
    
    # Находим транспорт с загруженными грузами
    loaded_vehicles = [v for v in company.vehicles if v.clients_list]
    if not loaded_vehicles:
        print("🚫 Нет загруженных грузов")
        return
    
    # Выбор транспорта
    print("Выберите транспорт для выгрузки:")
    for i, vehicle in enumerate(loaded_vehicles, 1):
        load_count = len(vehicle.clients_list)
        total_weight = sum(c.cargo_weight for c in vehicle.clients_list)
        print(f"{i}. {vehicle.vehicle_id} | Грузов: {load_count} | Общий вес: {total_weight} т")
    
    try:
        vehicle_choice = input_int("Номер транспорта: ", 1) - 1
        if vehicle_choice >= len(loaded_vehicles):
            print("Неверный номер транспорта!")
            return
        selected_vehicle = loaded_vehicles[vehicle_choice]
    except:
        print("Ошибка ввода!")
        return
    
    # Опции выгрузки
    print(f"\nТранспорт: {selected_vehicle.vehicle_id}")
    print("Загруженные грузы:")
    for i, client in enumerate(selected_vehicle.clients_list, 1):
        print(f"{i}. {client.name}: {client.cargo_weight} т")
    
    print("\n1. Выгрузить все грузы")
    print("2. Выгрузить конкретный груз")
    print("0. Назад")
    
    choice = input("Ваш выбор: ")
    
    if choice == '1':
        removed = selected_vehicle.unload_cargo()
        print(f"✅ Выгружено {len(removed)} грузов")
    
    elif choice == '2':
        client_name = input("Введите имя клиента для выгрузки: ").strip()
        removed = selected_vehicle.unload_cargo(client_name)
        if removed:
            print(f"✅ Груз клиента '{client_name}' выгружен")
        else:
            print(f"🚫 Груз клиента '{client_name}' не найден")

def remove_vehicle_menu(company):
    """Меню удаления транспортного средства."""
    print_header("УДАЛЕНИЕ ТРАНСПОРТНОГО СРЕДСТВА")
    
    vehicles = company.list_vehicles()
    if not vehicles:
        print("🚫 Транспортные средства отсутствуют")
        return
    
    print("Выберите транспорт для удаления:")
    for i, vehicle in enumerate(vehicles, 1):
        print(f"{i}. {vehicle.vehicle_id} | {vehicle.__class__.__name__}")
    
    try:
        choice = input_int("Номер транспорта: ", 1) - 1
        if choice >= len(vehicles):
            print("Неверный номер транспорта!")
            return
        
        selected_vehicle = vehicles[choice]
        
        confirm = input_bool(f"Удалить транспорт {selected_vehicle.vehicle_id}?")
        if confirm:
            removed = company.remove_vehicle(selected_vehicle.vehicle_id)
            print(f"✅ Транспорт {removed.vehicle_id} удален")
        else:
            print("Удаление отменено")
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
    except:
        print("Ошибка ввода!")

def remove_client_menu(company):
    """Меню удаления клиента."""
    print_header("УДАЛЕНИЕ КЛИЕНТА")
    
    clients = company.list_clients()
    if not clients:
        print("🚫 Клиенты отсутствуют")
        return
    
    print("Выберите клиента для удаления:")
    for i, client in enumerate(clients, 1):
        print(f"{i}. {client.name} | Груз: {client.cargo_weight} т")
    
    try:
        choice = input_int("Номер клиента: ", 1) - 1
        if choice >= len(clients):
            print("Неверный номер клиента!")
            return
        
        selected_client = clients[choice]
        
        confirm = input_bool(f"Удалить клиента '{selected_client.name}'?")
        if confirm:
            removed = company.remove_client(selected_client.name)
            print(f"✅ Клиент '{removed.name}' удален")
        else:
            print("Удаление отменено")
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
    except:
        print("Ошибка ввода!")

def save_to_file_menu(company):
    """Меню сохранения данных в файл."""
    print_header("СОХРАНЕНИЕ ДАННЫХ")
    
    filename = input("Введите имя файла (без расширения): ").strip()
    if not filename:
        print("Имя файла не может быть пустым!")
        return
    
    filename = filename + ".txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"ОТЧЕТ ТРАНСПОРТНОЙ КОМПАНИИ: {company.name}\n")
            file.write("="*60 + "\n\n")
            
            stats = company.get_statistics()
            file.write("ОБЩАЯ СТАТИСТИКА:\n")
            file.write(f"  Транспортных средств: {stats['vehicles_count']}\n")
            file.write(f"  Клиентов: {stats['clients_count']} (VIP: {stats['vip_clients']})\n")
            file.write(f"  Общая грузоподъемность: {stats['total_capacity']:.2f} т\n")
            file.write(f"  Общая загрузка: {stats['total_load']:.2f} т\n")
            file.write(f"  Процент загрузки: {stats['load_percentage']:.1f}%\n")
            file.write(f"  Загружено грузов: {stats['clients_loaded']} из {stats['clients_count']}\n\n")
            
            file.write("ТРАНСПОРТНЫЕ СРЕДСТВА:\n")
            for i, vehicle in enumerate(company.vehicles, 1):
                file.write(f"{i}. {vehicle}\n")
                if vehicle.clients_list:
                    file.write("   Загруженные грузы:\n")
                    for client in vehicle.clients_list:
                        vip = " (VIP)" if client.is_vip else ""
                        file.write(f"     - {client.name}{vip}: {client.cargo_weight} т\n")
                file.write("\n")
            
            file.write("КЛИЕНТЫ:\n")
            for i, client in enumerate(company.clients, 1):
                file.write(f"{i}. {client}\n")
            
        print(f"✅ Данные успешно сохранены в файл '{filename}'")
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

def load_demo_data(company):
    """Загружает демонстрационные данные."""
    print_header("ЗАГРУЗКА ДЕМО-ДАННЫХ")
    
    if input_bool("Загрузить демонстрационные данные? Существующие данные будут сохранены."):
        # Добавляем демо транспорт
        demo_vehicles = [
            Vehicle(5.0),
            Train(10.0, 5),
            Airplane(8.0, 10000),
            Vehicle(7.5),
            Train(15.0, 8)
        ]
        
        # Добавляем демо клиентов
        demo_clients = [
            Client("Иван Петров", 3.5),
            Client("Мария Сидорова", 2.1, True),
            Client("Алексей Иванов", 4.2),
            Client("Ольга Смирнова", 1.8, True),
            Client("Дмитрий Кузнецов", 2.7),
            Client("Екатерина Волкова", 3.0, True),
            Client("Сергей Николаев", 2.5),
            Client("Анна Козлова", 1.5)
        ]
        
        try:
            for vehicle in demo_vehicles:
                company.add_vehicle(vehicle)
            
            for client in demo_clients:
                company.add_client(client)
            
            print("✅ Демонстрационные данные успешно загружены!")
            print(f"   Добавлено: {len(demo_vehicles)} транспортных средств")
            print(f"   Добавлено: {len(demo_clients)} клиентов")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки демо-данных: {e}")

# ==================== ОСНОВНОЕ МЕНЮ ====================

def main():
    """Основная функция программы."""
    print_header("🚚 СИСТЕМА УПРАВЛЕНИЯ ТРАНСПОРТНОЙ КОМПАНИЕЙ 🚚")
    
    # Создаем компанию
    company = create_company()
    
    while True:
        print_header("ГЛАВНОЕ МЕНЮ")
        print(f"🏢 Компания: {company.name}")
        print(f"🚚 Транспорт: {len(company.vehicles)} | 👥 Клиенты: {len(company.clients)}")
        print()
        
        print("1.  🚚 Добавить транспортное средство")
        print("2.  👥 Добавить клиента")
        print("3.  📋 Просмотр транспортных средств")
        print("4.  📋 Просмотр клиентов")
        print("5.  📦 Ручная загрузка груза")
        print("6.  ⚡ Оптимизировать распределение грузов")
        print("7.  📊 Показать статистику")
        print("8.  📤 Выгрузить груз")
        print("9.  🗑️ Удалить транспортное средство")
        print("10. 🗑️ Удалить клиента")
        print("11. 💾 Сохранить данные в файл")
        print("12. 🎮 Загрузить демо-данные")
        print("0.  🚪 Выход")
        
        choice = input("\n📝 Ваш выбор: ")
        
        if choice == '1':
            add_vehicle_menu(company)
        elif choice == '2':
            add_client_menu(company)
        elif choice == '3':
            list_vehicles_menu(company)
        elif choice == '4':
            list_clients_menu(company)
        elif choice == '5':
            manual_load_menu(company)
        elif choice == '6':
            optimize_distribution_menu(company)
        elif choice == '7':
            show_statistics_menu(company)
        elif choice == '8':
            unload_cargo_menu(company)
        elif choice == '9':
            remove_vehicle_menu(company)
        elif choice == '10':
            remove_client_menu(company)
        elif choice == '11':
            save_to_file_menu(company)
        elif choice == '12':
            load_demo_data(company)
        elif choice == '0':
            print_header("ВЫХОД ИЗ ПРОГРАММЫ")
            if input_bool("Сохранить данные перед выходом?"):
                save_to_file_menu(company)
            print("Спасибо за использование системы! 👋")
            break
        else:
            print("❌ Неверный выбор!")
        
        input("\n⏎ Нажмите Enter для продолжения...")

# ==================== ЗАПУСК ПРОГРАММЫ ====================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\n⚠ Критическая ошибка: {e}")