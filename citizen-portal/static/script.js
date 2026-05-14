document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const ministryList = document.getElementById('ministry-list');
    const welcomeScreen = document.getElementById('welcome-screen');
    const ministryDetails = document.getElementById('ministry-details');
    const servicesGrid = document.getElementById('services-list');
    const faqList = document.getElementById('faq-list');
    const ministryName = document.getElementById('selected-ministry-name');
    const ministryDesc = document.getElementById('selected-ministry-desc');
    
    

    const engagementForm = document.getElementById('engagement-form');
    const authBtn = document.getElementById('auth-btn');
    const authModal = document.getElementById('auth-modal');
    const userDisplay = document.getElementById('user-display');
    const usernameSpan = document.getElementById('username-span');
    const logoutBtn = document.getElementById('logout-btn');
    
    // Clock
    const clockEl = document.getElementById('sl-clock');

    // Profile Elements
    const profileTrigger = document.getElementById('profile-trigger');
    const profileModal = document.getElementById('profile-modal');
    const profileUsername = document.getElementById('profile-username');
    const closeProfileBtn = document.getElementById('close-profile');
    
    // Auth Modal Elements
    const authForm = document.getElementById('auth-form');
    const tabLogin = document.getElementById('tab-login');
    const tabSignup = document.getElementById('tab-signup');
    const authSubmitBtn = document.getElementById('auth-submit-btn');
    const closeModal = document.getElementById('close-modal');
    
    let currentMode = 'login';
    let currentLang = 'en';
    let allMinistries = [];
    let currentSelectedMinistry = null;

    // --- 1. Clock Logic (Sri Lanka UTC+5:30) ---
    function updateClock() {
        const now = new Date();
        const options = {
            timeZone: 'Asia/Colombo',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        };
        const slTime = new Intl.DateTimeFormat('en-US', options).format(now);
        clockEl.textContent = `Sri Lanka: ${slTime}`;
    }
    setInterval(updateClock, 1000);
    updateClock();

    // --- 2. Language Support ---
    const i18n = {
        en: { ministries: "Ministries", welcome_title: "Welcome to the Citizen Services Portal", welcome_desc: "Select a ministry from the sidebar to view available services and common questions.", services: "Services", available_services: "Available Services", faqs: "Frequently Asked Questions", ai_assistant: "Gemini AI Assistant", close: "Close Assistant", citizen_engagement: "Citizen Engagement", engagement_desc: "Tell us more about yourself to personalize your experience.", age: "Age", job: "Occupation", interest: "Primary Interest", update_profile: "Update Profile", healthcare: "Healthcare", education: "Education", employment: "Employment" },
        si: { ministries: "අමාත්‍යාංශ", welcome_title: "පුරවැසි සේවා ද්වාරය වෙත සාදරයෙන් පිළිගනිමු", welcome_desc: "පවතින සේවාවන් සහ පොදු ප්‍රශ්න බැලීමට පැති තීරුවෙන් අමාත්‍යාංශයක් තෝරන්න.", services: "සේවා", available_services: "පවතින සේවාවන්", faqs: "නිතර අසන පැන", ai_assistant: "Gemini AI සහායකයා", close: "සහායකයා වසන්න", citizen_engagement: "පුරවැසි සම්බන්ධතාවය", engagement_desc: "ඔබේ අත්දැකීම් පුද්ගලීකරණය කිරීමට ඔබ ගැන අපට තව කියන්න.", age: "වයස", job: "රැකියාව", interest: "ප්‍රධාන උනන්දුව", update_profile: "පැතිකඩ යාවත්කාලීන කරන්න", healthcare: "සෞඛ්‍ය සේවය", education: "අධ්‍යාපනය", employment: "රැකියා" },
        ta: { ministries: "அமைச்சகங்கள்", welcome_title: "குடிமக்கள் சேவை போர்ட்டலுக்கு வரவேற்கிறோம்", welcome_desc: "கிடைக்கக்கூடிய சேவைகள் மற்றும் பொதுவான கேள்விகளைக் காண பக்கப்பட்டியில் இருந்து ஒரு அமைச்சகத்தைத் தேர்ந்தெடுக்கவும்.", services: "சேவைகள்", available_services: "கிடைக்கக்கூடிய சேவைகள்", faqs: "அடிக்கடி கேட்கப்படும் கேள்விகள்", ai_assistant: "ஜெமினி AI உதவியாளர்", close: "உதவியாளரை மூடு", citizen_engagement: "குடிமக்கள் ஈடுபாடு", engagement_desc: "உங்கள் அனுபவத்தைத் தனிப்பயனாக்க உங்களைப் பற்றி மேலும் எங்களிடம் கூறுங்கள்.", age: "வயது", job: "தொழில்", interest: "முதன்மை ஆர்வம்", update_profile: "சுயவிவரத்தைப் புதுப்பிக்கவும்", healthcare: "சுகாதாரம்", education: "கல்வி", employment: "வேலைவாய்ப்பு" }
    };

    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            currentLang = btn.dataset.lang;
            document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            updateUIStrings();
            if (currentSelectedMinistry) renderMinistryDetails(currentSelectedMinistry);
            renderMinistryList();
        });
    });

    function updateUIStrings() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.dataset.i18n;
            el.textContent = i18n[currentLang][key] || el.textContent;
        });
    }

    async function translateDynamic(content) {
        if (typeof content === 'string') return content;
        if (content && content[currentLang]) {
            return content[currentLang];
        } else if (content && content['en']) {
            return content['en'];
        }
        return "Not available";
    }

    // --- 3. Data Loading ---
    async function fetchMinistries() {
        const res = await fetch('/api/services');
        allMinistries = await res.json();
        renderMinistryList();
    }

    async function renderMinistryList() {
        ministryList.innerHTML = '';
        for (const m of allMinistries) {
            const li = document.createElement('li');
            li.textContent = await translateDynamic(m.name);
            li.addEventListener('click', () => {
                currentSelectedMinistry = m;
                renderMinistryDetails(m);
                document.querySelectorAll('#ministry-list li').forEach(el => el.classList.remove('active'));
                li.classList.add('active');
            });
            ministryList.appendChild(li);
        }
    }

    async function renderMinistryDetails(m) {
        welcomeScreen.classList.add('hidden');
        ministryDetails.classList.remove('hidden');
        ministryName.textContent = await translateDynamic(m.name);
        // User data might not have top-level description, check for it
        ministryDesc.textContent = m.description ? await translateDynamic(m.description) : "";
        
        // Add Contact and Links section
        let infoHtml = '';
        if (m.contact) {
            infoHtml += `
                <div class="contact-info-box">
                    <h4><i class="fas fa-address-book"></i> Contact Information</h4>
                    <p><strong>Phone:</strong> ${m.contact.phone || 'N/A'}</p>
                    <p><strong>Email:</strong> ${m.contact.email || 'N/A'}</p>
                </div>
            `;
        }
        
        if (m.links && m.links.length > 0) {
            infoHtml += `<div class="useful-links-box"><h4><i class="fas fa-external-link-alt"></i> Useful Links</h4><div class="links-grid">`;
            for (const link of m.links) {
                const linkTitle = await translateDynamic(link.title);
                infoHtml += `<button class="btn-link" onclick="window.open('${link.url}', '_blank')">${linkTitle}</button>`;
            }
            infoHtml += `</div></div>`;
        }
        
        // Create a container for info if it doesn't exist or just prepend it
        let infoContainer = document.getElementById('ministry-info-extra');
        if (!infoContainer) {
            infoContainer = document.createElement('div');
            infoContainer.id = 'ministry-info-extra';
            ministryDesc.after(infoContainer);
        }
        infoContainer.innerHTML = infoHtml;

        servicesGrid.innerHTML = '';
        faqList.innerHTML = ''; // Clear FAQs initially
        
        const subservices = m.subservices || [];
        for (const s of subservices) {
            const btn = document.createElement('button');
            btn.className = 'service-btn';
            const translatedName = await translateDynamic(s.name);
            btn.innerHTML = `<i class="fas fa-external-link-alt"></i> ${translatedName}`;
            
            btn.onclick = () => {
                const url = (m.links && m.links[0]) ? m.links[0].url : 'https://www.gov.lk';
                window.open(url, '_blank');
            };
            servicesGrid.appendChild(btn);
        }
        
        // No auto-select needed for external links
    }

    async function renderSubserviceQuestions(s) {
        faqList.innerHTML = '';
        const questions = s.questions || [];
        for (const f of questions) {
            const div = document.createElement('div');
            div.className = 'faq-item';
            
            const q = await translateDynamic(f.q);
            const a = await translateDynamic(f.answer);
            
            let extraInfo = '';
            if (f.instructions) extraInfo += `<p class="instructions"><strong>Instructions:</strong> ${f.instructions}</p>`;
            if (f.location) extraInfo += `<p class="location"><a href="${f.location}" target="_blank"><i class="fas fa-map-marker-alt"></i> Location Map</a></p>`;
            
            div.innerHTML = `<h4>${q}</h4><p>${a}</p>${extraInfo}`;
            faqList.appendChild(div);
        }
    }

    // --- 4. Auth & Profile Logic ---
    authBtn.addEventListener('click', () => authModal.classList.remove('hidden'));
    closeModal.addEventListener('click', () => authModal.classList.add('hidden'));
    
    // Profile Modal
    profileTrigger.addEventListener('click', () => {
        const user = localStorage.getItem('user');
        if (user) {
            profileUsername.textContent = user;
            profileModal.classList.remove('hidden');
        }
    });
    closeProfileBtn.addEventListener('click', () => profileModal.classList.add('hidden'));

    tabLogin.addEventListener('click', () => {
        currentMode = 'login';
        tabLogin.classList.add('active');
        tabSignup.classList.remove('active');
        authSubmitBtn.textContent = 'Login';
    });

    tabSignup.addEventListener('click', () => {
        currentMode = 'signup';
        tabSignup.classList.add('active');
        tabLogin.classList.remove('active');
        authSubmitBtn.textContent = 'Sign Up';
    });

    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('auth-username').value;
        const password = document.getElementById('auth-password').value;
        const endpoint = currentMode === 'login' ? '/api/auth/login' : '/api/auth/register';

        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (res.ok) {
            const data = await res.json();
            if (currentMode === 'login') {
                localStorage.setItem('user', data.username);
                alert('Login successful!');
                updateAuthUI();
                authModal.classList.add('hidden');
            } else {
                alert('Account created! Please login.');
                tabLogin.click();
            }
        } else {
            const errorData = await res.json();
            alert(errorData.error || 'Authentication failed');
        }
    });

    function updateAuthUI() {
        const user = localStorage.getItem('user');
        if (user) {
            authBtn.classList.add('hidden');
            userDisplay.classList.remove('hidden');
            usernameSpan.textContent = user;
            // Update profile image if needed
            document.getElementById('profile-img').src = `https://ui-avatars.com/api/?name=${user}&background=random`;
        } else {
            authBtn.classList.remove('hidden');
            userDisplay.classList.add('hidden');
        }
    }

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('user');
        updateAuthUI();
    });

    // --- 5. Engagement ---

    engagementForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            age: document.getElementById('age').value,
            job: document.getElementById('job').value,
            interest: document.getElementById('interest').value,
            timestamp: new Date().toISOString()
        };
        await fetch('/api/engagement', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        alert('Data Saved!');
    });

    

    // --- AI Chat Bubble Logic ---
    const chatBubble = document.getElementById('chat-bubble');
    const chatWindow = document.getElementById('chat-window');
    const closeChat = document.getElementById('close-chat');
    const sendChat = document.getElementById('send-chat');
    const chatInput = document.getElementById('user-chat-input');
    const chatMessages = document.getElementById('chat-messages');

    chatBubble.addEventListener('click', () => {
        chatWindow.classList.toggle('hidden');
    });

    closeChat.addEventListener('click', () => {
        chatWindow.classList.add('hidden');
    });

    async function handleChat() {
        const prompt = chatInput.value.trim();
        if (!prompt) return;

        // Display user message
        addMessage('user', prompt);
        chatInput.value = '';

        // Typing indicator
        const typingId = addMessage('ai typing', 'Typing...');

        try {
            const res = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });
            const data = await res.json();
            
            // Remove typing indicator
            const typingEl = document.getElementById(typingId);
            if (typingEl) typingEl.remove();

            if (data.response) {
                addMessage('ai', data.response);
            } else {
                addMessage('ai', "Sorry, I'm having trouble connecting right now.");
            }
        } catch (error) {
            const typingEl = document.getElementById(typingId);
            if (typingEl) typingEl.remove();
            addMessage('ai', "Error: Could not reach the server.");
        }
    }

    function addMessage(role, text) {
        const div = document.createElement('div');
        const id = 'msg-' + Date.now();
        div.id = id;
        div.className = `message ${role}`;
        div.textContent = text;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    sendChat.addEventListener('click', handleChat);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleChat();
    });

    fetchMinistries();
    updateAuthUI();
});
