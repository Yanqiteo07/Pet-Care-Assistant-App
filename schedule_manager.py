import json
from copy import deepcopy
from session_manager import active_session


# --- Helper Functions for File I/O ---
def _read_file_content(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return '[]' if 'json' in filename or 'vet' in filename or 'feeding' in filename else ''


def _write_file_content(filename, content):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error writing to file {filename}: {e}")


# --- Parsing Functions  ---
def parse_vet_appointments(file_content):
    try:
        data = json.loads(file_content)
        for i, item in enumerate(data):
            item['id'] = f"v{i + 1}"
            item['category'] = 'vet'
        return data
    except:
        return []


def parse_grooming_records(file_content):
    records = []
    blocks = [b.strip() for b in file_content.split('----------------------------------------') if b.strip()]
    for i, block in enumerate(blocks):
        record = {'id': f"g{i + 1}", 'category': 'grooming'}
        for line in block.split('\n'):
            if ":" in line:
                key, val = line.split(":", 1)
                key_map = {"Pet Name": "pet_name", "Date": "visit_date", "Time": "visit_time", "Task": "task",
                           "Description": "description"}
                if key.strip() in key_map: record[key_map[key.strip()]] = val.strip()
        records.append(record)
    return records


def parse_feeding_records(file_content):
    try:
        data = json.loads(file_content)
        records = []
        for i, item in enumerate(data):
            records.append({
                'id': f"f{i + 1}",
                'category': 'feeding',
                'pet_name': item.get('Pet Name', 'N/A'),
                'visit_date': item.get('Date', 'N/A'),
                'time': item.get('Time', 'N/A'),
                'task': f"Feed: {item.get('Food Type', 'N/A')}",
                'amount': item.get('Amount', 'N/A'),
                'pet_age': item.get('Age', '')
            })
        return records
    except:
        return []

class ScheduleManager:
    def __init__(self):

        self.vet_file = active_session.get_user_file('vet_appointments.txt')
        self.grooming_file = active_session.get_user_file('grooming_records.txt')
        self.feeding_file = active_session.get_user_file('feeding_history.json')

        self.vet_schedule = parse_vet_appointments(_read_file_content(self.vet_file))
        self.grooming_schedule = parse_grooming_records(_read_file_content(self.grooming_file))
        self.feeding_schedule = parse_feeding_records(_read_file_content(self.feeding_file))
        self.undo_stack = []

    def _save_to_disk(self):

        # 1. Save Vet
        vet_clean = deepcopy(self.vet_schedule)
        for item in vet_clean:
            item.pop('id', None)
            item.pop('category', None)
        _write_file_content(self.vet_file, json.dumps(vet_clean, indent=4))

        # 2. Save Grooming (Text format)
        blocks = []
        for r in self.grooming_schedule:
            blocks.append(
                f"Pet Name: {r.get('pet_name')}\nDescription: {r.get('description', '')}\nDate: {r.get('visit_date')}\nTime: {r.get('visit_time')}\nTask: {r.get('task')}")
        content = '----------------------------------------\n' + '\n----------------------------------------\n'.join(
            blocks) + '\n----------------------------------------\n'
        _write_file_content(self.grooming_file, content)

        # 3. Save Feeding
        feeding_clean = []
        for r in self.feeding_schedule:
            feeding_clean.append({
                "Pet Name": r['pet_name'], "Age": r.get('pet_age', ''),
                "Date": r['visit_date'], "Time": r['time'],
                "Food Type": r['task'].replace('Feed: ', ''), "Amount": r['amount']
            })
        _write_file_content(self.feeding_file, json.dumps(feeding_clean, indent=4))

    def complete_task(self, category, item_id):
        target_list = getattr(self, f"{category}_schedule")
        item = next((i for i in target_list if i['id'] == item_id), None)
        if item:
            new_list = [i for i in target_list if i['id'] != item_id]
            setattr(self, f"{category}_schedule", new_list)
            self.undo_stack.append({'category': category, 'item': item})
            self._save_to_disk()
            return True
        return False

    def undo_last_action(self):
        if not self.undo_stack:
            return False

        last_action = self.undo_stack.pop()
        category = last_action['category']
        item = last_action['item']


        target_list = getattr(self, f"{category}_schedule")
        target_list.append(item)

        self._save_to_disk()
        return True

    def get_undo_count(self):
        return len(self.undo_stack)

    def get_schedule_data(self):
        return {'feeding': self.feeding_schedule, 'grooming': self.grooming_schedule, 'vet': self.vet_schedule}