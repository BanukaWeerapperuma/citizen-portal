import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def seed_database():
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    db = client.get_default_database()
    
    services_col = db['services']
    admins_col = db['admins']
    
    # 1. Clear existing data
    services_col.delete_many({})
    
    # 2. Real Sri Lankan Ministry Data
    ministries = [
        {
            "name": "Ministry of Transport & Civil Aviation",
            "description": "Responsible for the formulation and implementation of policies for transport in Sri Lanka.",
            "services": [
                {"name": "Driving License Renewal", "url": "https://dmt.gov.lk/index.php?option=com_content&view=article&id=51&Itemid=163&lang=en"},
                {"name": "Vehicle Registration", "url": "https://dmt.gov.lk/index.php?option=com_content&view=article&id=70&Itemid=173&lang=en"},
                {"name": "Railway Timetable", "url": "https://railway.gov.lk/web/index.php?lang=en"}
            ],
            "faqs": [
                {"q": "How to renew a driving license?", "a": "You can visit the DMT office or use the online portal for appointments."},
                {"q": "Where to find train schedules?", "a": "Visit the Sri Lanka Railways official website."}
            ]
        },
        {
            "name": "Department of Immigration and Emigration",
            "description": "Handling passports, visas, and border control for Sri Lankan citizens and visitors.",
            "services": [
                {"name": "Passport Application", "url": "https://www.immigration.gov.lk/pages_e.php?id=7"},
                {"name": "Electronic Travel Authorization (ETA)", "url": "https://eta.gov.lk/slvisa/"},
                {"name": "Dual Citizenship", "url": "https://www.immigration.gov.lk/pages_e.php?id=18"}
            ],
            "faqs": [
                {"q": "Can I apply for a passport online?", "a": "Yes, through the official department website portal."},
                {"q": "How long does it take for a one-day service?", "a": "One-day service passports are usually issued by evening if applied before 12 PM."}
            ]
        },
        {
            "name": "Ministry of Education",
            "description": "Overseeing the primary, secondary and tertiary education system in Sri Lanka.",
            "services": [
                {"name": "Exam Results (DoE)", "url": "https://www.doenets.lk/"},
                {"name": "School Admission Info", "url": "https://moe.gov.lk/"},
                {"name": "Higher Education Portal", "url": "https://www.mohe.gov.lk/"}
            ],
            "faqs": [
                {"q": "Where can I see O/L results?", "a": "Visit doenets.lk and enter your index number."},
                {"q": "How to apply for a university?", "a": "UGC handles university entrance via their official portal."}
            ]
        },
        {
            "name": "Ministry of Health",
            "description": "Providing healthcare services and regulating medical standards across the island.",
            "services": [
                {"name": "Vaccination Records", "url": "https://www.health.gov.lk/"},
                {"name": "Pharmacy Locator", "url": "https://www.nmra.gov.lk/"},
                {"name": "Hospital Appointments", "url": "https://echannelling.com/"}
            ],
            "faqs": [
                {"q": "Is the COVID vaccine still mandatory?", "a": "Please check the latest guidelines on the Health Ministry website."},
                {"q": "Where is the nearest government hospital?", "a": "Use the health map on the ministry website."}
            ]
        },
        {
            "name": "Department of Registration of Persons",
            "description": "Issuing National Identity Cards (NIC) for all Sri Lankan citizens.",
            "services": [
                {"name": "New NIC Application", "url": "https://www.drp.gov.lk/index.php?option=com_content&view=article&id=5&Itemid=125&lang=en"},
                {"name": "NIC Renewal/Duplicate", "url": "https://www.drp.gov.lk/index.php?option=com_content&view=article&id=6&Itemid=126&lang=en"}
            ],
            "faqs": [
                {"q": "What is the age to apply for NIC?", "a": "Currently 15 years and above."},
                {"q": "How much is the duplicate NIC fee?", "a": "Please refer to the fee schedule on drp.gov.lk."}
            ]
        }
    ]
    
    services_col.insert_many(ministries)
    print(f"Seeded {len(ministries)} ministries with clickable service URLs.")
    
    # 3. Ensure Admin exists
    admin_pwd = "admin123"
    admins_col.update_one(
        {"username": "admin"},
        {"$set": {"password": admin_pwd, "role": "superadmin"}},
        upsert=True
    )
    print("Admin 'admin' verified with password 'admin123'.")

if __name__ == "__main__":
    seed_database()
