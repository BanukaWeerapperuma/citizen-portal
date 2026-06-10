/**
 * Citizen Services Portal – script.js  (Task 07)
 * ─────────────────────────────────────────────────
 * Vanilla JS SPA controller:
 *   • Multilingual rendering  (EN / SI / TA)
 *   • Category → Subservice → Question drill-down
 *   • AI chat panel + autosuggest typeahead
 *   • Progressive profile modal (3 steps)
 *   • Ad carousel in sidebar
 */

// ═══════════════════════════════════════════════════════════════
// 1. GLOBAL STATE
// ═══════════════════════════════════════════════════════════════

let currentLang        = localStorage.getItem('lang') || 'en';
let selectedCategoryId = null;
let profileId          = localStorage.getItem('profileId') || null;

// Local data caches
let categories = [];
let services   = [];
let ads        = [];

// Pending action to resume after profile submission
let _pendingAction = null;


// ═══════════════════════════════════════════════════════════════
// 2. INITIALISATION
// ═══════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', init);

async function init() {
    try {
        // Fetch services (= categories/ministries)
        const svcRes = await fetch('/api/services');
        if (!svcRes.ok) throw new Error('Failed to load services');
        services = await svcRes.json();

        // Build category list from services (each top-level service IS a category)
        categories = services;

        renderCategories();
        renderAds();
        setLang(currentLang);          // Honour saved language
        syncLangButtons();

        // Wire search input on the main pane
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', e => {
                autosuggest(e.target.value);
            });
            searchInput.addEventListener('keydown', e => {
                if (e.key === 'Enter') openChat();
            });
        }
    } catch (err) {
        console.error('[init]', err);
    }
}


// ═══════════════════════════════════════════════════════════════
// 2b. AD CAROUSEL
// ═══════════════════════════════════════════════════════════════

async function renderAds() {
    const adsArea = document.getElementById('ads-area');
    if (!adsArea) return;

    try {
        const res = await fetch('/api/admin/ads', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('adminToken') || 'none'}` }
        });

        if (res.ok) {
            ads = await res.json();
        }
    } catch (_) {
        // Ads are non-critical – fail silently
    }

    if (!ads.length) {
        adsArea.innerHTML = `
            <div class="ad-card">
                <p>📢 Access government services quickly.<br>
                   Use the <strong>AI Assistant</strong> to ask questions in your language.</p>
            </div>`;
        return;
    }

    // Cycle through ads every 5 s
    let adIndex = 0;
    function showAd() {
        const ad = ads[adIndex % ads.length];
        adIndex++;
        const title  = getLocalized(ad.title)  || ad.title  || 'Announcement';
        const body   = getLocalized(ad.body)   || ad.body   || '';
        const imgSrc = ad.image || null;
        const link   = ad.link  || null;

        adsArea.innerHTML = `
            <div class="ad-card">
                ${imgSrc ? `<img src="${imgSrc}" alt="${title}" class="ad-img">` : ''}
                <p class="ad-title">${title}</p>
                ${body ? `<p class="ad-body">${body}</p>` : ''}
                ${link ? `<a href="${link}" target="_blank" class="ad-link">Learn more →</a>` : ''}
            </div>`;
    }

    showAd();
    setInterval(showAd, 5000);
}


// ═══════════════════════════════════════════════════════════════
// 3. MULTILINGUAL ENGINE
// ═══════════════════════════════════════════════════════════════

/**
 * Return the localised string from a multilingual object.
 * Falls back: target lang → 'en' → raw string.
 */
function getLocalized(obj) {
    if (!obj) return '';
    if (typeof obj === 'string') return obj;
    return obj[currentLang] || obj['en'] || Object.values(obj)[0] || '';
}

function setLang(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    syncLangButtons();

    // Re-render visible content in new language
    if (selectedCategoryId) {
        renderSubservices();
    }
    renderCategories();
}

function syncLangButtons() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
        const btnLang = btn.getAttribute('onclick')?.match(/setLang\('(\w+)'\)/)?.[1];
        if (btnLang) {
            btn.classList.toggle('active', btnLang === currentLang);
            btn.setAttribute('aria-pressed', String(btnLang === currentLang));
        }
    });
}


// ═══════════════════════════════════════════════════════════════
// 4. CATEGORY → SUBSERVICE → QUESTION DRILL-DOWN
// ═══════════════════════════════════════════════════════════════

function renderCategories() {
    const container = document.getElementById('category-list');
    if (!container) return;
    container.innerHTML = '';

    categories.forEach(cat => {
        const name = getLocalized(cat.name) || cat.id || 'Unknown';

        const btn = document.createElement('button');
        btn.className   = 'cat-btn' + (cat.id === selectedCategoryId ? ' active' : '');
        btn.textContent = name;
        btn.role        = 'listitem';
        btn.setAttribute('aria-pressed', String(cat.id === selectedCategoryId));

        btn.addEventListener('click', () => {
            selectedCategoryId = cat.id;
            renderCategories();      // Refresh active state
            renderSubservices();
        });

        container.appendChild(btn);
    });
}

function renderSubservices() {
    const subList = document.getElementById('sub-list');
    const subTitle = document.getElementById('sub-title');
    if (!subList) return;
    subList.innerHTML = '';

    const service = services.find(s => s.id === selectedCategoryId);
    if (!service) return;

    const catName = getLocalized(service.name);
    if (subTitle) subTitle.textContent = catName;

    const subservices = service.subservices || [];
    subservices.forEach(sub => {
        const name = getLocalized(sub.name) || sub.id || 'Subservice';

        const li = document.createElement('li');
        li.className = 'sub-item';
        li.innerHTML = `<i class="fas fa-chevron-right" aria-hidden="true"></i> ${name}`;
        li.setAttribute('role', 'listitem');

        li.addEventListener('click', () => {
            document.querySelectorAll('.sub-item').forEach(el => el.classList.remove('active'));
            li.classList.add('active');
            renderQuestions(service.id, sub.id);
        });

        subList.appendChild(li);
    });

    // Clear question/answer pane when switching category
    const qList  = document.getElementById('question-list');
    const ansBox = document.getElementById('answer-box');
    if (qList) qList.innerHTML = '';
    if (ansBox) ansBox.innerHTML = '';
    const qTitle = document.getElementById('q-title');
    if (qTitle) qTitle.textContent = 'Select Question';
}

function renderQuestions(serviceId, subserviceId) {
    const qList  = document.getElementById('question-list');
    const qTitle = document.getElementById('q-title');
    const ansBox = document.getElementById('answer-box');
    if (!qList) return;
    qList.innerHTML = '';
    if (ansBox) ansBox.innerHTML = '';

    const service    = services.find(s => s.id === serviceId);
    if (!service) return;
    const subservice = (service.subservices || []).find(s => s.id === subserviceId);
    if (!subservice) return;

    const subName = getLocalized(subservice.name);
    if (qTitle) qTitle.textContent = subName;

    const questions = subservice.questions || [];
    questions.forEach((qObj, idx) => {
        const qText = getLocalized(qObj.q) || `Question ${idx + 1}`;

        const li = document.createElement('li');
        li.className = 'q-item';
        li.setAttribute('role', 'listitem');
        li.innerHTML = `<span class="q-num">${idx + 1}</span> ${qText}`;

        li.addEventListener('click', () => {
            document.querySelectorAll('.q-item').forEach(el => el.classList.remove('active'));
            li.classList.add('active');
            showAnswer(qObj, service);
            trackClick(serviceId, subserviceId, qText);
        });

        qList.appendChild(li);
    });
}

function showAnswer(qObj, service) {
    const ansBox = document.getElementById('answer-box');
    if (!ansBox) return;

    const answer       = getLocalized(qObj.answer)       || 'No information available.';
    const instructions = getLocalized(qObj.instructions) || '';
    const location     = qObj.location  || '';
    const downloads    = qObj.downloads || [];
    const contact      = service?.contact || {};
    const links        = service?.links   || [];

    let html = `
        <div class="answer-card">
            <div class="answer-text">
                <i class="fas fa-info-circle" aria-hidden="true"></i>
                <p>${answer}</p>
            </div>`;

    if (instructions) {
        html += `
            <div class="answer-instructions">
                <h4><i class="fas fa-list-ol" aria-hidden="true"></i> Instructions</h4>
                <p>${instructions}</p>
            </div>`;
    }

    if (location) {
        html += `
            <a href="${location}" target="_blank" rel="noopener" class="answer-location"
               onclick="triggerProfileCheck(this)">
                <i class="fas fa-map-marker-alt" aria-hidden="true"></i> View Location Map
            </a>`;
    }

    if (downloads.length) {
        html += `<div class="answer-downloads"><h4><i class="fas fa-paperclip" aria-hidden="true"></i> Downloads</h4>`;
        downloads.forEach(dl => {
            const dlName = getLocalized(dl.name) || dl.url || 'Download';
            html += `
                <a href="${dl.url}" target="_blank" rel="noopener" class="dl-link"
                   onclick="triggerProfileCheck(this)">
                    <i class="fas fa-file-download" aria-hidden="true"></i> ${dlName}
                </a>`;
        });
        html += `</div>`;
    }

    if (contact.phone || contact.email) {
        html += `
            <div class="answer-contact">
                <h4><i class="fas fa-address-book" aria-hidden="true"></i> Contact</h4>
                ${contact.phone ? `<p><i class="fas fa-phone"></i> ${contact.phone}</p>` : ''}
                ${contact.email ? `<p><i class="fas fa-envelope"></i> ${contact.email}</p>` : ''}
            </div>`;
    }

    if (links.length) {
        const linkBtns = links.map(l => {
            const lTitle = getLocalized(l.title) || l.url;
            return `<a href="${l.url}" target="_blank" rel="noopener" class="btn-link">
                        <i class="fas fa-external-link-alt" aria-hidden="true"></i> ${lTitle}
                    </a>`;
        }).join('');
        html += `<div class="answer-links">${linkBtns}</div>`;
    }

    html += `</div>`;
    ansBox.innerHTML = html;
    ansBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function trackClick(serviceId, subserviceId, questionText) {
    try {
        await fetch('/api/analytics/click', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id:          profileId || 'anonymous',
                service:          serviceId,
                subservice:       subserviceId,
                question_clicked: questionText,
                timestamp:        new Date().toISOString()
            })
        });
    } catch (err) {
        // Analytics errors must not break UX
        console.warn('[trackClick]', err);
    }
}


// ═══════════════════════════════════════════════════════════════
// 5. REAL-TIME AUTOSUGGEST TYPEAHEAD
// ═══════════════════════════════════════════════════════════════

let _suggestDebounce = null;

async function autosuggest(val) {
    const box = document.getElementById('suggestions');
    if (!box) return;

    const query = (val || '').trim();
    if (query.length < 3) {
        box.innerHTML = '';
        box.style.display = 'none';
        return;
    }

    clearTimeout(_suggestDebounce);
    _suggestDebounce = setTimeout(async () => {
        try {
            const res = await fetch('/api/ai/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, top_k: 5 })
            });

            if (!res.ok) { box.style.display = 'none'; return; }

            const data = await res.json();
            const hits = data.source_metadata || [];

            if (!hits.length) { box.innerHTML = ''; box.style.display = 'none'; return; }

            box.innerHTML = '';
            hits.forEach(hit => {
                const text = hit.title || hit.content || '';
                if (!text) return;

                const item = document.createElement('div');
                item.className = 'suggestion-item';
                item.textContent = text;
                item.addEventListener('click', () => {
                    // Fill the chat input with selected suggestion
                    const chatInput = document.getElementById('chat-text');
                    if (chatInput) chatInput.value = text;
                    box.innerHTML   = '';
                    box.style.display = 'none';
                });
                box.appendChild(item);
            });

            box.style.display = 'block';
        } catch (err) {
            console.warn('[autosuggest]', err);
            box.innerHTML = '';
            box.style.display = 'none';
        }
    }, 300);      // 300 ms debounce
}


// ═══════════════════════════════════════════════════════════════
// 6. AI CHAT PANEL
// ═══════════════════════════════════════════════════════════════

function openChat() {
    const panel = document.getElementById('chat-panel');
    if (!panel) return;
    panel.style.display = 'flex';
    panel.setAttribute('aria-hidden', 'false');

    // Pre-fill with search input value if present
    const searchInput = document.getElementById('search-input');
    const chatText    = document.getElementById('chat-text');
    if (searchInput && chatText && searchInput.value.trim()) {
        chatText.value = searchInput.value.trim();
    }

    chatText?.focus();
}

function closeChat() {
    const panel = document.getElementById('chat-panel');
    if (!panel) return;
    panel.style.display = 'none';
    panel.setAttribute('aria-hidden', 'true');

    // Clear suggestions
    const box = document.getElementById('suggestions');
    if (box) { box.innerHTML = ''; box.style.display = 'none'; }
}

async function sendChat() {
    const chatText = document.getElementById('chat-text');
    const chatBody = document.getElementById('chat-body');
    if (!chatText || !chatBody) return;

    const query = chatText.value.trim();
    if (!query) return;

    chatText.value = '';

    // Clear suggestions
    const box = document.getElementById('suggestions');
    if (box) { box.innerHTML = ''; box.style.display = 'none'; }

    // Append user bubble
    appendChatMsg('user', query, chatBody);

    // Typing indicator
    const typingId = appendChatMsg('ai typing', '…', chatBody);

    try {
        const res = await fetch('/api/ai/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, top_k: 5 })
        });

        removeMsg(typingId, chatBody);

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        const answer = (data.answer || '').trim() ||
                       'I couldn\'t find a specific answer. Please try rephrasing your question.';

        appendChatMsg('ai', answer, chatBody);

        // Also try Gemini for richer responses
        fetchGeminiEnhancement(query, chatBody);

    } catch (err) {
        removeMsg(typingId, chatBody);
        appendChatMsg('ai', 'Sorry – I could not reach the server. Please check your connection.', chatBody);
        console.warn('[sendChat]', err);
    }
}

async function fetchGeminiEnhancement(query, chatBody) {
    // Non-blocking enrichment via the Gemini endpoint
    try {
        const res = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: query })
        });
        if (!res.ok) return;
        const data = await res.json();
        if (data.response && data.response.trim()) {
            appendChatMsg('ai gemini', data.response.trim(), chatBody, '✨ Gemini');
        }
    } catch (_) { /* silent */ }
}

function appendChatMsg(role, text, container, label = null) {
    const msgId = 'msg-' + Date.now() + '-' + Math.random().toString(36).slice(2, 6);
    const div = document.createElement('div');
    div.id        = msgId;
    div.className = `chat-msg ${role}`;

    if (label) {
        const lbl = document.createElement('span');
        lbl.className   = 'msg-label';
        lbl.textContent = label;
        div.appendChild(lbl);
    }

    const p = document.createElement('p');
    p.textContent = text;
    div.appendChild(p);

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return msgId;
}

function removeMsg(id, container) {
    const el = container.querySelector('#' + id);
    if (el) el.remove();
}


// ═══════════════════════════════════════════════════════════════
// 7. PROGRESSIVE PROFILING
// ═══════════════════════════════════════════════════════════════

/**
 * Gracefully show the profile modal when high-intent action detected.
 * `anchorEl` is the element the user tried to click – we resume it after submit.
 */
function triggerProfileCheck(anchorEl) {
    const hasProfile = Boolean(profileId);
    const name = localStorage.getItem('p_name');

    if (hasProfile && name) return;   // Profile already complete

    // Store the pending action
    if (anchorEl) {
        _pendingAction = () => anchorEl.click();
    }

    document.getElementById('profile-modal').style.display = 'flex';
}

function profileNext(currentStep) {
    // Basic validation
    if (currentStep === 1) {
        const name = document.getElementById('p_name')?.value.trim();
        const age  = document.getElementById('p_age')?.value.trim();
        if (!name || !age) {
            showFormError('Please fill in your name and age.'); return;
        }
    }
    if (currentStep === 2) {
        const email = document.getElementById('p_email')?.value.trim();
        if (email && !email.includes('@')) {
            showFormError('Please enter a valid email address.'); return;
        }
    }

    setProfileStep(currentStep, false);
    setProfileStep(currentStep + 1, true);
}

function profileBack(targetStep) {
    setProfileStep(targetStep, false);
    setProfileStep(targetStep - 1, true);
}

function setProfileStep(step, visible) {
    const el = document.getElementById(`profile-step-${step}`);
    if (el) el.style.display = visible ? 'block' : 'none';
}

async function profileSubmit() {
    const name  = document.getElementById('p_name')?.value.trim()  || '';
    const age   = document.getElementById('p_age')?.value.trim()   || '';
    const email = document.getElementById('p_email')?.value.trim() || '';
    const phone = document.getElementById('p_phone')?.value.trim() || '';
    const job   = document.getElementById('p_job')?.value.trim()   || '';

    const payload = {
        step: 'full',
        data: { name, age, job, phone },
        ...(email    ? { email }     : {}),
        ...(profileId ? { profile_id: profileId } : {})
    };

    try {
        const res = await fetch('/api/profile/step', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();

        // Persist profile ID + name locally
        if (data.profile_id) {
            profileId = data.profile_id;
            localStorage.setItem('profileId', profileId);
        }
        localStorage.setItem('p_name', name);

        // Close modal
        document.getElementById('profile-modal').style.display = 'none';

        // Reset steps for next open
        setProfileStep(1, true);
        setProfileStep(2, false);
        setProfileStep(3, false);

        // Resume pending download / link action
        if (_pendingAction) {
            const action = _pendingAction;
            _pendingAction = null;
            setTimeout(action, 100);
        }

    } catch (err) {
        showFormError('Could not save your profile. Please try again.');
        console.error('[profileSubmit]', err);
    }
}

function showFormError(msg) {
    let errEl = document.getElementById('profile-form-error');
    if (!errEl) {
        errEl = document.createElement('p');
        errEl.id        = 'profile-form-error';
        errEl.className = 'form-error';
        const content = document.querySelector('.modal-content');
        if (content) content.prepend(errEl);
    }
    errEl.textContent = msg;
    setTimeout(() => { if (errEl) errEl.textContent = ''; }, 4000);
}
