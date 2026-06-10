import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def seed_database():
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    db = client['citizen_portal']
    
    services_col = db['services']
    admins_col = db['admins']
    
    # 1. Clear existing data
    services_col.delete_many({})
    
    # 2. Sri Lanka Ministries and Services (12 Ministries)
    docs = [
        {
            "id": "ministry_finance",
            "name": {"en": "Ministry of Finance", "si": "මුදල් අමාත්‍යාංශය", "ta": "நிதி அமைச்சு"},
            "contact": {"phone": "0112 484 500", "email": "info@treasury.gov.lk"},
            "links": [{"title": {"en": "Finance Ministry", "si": "මුදල් අමාත්‍යාංශය", "ta": "நிதி அமைச்சு"}, "url": "https://www.treasury.gov.lk/"}],
            "subservices": [
                {"id": "budget", "name": {"en": "National Budgeting", "si": "ජාතික අයවැයකරණය", "ta": "தேசிய வரவுசெலவுத் திட்டம்"}, "questions": [{"q": {"en": "How to see the national budget?", "si": "ජාතික අයවැය බලන්නේ කෙසේද?", "ta": "தேசிய வரவுசெலவுத் திட்டத்தை எவ்வாறு பார்ப்பது?"}, "answer": {"en": "Visit the treasury portal for latest reports.", "si": "නවතම වාර්තා සඳහා භාණ්ඩාගාර ද්වාරයට පිවිසෙන්න.", "ta": "சமீபத்திய அறிக்கைகளுக்கு கருவூல போர்ட்டலைப் பார்வையிடவும்."}}]},
                {"id": "tax", "name": {"en": "Tax Policy (Inland Revenue)", "si": "බදු ප්‍රතිපත්තිය (දේශීය ආදායම්)", "ta": "வரி கொள்கை (உள்நாட்டு வருவாய்)"}, "questions": [{"q": {"en": "How to register for TIN?", "si": "TIN සඳහා ලියාපදිංචි වන්නේ කෙසේද?", "ta": "TIN இற்கு எவ்வாறு பதிவு செய்வது?"}, "answer": {"en": "Register via the Inland Revenue website.", "si": "දේශීය ආදායම් වෙබ් අඩවිය හරහා ලියාපදිංචි වන්න.", "ta": "உள்நாட்டு வருவாய் வலைத்தளம் மூலம் பதிவு செய்யவும்."}}]},
                {"id": "customs", "name": {"en": "Custom Duties", "si": "රේගු බදු", "ta": "சுங்க வரிகள்"}, "questions": [{"q": {"en": "What are custom rates?", "si": "රේගු ගාස්තු මොනවාද?", "ta": "சுங்க விகிதங்கள் என்ன?"}, "answer": {"en": "Refer to Sri Lanka Customs official page.", "si": "ශ්‍රී ලංකා රේගු නිල පිටුව බලන්න.", "ta": "இலங்கை சுங்க அதிகாரப்பூர்வ பக்கத்தைப் பார்க்கவும்."}}]},
                {"id": "stabilization", "name": {"en": "Economic Stabilization", "si": "ආර්ථික ස්ථායීකරණය", "ta": "பொருளாதார ஸ்திரப்படுத்தல்"}, "questions": [{"q": {"en": "Latest economic status?", "si": "නවතම ආර්ථික තත්ත්වය?", "ta": "சமீபத்திய பொருளாதார நிலை?"}, "answer": {"en": "Check the central bank or treasury updates.", "si": "මහ බැංකු හෝ භාණ්ඩාගාර යාවත්කාලීන කිරීම් පරීක්ෂා කරන්න.", "ta": "மத்திய வங்கி அல்லது கருவூல புதுப்பிப்புகளைச் சரிபார்க்கவும்."}}]}
            ]
        },
        {
            "id": "ministry_education",
            "name": {"en": "Ministry of Education", "si": "අධ්‍යාපන අමාත්‍යාංශය", "ta": "கல்வி அமைச்சு"},
            "contact": {"phone": "0112 785 141", "email": "info@moe.gov.lk"},
            "links": [{"title": {"en": "MOE Portal", "si": "අධ්‍යාපන ද්වාරය", "ta": "கல்வி போர்டல்"}, "url": "https://moe.gov.lk/"}],
            "subservices": [
                {"id": "admission", "name": {"en": "School Admissions", "si": "පාසල් ඇතුළත් කිරීම්", "ta": "பள்ளி சேர்க்கை"}, "questions": [{"q": {"en": "How to apply for Grade 1?", "si": "1 ශ්‍රේණිය සඳහා අයදුම් කරන්නේ කෙසේද?", "ta": "முதலாம் வகுப்பிற்கு எவ்வாறு விண்ணப்பிப்பது?"}, "answer": {"en": "Follow the circular issued on MOE website.", "si": "අධ්‍යාපන අමාත්‍යාංශ වෙබ් අඩවියේ නිකුත් කර ඇති චක්‍රලේඛය අනුගමනය කරන්න.", "ta": "கல்வி அமைச்சின் இணையதளத்தில் வெளியிடப்பட்ட சுற்றறிக்கையைப் பின்பற்றவும்."}}]},
                {"id": "placements", "name": {"en": "Teacher Placements", "si": "ගුරු ස්ථානගත කිරීම්", "ta": "ஆசிரியர் இடமாற்றம்"}, "questions": [{"q": {"en": "How to request a transfer?", "si": "මාරුවීමක් ඉල්ලන්නේ කෙසේද?", "ta": "இடமாற்றம் கோருவது எப்படி?"}, "answer": {"en": "Apply through the teacher transfer portal.", "si": "ගුරු මාරු කිරීමේ ද්වාරය හරහා අයදුම් කරන්න.", "ta": "ஆசிரியர் இடமாற்ற போர்டல் மூலம் விண்ணப்பிக்கவும்."}}]},
                {"id": "exams", "name": {"en": "National Exam Coordination", "si": "ජාතික විභාග සම්බන්ධීකරණය", "ta": "தேசிய தேர்வு ஒருங்கிணைப்பு"}, "questions": [{"q": {"en": "When is the next exam?", "si": "ඊළඟ විභාගය කවදාද?", "ta": "அடுத்த தேர்வு எப்போது?"}, "answer": {"en": "Check doenets.lk for schedules.", "si": "කාලසටහන් සඳහා doenets.lk පරීක්ෂා කරන්න.", "ta": "அட்டவணைகளுக்கு doenets.lk ஐ சரிபார்க்கவும்."}}]},
                {"id": "curriculum", "name": {"en": "Curriculum Development", "si": "විෂයමාලා සංවර්ධනය", "ta": "பாடத்திட்ட மேம்பாடு"}, "questions": [{"q": {"en": "Where to get textbooks?", "si": "පෙළපොත් ලබා ගන්නේ කොහෙන්ද?", "ta": "பாடப்புத்தகங்களை எங்கே பெறுவது?"}, "answer": {"en": "Visit the Educational Publications Department.", "si": "අධ්‍යාපන ප්‍රකාශන දෙපාර්තමේන්තුවට පිවිසෙන්න.", "ta": "கல்வி வெளியீட்டுத் துறைக்குச் செல்லவும்."}}]}
            ]
        },
        {
            "id": "ministry_health",
            "name": {"en": "Ministry of Health", "si": "සෞඛ්‍ය අමාත්‍යාංශය", "ta": "சுகாதார அமைச்சு"},
            "contact": {"phone": "0112 669 192", "email": "postmaster@health.gov.lk"},
            "links": [{"title": {"en": "Health Ministry", "si": "සෞඛ්‍ය අමාත්‍යාංශය", "ta": "சுகாதார அமைச்சு"}, "url": "https://www.health.gov.lk/"}],
            "subservices": [
                {"id": "healthcare", "name": {"en": "Free Healthcare & Hospitals", "si": "නොමිලේ සෞඛ්‍ය සේවා සහ රෝහල්", "ta": "இலவச சுகாதாரம் மற்றும் மருத்துவமனைகள்"}, "questions": [{"q": {"en": "Is treatment free?", "si": "ප්‍රතිකාර නොමිලේ ද?", "ta": "சிகிச்சை இலவசமா?"}, "answer": {"en": "Yes, all government hospitals provide free treatment.", "si": "ඔව්, සියලුම රජයේ රෝහල් නොමිලේ ප්‍රතිකාර ලබා දෙයි.", "ta": "ஆம், அனைத்து அரசு மருத்துவமனைகளும் இலவச சிகிச்சை அளிக்கின்றன."}}]},
                {"id": "surveillance", "name": {"en": "Disease Surveillance (Dengue/NCDs)", "si": "රෝග නිරීක්ෂණය (ඩෙංගු/NCDs)", "ta": "நோய் கண்காணிப்பு (டெங்கு/NCDகள்)"}, "questions": [{"q": {"en": "Dengue alerts?", "si": "ඩෙංගු අනතුරු ඇඟවීම්?", "ta": "டெங்கு எச்சரிக்கைகள்?"}, "answer": {"en": "Check the Epidemiology Unit website.", "si": "වසංගත රෝග විද්‍යා අංශයේ වෙබ් අඩවිය පරීක්ෂා කරන්න.", "ta": "தொற்றுநோயியல் பிரிவு இணையதளத்தைப் பார்க்கவும்."}}]},
                {"id": "immunization", "name": {"en": "Immunization Programs", "si": "එන්නත් කිරීමේ වැඩසටහන්", "ta": "தடுப்பூசி திட்டங்கள்"}, "questions": [{"q": {"en": "Vaccine schedule?", "si": "එන්නත් කාලසටහන?", "ta": "தடுப்பூசி அட்டவணை?"}, "answer": {"en": "Available at all local MOH offices.", "si": "සියලුම ප්‍රාදේශීය MOH කාර්යාලවල පවතී.", "ta": "அனைத்து உள்ளூர் MOH அலுவலகங்களிலும் கிடைக்கிறது."}}]},
                {"id": "maternal", "name": {"en": "Maternal & Child Health", "si": "මාතෘ හා ළමා සෞඛ්‍යය", "ta": "தாய் மற்றும் சேய் ஆரோக்கியம்"}, "questions": [{"q": {"en": "Nutrition advice?", "si": "පෝෂණ උපදෙස්?", "ta": "ஊட்டச்சத்து ஆலோசனை?"}, "answer": {"en": "Consult your local midwife or family health clinic.", "si": "ඔබේ ප්‍රාදේශීය වින්නඹු මාතාව හෝ පවුල් සෞඛ්‍ය සායනය විමසන්න.", "ta": "உங்கள் உள்ளூர் மருத்துவச்சி அல்லது குடும்ப சுகாதார கிளினிக்கை அணுகவும்."}}]}
            ]
        },
        {
            "id": "ministry_transport",
            "name": {"en": "Ministry of Transport", "si": "ප්‍රවාහන අමාත්‍යාංශය", "ta": "போக்குவரத்து அமைச்சு"},
            "contact": {"phone": "0112 187 200", "email": "mintransport@sltnet.lk"},
            "links": [{"title": {"en": "Transport Ministry", "si": "ප්‍රවාහන අමාත්‍යාංශය", "ta": "போக்குவரத்து அமைச்சு"}, "url": "http://transport.gov.lk/"}],
            "subservices": [
                {"id": "license", "name": {"en": "Driving Licenses (DMT)", "si": "රියදුරු බලපත්‍ර (DMT)", "ta": "ஓட்டுநர் உரிமங்கள் (DMT)"}, "questions": [{"q": {"en": "How to renew license?", "si": "බලපත්‍රය අලුත් කරන්නේ කෙසේද?", "ta": "உரிமத்தை எவ்வாறு புதுப்பிப்பது?"}, "answer": {"en": "Apply at DMT Werahera or online.", "si": "වේරහැර DMT කාර්යාලයට හෝ මාර්ගගතව අයදුම් කරන්න.", "ta": "வேரஹெர DMT அல்லது ஆன்லைனில் விண்ணப்பிக்கவும்."}}]},
                {"id": "railway", "name": {"en": "Railway Services", "si": "දුම්රිය සේවා", "ta": "ரயில் சேவைகள்"}, "questions": [{"q": {"en": "Train tickets online?", "si": "දුම්රිය ටිකට් පත් මාර්ගගතව?", "ta": "ரயில் டிக்கெட்டுகள் ஆன்லைனில்?"}, "answer": {"en": "Visit railway.gov.lk for seat bookings.", "si": "ආසන වෙන්කරවා ගැනීම සඳහා railway.gov.lk වෙත පිවිසෙන්න.", "ta": "இருக்கை முன்பதிவு செய்ய railway.gov.lk ஐப் பார்வையிடவும்."}}]},
                {"id": "bus", "name": {"en": "Public Bus Regulation", "si": "පොදු බස් රථ නියාමනය", "ta": "பொது பஸ் ஒழுங்குமுறை"}, "questions": [{"q": {"en": "Bus route info?", "si": "බස් මාර්ග තොරතුරු?", "ta": "பஸ் வழித்தட தகவல்?"}, "answer": {"en": "Contact NTC for route and fare details.", "si": "මාර්ග සහ ගාස්තු විස්තර සඳහා NTC අමතන්න.", "ta": "வழித்தடம் மற்றும் கட்டண விவரங்களுக்கு NTC ஐ தொடர்பு கொள்ளவும்."}}]},
                {"id": "vehicle_reg", "name": {"en": "Vehicle Registrations", "si": "වාහන ලියාපදිංචි කිරීම්", "ta": "வாகனப் பதிவு"}, "questions": [{"q": {"en": "How to transfer ownership?", "si": "අයිතිය පවරන්නේ කෙසේද?", "ta": "உரிமையை மாற்றுவது எப்படி?"}, "answer": {"en": "Visit DMT with transfer documents.", "si": "මාරු කිරීමේ ලේඛන සමඟ DMT වෙත පිවිසෙන්න.", "ta": "மாற்ற ஆவணங்களுடன் DMT ஐப் பார்வையிடவும்."}}]}
            ]
        },
        {
            "id": "ministry_foreign",
            "name": {"en": "Ministry of Foreign Affairs", "si": "විදේශ කටයුතු අමාත්‍යාංශය", "ta": "வெளிவிவகார அமைச்சு"},
            "contact": {"phone": "0112 323 015", "email": "mfa@gov.lk"},
            "links": [{"title": {"en": "MFA Website", "si": "විදේශ කටයුතු අමාත්‍යාංශය", "ta": "வெளிவிவகார அமைச்சு"}, "url": "https://mfa.gov.lk/"}],
            "subservices": [
                {"id": "consular", "name": {"en": "Consular Services (Attestations)", "si": "කොන්සියුලර් සේවා (සහතික කිරීම්)", "ta": "தூதரக சேவைகள் (சான்றளிப்பு)"}, "questions": [{"q": {"en": "How to attest degree cert?", "si": "උපාධි සහතිකය සහතික කරන්නේ කෙසේද?", "ta": "பட்டச் சான்றிதழை எவ்வாறு சான்றளிப்பது?"}, "answer": {"en": "Book an appointment online and visit MFA.", "si": "මාර්ගගතව පත්වීමක් වෙන් කර MFA වෙත පිවිසෙන්න.", "ta": "ஆன்லைனில் சந்திப்பை முன்பதிவு செய்து MFA ஐப் பார்வையிடவும்."}}]},
                {"id": "pass_abroad", "name": {"en": "Passport Assistance Abroad", "si": "විදේශයන්හි විදේශ ගමන් බලපත්‍ර සහාය", "ta": "வெளிநாடுகளில் கடவுச்சீட்டு உதவி"}, "questions": [{"q": {"en": "Lost passport abroad?", "si": "විදේශයකදී විදේශ ගමන් බලපත්‍රය නැති වුනාද?", "ta": "வெளிநாட்டில் கடவுச்சீட்டு தொலைந்ததா?"}, "answer": {"en": "Contact the nearest Sri Lankan Embassy.", "si": "ළඟම ඇති ශ්‍රී ලංකා තානාපති කාර්යාලය අමතන්න.", "ta": "அருகிலுள்ள இலங்கை தூதரகத்தை தொடர்பு கொள்ளவும்."}}]},
                {"id": "repatriation", "name": {"en": "Repatriation Support", "si": "නැවත පැමිණීමේ සහාය", "ta": "தாயகம் திரும்புவதற்கான ஆதரவு"}, "questions": [{"q": {"en": "Need to come back to SL?", "si": "නැවත ශ්‍රී ලංකාවට පැමිණීමට අවශ්‍යද?", "ta": "இலங்கைக்கு திரும்ப வேண்டுமா?"}, "answer": {"en": "Consult the consular division for emergency travel docs.", "si": "හදිසි ගමන් ලේඛන සඳහා කොන්සියුලර් අංශයෙන් විමසන්න.", "ta": "அவசர பயண ஆவணங்களுக்கு தூதரகப் பிரிவை அணுகவும்."}}]},
                {"id": "diplomatic", "name": {"en": "Diplomatic Relations", "si": "රාජ්‍ය තාන්ත්‍රික සබඳතා", "ta": "ராஜதந்திர உறவுகள்"}, "questions": [{"q": {"en": "Who is the ambassador?", "si": "තානාපති කවුද?", "ta": "தூதுவர் யார்?"}, "answer": {"en": "List of missions available on MFA website.", "si": "MFA වෙබ් අඩවියේ ඇති දූත මණ්ඩල ලැයිස්තුව බලන්න.", "ta": "MFA இணையதளத்தில் கிடைக்கும் பணிகளின் பட்டியல்."}}]}
            ]
        },
        {
            "id": "ministry_agri",
            "name": {"en": "Ministry of Agriculture", "si": "කෘෂිකර්ම අමාත්‍යාංශය", "ta": "விவசாய அமைச்சு"},
            "contact": {"phone": "0112 669 300", "email": "info@agrimin.gov.lk"},
            "links": [{"title": {"en": "Agriculture Ministry", "si": "කෘෂිකර්ම අමාත්‍යාංශය", "ta": "விவசாய அமைச்சு"}, "url": "http://www.agrimin.gov.lk/"}],
            "subservices": [
                {"id": "advisory", "name": {"en": "Farmer Advisory (1920 Center)", "si": "ගොවි උපදේශනය (1920 මධ්‍යස්ථානය)", "ta": "விவசாயிகள் ஆலோசனை (1920 மையம்)"}, "questions": [{"q": {"en": "Pest control tips?", "si": "පළිබෝධ පාලන උපදෙස්?", "ta": "பூச்சி கட்டுப்பாடு குறிப்புகள்?"}, "answer": {"en": "Call 1920 for expert agricultural advice.", "si": "විශේෂඥ කෘෂිකාර්මික උපදෙස් සඳහා 1920 අමතන්න.", "ta": "நிபுணத்துவ விவசாய ஆலோசனைக்கு 1920 ஐ அழைக்கவும்."}}]},
                {"id": "fertilizer", "name": {"en": "Fertilizer Distribution", "si": "පොහොර බෙදා හැරීම", "ta": "உர விநியோகம்"}, "questions": [{"q": {"en": "How to get urea?", "si": "යූරියා ලබා ගන්නේ කෙසේද?", "ta": "யுரியாவை எப்படி பெறுவது?"}, "answer": {"en": "Contact your local Agrarian Service center.", "si": "ඔබේ ප්‍රාදේශීය ගොවිජන සේවා මධ්‍යස්ථානය අමතන්න.", "ta": "உங்கள் உள்ளூர் விவசாய சேவை மையத்தை தொடர்பு கொள்ளவும்."}}]},
                {"id": "certification", "name": {"en": "Seed & Plant Certification", "si": "බීජ හා පැළෑටි සහතික කිරීම", "ta": "விதை மற்றும் தாவர சான்றிதழ்"}, "questions": [{"q": {"en": "Are these seeds certified?", "si": "මෙම බීජ සහතික කර තිබේද?", "ta": "இந்த விதைகள் சான்றளிக்கப்பட்டதா?"}, "answer": {"en": "Verify labels with Department of Agriculture.", "si": "කෘෂිකර්ම දෙපාර්තමේන්තුව සමඟ ලේබල් සත්‍යාපනය කරන්න.", "ta": "விவசாயத் துறையுடன் லேபிள்களைச் சரிபார்க்கவும்."}}]},
                {"id": "insurance", "name": {"en": "Crop Insurance", "si": "බෝග රක්ෂණය", "ta": "பயிர் காப்பீடு"}, "questions": [{"q": {"en": "Insurance for flood damage?", "si": "ගංවතුර හානිය සඳහා රක්ෂණය?", "ta": "வெள்ள சேதத்திற்கான காப்பீடு?"}, "answer": {"en": "Apply via the Agricultural and Agrarian Insurance Board.", "si": "කෘෂිකාර්මික හා ගොවිජන රක්ෂණ මණ්ඩලය හරහා අයදුම් කරන්න.", "ta": "விவசாய மற்றும் விவசாய காப்பீட்டு வாரியம் மூலம் விண்ணப்பிக்கவும்."}}]}
            ]
        },
        {
            "id": "ministry_energy",
            "name": {"en": "Ministry of Power & Energy", "si": "විදුලිබල හා බලශක්ති අමාත්‍යාංශය", "ta": "மின்சக்தி மற்றும் எரிசக்தி அமைச்சு"},
            "contact": {"phone": "0112 370 033", "email": "info@powermin.gov.lk"},
            "links": [{"title": {"en": "Power & Energy", "si": "විදුලිබල හා බලශක්ති", "ta": "மின்சக்தி மற்றும் எரிசக்தி"}, "url": "http://powermin.gov.lk/"}],
            "subservices": [
                {"id": "electricity", "name": {"en": "Electricity Connections", "si": "විදුලි සම්බන්ධතා", "ta": "மின்சார இணைப்புகள்"}, "questions": [{"q": {"en": "Apply for new connection?", "si": "නව සම්බන්ධතාවයක් සඳහා අයදුම් කරනවාද?", "ta": "புதிய இணைப்பிற்கு விண்ணப்பிக்கவா?"}, "answer": {"en": "Submit form at nearest CEB/LECO office.", "si": "ළඟම ඇති CEB/LECO කාර්යාලයට පෝරමය ඉදිරිපත් කරන්න.", "ta": "அருகிலுள்ள CEB/LECO அலுவலகத்தில் படிவத்தைச் சமர்ப்பிக்கவும்."}}]},
                {"id": "fuel", "name": {"en": "Fuel Import & Distribution", "si": "ඉන්ධන ආනයනය සහ බෙදා හැරීම", "ta": "எரிபொருள் இறக்குமதி மற்றும் விநியோகம்"}, "questions": [{"q": {"en": "Fuel availability?", "si": "ඉන්ධන තිබේද?", "ta": "எரிபொருள் கிடைக்குமா?"}, "answer": {"en": "Check CPC updates or fuel shed apps.", "si": "CPC යාවත්කාලීන කිරීම් හෝ ඉන්ධන මඩුවල යෙදුම් පරීක්ෂා කරන්න.", "ta": "CPC புதுப்பிப்புகள் அல்லது எரிபொருள் ஷெட் பயன்பாடுகளைச் சரிபார்க்கவும்."}}]},
                {"id": "renewable", "name": {"en": "Renewable Energy Grants", "si": "පුනර්ජනනීය බලශක්ති ආධාර", "ta": "புதுப்பிக்கத்தக்க எரிசக்தி மானியங்கள்"}, "questions": [{"q": {"en": "Grant for solar panels?", "si": "සූර්ය පැනල සඳහා ආධාර?", "ta": "சூரிய சக்திக்கான மானியம்?"}, "answer": {"en": "Contact SLSEA for available solar schemes.", "si": "පවතින සූර්ය යෝජනා ක්‍රම සඳහා SLSEA අමතන්න.", "ta": "கிடைக்கக்கூடிய சூரிய திட்டங்களுக்கு SLSEA ஐ தொடர்பு கொள்ளவும்."}}]},
                {"id": "utility", "name": {"en": "Utility Bill Management", "si": "බිල්පත් කළමනාකරණය", "ta": "மின்சார கட்டண மேலாண்மை"}, "questions": [{"q": {"en": "Pay bill online?", "si": "බිල මාර්ගගතව ගෙවනවාද?", "ta": "கட்டணத்தை ஆன்லைனில் செலுத்துவதா?"}, "answer": {"en": "Use CEB Care or LECO online portals.", "si": "CEB Care හෝ LECO මාර්ගගත ද්වාර භාවිතා කරන්න.", "ta": "CEB Care அல்லது LECO ஆன்லைன் போர்ட்டல்களைப் பயன்படுத்தவும்."}}]}
            ]
        },
        {
            "id": "ministry_public",
            "name": {"en": "Ministry of Public Administration", "si": "රාජ්‍ය පරිපාලන අමාත්‍යාංශය", "ta": "பொது நிர்வாக அமைச்சு"},
            "contact": {"phone": "0112 696 211", "email": "info@pubad.gov.lk"},
            "links": [{"title": {"en": "Public Admin Website", "si": "රාජ්‍ය පරිපාලන අමාත්‍යාංශය", "ta": "பொது நிர்வாக அமைச்சு"}, "url": "http://www.pubad.gov.lk/"}],
            "subservices": [
                {"id": "admin", "name": {"en": "District/Divisional Admin", "si": "දිස්ත්‍රික්/ප්‍රාදේශීය පරිපාලනය", "ta": "மாவட்ட/பிரதேச நிர்வாகம்"}, "questions": [{"q": {"en": "Who is my Divisional Secretary?", "si": "මගේ ප්‍රාදේශීය ලේකම් කවුද?", "ta": "எனது பிரதேச செயலாளர் யார்?"}, "answer": {"en": "Search by region on the ministry website.", "si": "අමාත්‍යාංශ වෙබ් අඩවියේ කලාපය අනුව සොයන්න.", "ta": "அமைச்சின் இணையதளத்தில் பிராந்தியம் வாரியாக தேடவும்."}}]},
                {"id": "certificates", "name": {"en": "Birth/Marriage Certificates", "si": "උප්පැන්න/විවාහ සහතික", "ta": "பிறப்பு/திருமண சான்றிதழ்கள்"}, "questions": [{"q": {"en": "How to get a copy of birth cert?", "si": "උප්පැන්න සහතිකයේ පිටපතක් ලබා ගන්නේ කෙසේද?", "ta": "பிறப்புச் சான்றிதழின் நகலை எவ்வாறு பெறுவது?"}, "answer": {"en": "Apply at the local Divisional Secretariat.", "si": "ප්‍රාදේශීය ලේකම් කාර්යාලයේ අයදුම් කරන්න.", "ta": "உள்ளூர் பிரதேச செயலகத்தில் விண்ணப்பிக்கவும்."}}]},
                {"id": "pensions", "name": {"en": "Pensions Administration", "si": "විශ්‍රාම වැටුප් පරිපාලනය", "ta": "ஓய்வூதிய நிர்வாகம்"}, "questions": [{"q": {"en": "Pension status check?", "si": "විශ්‍රාම වැටුප් තත්ත්වය පරීක්ෂා කිරීම?", "ta": "ஓய்வூதிய நிலை சரிபார்ப்பு?"}, "answer": {"en": "Use the Department of Pensions online portal.", "si": "විශ්‍රාම වැටුප් දෙපාර්තමේන්තු මාර්ගගත ද්වාරය භාවිතා කරන්න.", "ta": "ஓய்வூதியத் துறை ஆன்லைன் போர்ட்டலைப் பயன்படுத்தவும்."}}]},
                {"id": "grama", "name": {"en": "Grama Niladhari Services", "si": "ග්‍රාම නිලධාරී සේවා", "ta": "கிராம நிலதாரி சேவைகள்"}, "questions": [{"q": {"en": "Need GN character cert?", "si": "ග්‍රාම නිලධාරී චරිත සහතිකය අවශ්‍යද?", "ta": "கிராம நிலதாரி நடத்தை சான்றிதழ் வேண்டுமா?"}, "answer": {"en": "Contact your local GN with identity proof.", "si": "අනන්‍යතා සාධක සමඟ ඔබේ ප්‍රාදේශීය ග්‍රාම නිලධාරී අමතන්න.", "ta": "அடையாளச் சான்றுடன் உங்கள் உள்ளூர் கிராம நிலதாரியைத் தொடர்பு கொள்ளவும்."}}]}
            ]
        },
        {
            "id": "ministry_defence",
            "name": {"en": "Ministry of Defence", "si": "ආරක්ෂක අමාත්‍යාංශය", "ta": "பாதுகாப்பு அமைச்சு"},
            "contact": {"phone": "0112 430 860", "email": "info@defence.lk"},
            "links": [{"title": {"en": "Defence Website", "si": "ආරක්ෂක අමාත්‍යාංශය", "ta": "பாதுகாப்பு அமைச்சு"}, "url": "http://www.defence.lk/"}],
            "subservices": [
                {"id": "security", "name": {"en": "National Security", "si": "ජාතික ආරක්ෂාව", "ta": "தேசிய பாதுகாப்பு"}, "questions": [{"q": {"en": "Latest security updates?", "si": "නවතම ආරක්ෂක තොරතුරු?", "ta": "சமீபத்திய பாதுகாப்பு புதுப்பிப்புகள்?"}, "answer": {"en": "Follow the official MOD news portal.", "si": "නිල MOD පුවත් ද්වාරය අනුගමනය කරන්න.", "ta": "அதிகாரப்பூர்வ MOD செய்தி போர்ட்டலைப் பின்தொடரவும்."}}]},
                {"id": "civil", "name": {"en": "Civil Defense", "si": "සිවිල් ආරක්ෂාව", "ta": "சிவில் பாதுகாப்பு"}, "questions": [{"q": {"en": "Civil Defense services?", "si": "සිවිල් ආරක්ෂක සේවා?", "ta": "சிவில் பாதுகாப்பு சேவைகள்?"}, "answer": {"en": "Refer to the CSD official website.", "si": "CSD නිල වෙබ් අඩවිය බලන්න.", "ta": "CSD அதிகாரப்பூர்வ வலைத்தளத்தைப் பார்க்கவும்."}}]},
                {"id": "coast", "name": {"en": "Coast Guard Monitoring", "si": "වෙරළාරක්ෂක නිරීක්ෂණ", "ta": "கடலோர காவல்படை கண்காணிப்பு"}, "questions": [{"q": {"en": "Report sea pollution?", "si": "මුහුදු දූෂණය වාර්තා කරනවාද?", "ta": "கடல் மாசுபாட்டைப் புகாரளிப்பதா?"}, "answer": {"en": "Notify Sri Lanka Coast Guard immediately.", "si": "වහාම ශ්‍රී ලංකා වෙරළාරක්ෂක බලකායට දන්වන්න.", "ta": "இலங்கை கடலோர காவல்படைக்கு உடனடியாக அறிவிக்கவும்."}}]},
                {"id": "immigration", "name": {"en": "Immigration & Emigration", "si": "ආගමන හා විගමන", "ta": "குடிவரவு மற்றும் குடியகல்வு"}, "questions": [{"q": {"en": "Apply for visa?", "si": "වීසා සඳහා අයදුම් කරනවාද?", "ta": "விசாவிற்கு விண்ணப்பிப்பதா?"}, "answer": {"en": "Visit immigration.gov.lk or eta.gov.lk.", "si": "immigration.gov.lk හෝ eta.gov.lk වෙත පිවිසෙන්න.", "ta": "immigration.gov.lk அல்லது eta.gov.lk ஐப் பார்வையிடவும்."}}]}
            ]
        },
        {
            "id": "ministry_justice",
            "name": {"en": "Ministry of Justice", "si": "අධිකරණ අමාත්‍යාංශය", "ta": "நீதி அமைச்சு"},
            "contact": {"phone": "0112 323 026", "email": "info@justice.gov.lk"},
            "links": [{"title": {"en": "Justice Ministry", "si": "අධිකරණ අමාත්‍යාංශය", "ta": "நீதி அமைச்சு"}, "url": "http://www.justice.gov.lk/"}],
            "subservices": [
                {"id": "legal_infra", "name": {"en": "Legal Infrastructure", "si": "නීතිමය යටිතල පහසුකම්", "ta": "சட்ட உள்கட்டமைப்பு"}, "questions": [{"q": {"en": "Where is the court located?", "si": "උසාවිය පිහිටා ඇත්තේ කොහේද?", "ta": "நீதிமன்றம் எங்கே அமைந்துள்ளது?"}, "answer": {"en": "Search the court directory on the ministry website.", "si": "අමාත්‍යාංශ වෙබ් අඩවියේ උසාවි නාමාවලිය සොයන්න.", "ta": "அமைச்சின் இணையதளத்தில் நீதிமன்ற விபரங்களைத் தேடவும்."}}]},
                {"id": "mediation", "name": {"en": "Mediation Boards", "si": "සමථ මණ්ඩල", "ta": "சமரச சபைகள்"}, "questions": [{"q": {"en": "How to file a mediation case?", "si": "සමථකරණ නඩුවක් ගොනු කරන්නේ කෙසේද?", "ta": "சமரசம் செய்வது எப்படி?"}, "answer": {"en": "Visit your local Mediation Board office.", "si": "ඔබේ ප්‍රාදේශීය සමථ මණ්ඩල කාර්යාලයට පැමිණෙන්න.", "ta": "உங்கள் உள்ளூர் சமரச சபையின் அலுவலகத்தைப் பார்வையிடவும்."}}]},
                {"id": "ag_services", "name": {"en": "Attorney General Services", "si": "නීතිපති සේවා", "ta": "சட்டமா அதிபர் சேவைகள்"}, "questions": [{"q": {"en": "Role of AG?", "si": "නීතිපතිගේ කාර්යභාරය?", "ta": "சட்டமா அதிபரின் பங்கு?"}, "answer": {"en": "The AG acts as the chief legal advisor to the state.", "si": "නීතිපතිවරයා රජයේ ප්‍රධාන නීති උපදේශකවරයා ලෙස කටයුතු කරයි.", "ta": "சட்டமா அதிபர் அரசின் தலைமை சட்ட ஆலோசகராக செயல்படுகிறார்."}}]},
                {"id": "legal_aid", "name": {"en": "Legal Aid for Citizens", "si": "පුරවැසියන් සඳහා නීති ආධාර", "ta": "குடிமக்களுக்கான சட்ட உதவி"}, "questions": [{"q": {"en": "Free legal consultation?", "si": "නොමිලේ නීති උපදෙස්?", "ta": "இலவச சட்ட ஆலோசனை?"}, "answer": {"en": "Contact the Legal Aid Commission.", "si": "නීති ආධාර කොමිෂන් සභාව අමතන්න.", "ta": "சட்ட உதவி ஆணைக்குழுவைத் தொடர்பு கொள்ளவும்."}}]}
            ]
        },
        {
            "id": "ministry_industries",
            "name": {"en": "Ministry of Industries", "si": "කර්මාන්ත අමාත්‍යාංශය", "ta": "தொழில் அமைச்சு"},
            "contact": {"phone": "0112 392 149", "email": "info@industry.gov.lk"},
            "links": [{"title": {"en": "Industry Website", "si": "කර්මාන්ත අමාත්‍යාංශය", "ta": "தொழில் அமைச்சு"}, "url": "http://www.industry.gov.lk/"}],
            "subservices": [
                {"id": "sme", "name": {"en": "SME Support & Grants", "si": "SME සහාය සහ ආධාර", "ta": "சிறு நடுத்தர தொழில் ஆதரவு மற்றும் மானியங்கள்"}, "questions": [{"q": {"en": "How to get a startup grant?", "si": "ආරම්භක ආධාර ලබා ගන්නේ කෙසේද?", "ta": "தொடக்க மானியத்தை எவ்வாறு பெறுவது?"}, "answer": {"en": "Apply via the SME development division.", "si": "SME සංවර්ධන අංශය හරහා අයදුම් කරන්න.", "ta": "சிறு நடுத்தர தொழில் வளர்ச்சிப் பிரிவு மூலம் விண்ணப்பிக்கவும்."}}]},
                {"id": "industrial_parks", "name": {"en": "Industrial Park Management", "si": "කර්මාන්ත උද්‍යාන කළමනාකරණය", "ta": "தொழில் பூங்கா மேலாண்மை"}, "questions": [{"q": {"en": "Lease land for factory?", "si": "කර්මාන්ත ශාලාවකට ඉඩම් බදු දෙනවාද?", "ta": "தொழிற்சாலைக்கு நிலத்தை குத்தகைக்கு விடுவதா?"}, "answer": {"en": "Contact the Industrial Development Board.", "si": "කර්මාන්ත සංවර්ධන මණ්ඩලය අමතන්න.", "ta": "தொழில் மேம்பாட்டு வாரியத்தை தொடர்பு கொள்ளவும்."}}]},
                {"id": "entrepreneur", "name": {"en": "Entrepreneur Training", "si": "ව්‍යවසායක පුහුණුව", "ta": "தொழில்முனைவோர் பயிற்சி"}, "questions": [{"q": {"en": "Available training programs?", "si": "පවතින පුහුණු වැඩසටහන්?", "ta": "கிடைக்கக்கூடிய பயிற்சி திட்டங்கள்?"}, "answer": {"en": "Register for courses at IDB or SLSI.", "si": "IDB හෝ SLSI හි පාඨමාලා සඳහා ලියාපදිංචි වන්න.", "ta": "IDB அல்லது SLSI இல் படிப்புகளுக்கு பதிவு செய்யவும்."}}]},
                {"id": "standards", "name": {"en": "Standards & Licensing", "si": "ප්‍රමිති සහ බලපත්‍ර ලබා දීම", "ta": "தரநிலைகள் மற்றும் உரிமம்"}, "questions": [{"q": {"en": "How to get SLS mark?", "si": "SLS ලකුණ ලබා ගන්නේ කෙසේද?", "ta": "SLS முத்திரையை எவ்வாறு பெறுவது?"}, "answer": {"en": "Apply at Sri Lanka Standards Institution.", "si": "ශ්‍රී ලංකා ප්‍රමිති ආයතනයට අයදුම් කරන්න.", "ta": "இலங்கை தரநிர்ணய நிறுவனத்தில் விண்ணப்பிக்கவும்."}}]}
            ]
        },
        {
            "id": "ministry_tourism",
            "name": {"en": "Ministry of Tourism", "si": "සංචාරක අමාත්‍යාංශය", "ta": "சுற்றுலா அமைச்சு"},
            "contact": {"phone": "0112 437 055", "email": "info@tourismmin.gov.lk"},
            "links": [{"title": {"en": "Tourism Ministry", "si": "සංචාරක අමාත්‍යාංශය", "ta": "சுற்றுலா அமைச்சு"}, "url": "http://www.tourismmin.gov.lk/"}],
            "subservices": [
                {"id": "police", "name": {"en": "Tourist Police Services", "si": "සංචාරක පොලිස් සේවා", "ta": "சுற்றுலா பொலிஸ் சேவைகள்"}, "questions": [{"q": {"en": "Emergency contact for tourists?", "si": "සංචාරකයින් සඳහා හදිසි ඇමතුම් අංකය?", "ta": "சுற்றுலாப் பயணிகளுக்கான அவசர தொடர்பு எண்?"}, "answer": {"en": "Call 1912 for tourist assistance.", "si": "සංචාරක සහාය සඳහා 1912 අමතන්න.", "ta": "சுற்றுலா உதவிக்கு 1912 ஐ அழைக்கவும்."}}]},
                {"id": "licensing", "name": {"en": "Hotel Licensing", "si": "හෝටල් බලපත්‍ර ලබා දීම", "ta": "ஹோட்டல் உரிமம்"}, "questions": [{"q": {"en": "How to register a homestay?", "si": "homestay එකක් ලියාපදිංචි කරන්නේ කෙසේද?", "ta": "ஹோம்ஸ்டேவை எவ்வாறு பதிவு செய்வது?"}, "answer": {"en": "Register via the SLTDA portal.", "si": "SLTDA ද්වාරය හරහා ලියාපදිංචි වන්න.", "ta": "SLTDA போர்டல் மூலம் பதிவு செய்யவும்."}}]},
                {"id": "marketing", "name": {"en": "Destination Marketing", "si": "සංචාරක ප්‍රවර්ධනය", "ta": "இலக்கு சந்தைப்படுத்தல்"}, "questions": [{"q": {"en": "Where to find travel guides?", "si": "සංචාරක මාර්ගෝපදේශ සොයා ගන්නේ කොහෙන්ද?", "ta": "சுற்றுலா வழிகாட்டிகளை எங்கே காணலாம்?"}, "answer": {"en": "Check srilanka.travel for official info.", "si": "නිල තොරතුරු සඳහා srilanka.travel පරීක්ෂා කරන්න.", "ta": "அதிகாரப்பூர்வ தகவலுக்கு srilanka.travel ஐப் பார்க்கவும்."}}]},
                {"id": "certification_guide", "name": {"en": "Travel Guide Certification", "si": "සංචාරක මාර්ගෝපදේශක සහතික කිරීම", "ta": "பயண வழிகாட்டி சான்றிதழ்"}, "questions": [{"q": {"en": "Apply for guide license?", "si": "මාර්ගෝපදේශක බලපත්‍රය සඳහා අයදුම් කරනවාද?", "ta": "வழிகாட்டி உரிமத்திற்கு விண்ணப்பிப்பதா?"}, "answer": {"en": "Follow the SLTDA training and exam process.", "si": "SLTDA පුහුණු හා විභාග ක්‍රියාවලිය අනුගමනය කරන්න.", "ta": "SLTDA பயிற்சி மற்றும் தேர்வு செயல்முறையைப் பின்பற்றவும்."}}]}
            ]
        }
    ]

    services_col.insert_many(docs)
    print(f"Seeded {len(docs)} ministries with EXACT requested hierarchical structure.")
    
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
