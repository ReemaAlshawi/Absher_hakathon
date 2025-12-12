import csv
import random
import hashlib

# ==============================
#   SETTINGS
# ==============================
NUM_USERS = 50000
MIN_LOGS = 3
MAX_LOGS = 8

cities = ["Riyadh", "Jeddah", "Dammam", "Medina", "Taif", "Khobar", "Jizan", "Tabuk"]
services = [
    "Renew_ID", "Car_Sale", "Transfer_Owner", "Passport_Renew",
    "Absher_Activation", "License_Renew", "Cancel_Report"
]
ip_risks = ["Low", "Medium", "High"]

browsers = ["Chrome", "Safari", "Firefox", "Edge"]
oses = ["Windows", "iOS", "Android", "MacOS"]
languages = ["ar-SA", "en-US"]

# ==============================
#   FINGERPRINT GENERATOR
# ==============================
def generate_fingerprint(user_id, device_number):
    browser = random.choice(browsers)
    os = random.choice(oses)
    lang = random.choice(languages)
    screen = random.choice(["1920x1080", "1366x768", "1280x720"])

    base_string = f"{user_id}-{device_number}-{browser}-{os}-{lang}-{screen}"
    fp = hashlib.sha256(base_string.encode()).hexdigest()[:12]

    return f"fp_{fp}"

# ==============================
#   HELPERS
# ==============================
def random_time():
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"

def is_night(time_str):
    return int(time_str.split(":")[0]) < 6

def calculate_risk(is_known, time_str, user_city, location, ip_risk, first_time_service=False):
    risk = 0
    if is_known == "No":
        risk += 40
    if is_night(time_str):
        risk += 20
    if location != user_city:
        risk += 30
    if ip_risk == "Medium":
        risk += 20
    elif ip_risk == "High":
        risk += 40
    if first_time_service:
        risk += 10
    return risk

def classify_risk(score):
    if score <= 30:
        return "Low", "Allow"
    elif score <= 60:
        return "Medium", "OTP"
    elif score <= 80:
        return "High", "Fingerprint"
    else:
        return "Critical", "Call_User"

# ==============================
#   DATASET GENERATOR
# ==============================
def generate_dataset():
    rows = []

    for user_id in range(1001, 1001 + NUM_USERS):
        user_city = random.choice(cities)
        age = random.randint(18, 75)

        known_devices = [generate_fingerprint(user_id, i) for i in range(1, random.randint(2, 4))]

        num_logs = random.randint(MIN_LOGS, MAX_LOGS)
        used_services = set()

        # ----------- ENTRY EVENT (Login) -----------
        entry_device = random.choice(known_devices) if random.random() < 0.8 else generate_fingerprint(user_id, random.randint(100, 9999))
        entry_is_known = "Yes" if entry_device in known_devices else "No"

        entry_time = random_time()
        entry_ip_risk = random.choices(ip_risks, weights=[0.65, 0.25, 0.10])[0]
        entry_location = user_city if random.random() < 0.8 else random.choice([c for c in cities if c != user_city])

        entry_risk_score = calculate_risk(entry_is_known, entry_time, user_city, entry_location, entry_ip_risk)
        entry_risk_level, entry_action = classify_risk(entry_risk_score)

        rows.append([
            user_id, user_city, age, entry_device,
            "Login",                     # ← service added
            entry_time, entry_ip_risk, entry_location, entry_is_known,
            entry_risk_score, entry_risk_level, entry_action
        ])

        # ----------- SERVICE EVENTS -----------
        for _ in range(num_logs):
            service = random.choice(services)
            first_time_service = service not in used_services
            if first_time_service:
                used_services.add(service)

            device = random.choice(known_devices) if random.random() < 0.75 else generate_fingerprint(user_id, random.randint(100, 9999))
            is_known = "Yes" if device in known_devices else "No"

            time_used = random_time()
            location = user_city if random.random() < 0.8 else random.choice([c for c in cities if c != user_city])
            ip_risk = random.choices(ip_risks, weights=[0.65, 0.25, 0.10])[0]

            risk_score = calculate_risk(is_known, time_used, user_city, location, ip_risk, first_time_service)
            risk_level, action = classify_risk(risk_score)

            rows.append([
                user_id, user_city, age, device,
                service,              # ← service added
                time_used, ip_risk, location, is_known,
                risk_score, risk_level, action
            ])

    return rows

# ==============================
#   WRITE CSV
# ==============================
rows = generate_dataset()

filename = "absher_guardian_50000_no_event.csv"
with open(filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "UserID", "City", "Age", "DeviceID",
        "Service",          # ← NEW COLUMN
        "Time", "IP_Risk", "Location", "IsKnownDevice",
        "Risk_Score", "Risk_Level", "Action"
    ])
    writer.writerows(rows)

print(f"Dataset created: {filename}")
