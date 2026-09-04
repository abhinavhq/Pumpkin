// AI Search Engine - Frontend Application

const API_BASE = 'http://127.0.0.1:8000/api/v1';

// State
let currentMode = 'web';
let currentQuery = '';

// DOM Elements
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('results-section');
const resultsList = document.getElementById('results-list');
const resultCount = document.getElementById('result-count');
const aiAnswer = document.getElementById('ai-answer');
const answerContent = document.getElementById('answer-content');
const citations = document.getElementById('citations');

// Mode buttons
const modeButtons = document.querySelectorAll('.mode-btn');

// Event Listeners
searchBtn.addEventListener('click', performSearch);
searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') performSearch();
});

modeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        modeButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentMode = btn.dataset.mode;
        // Auto-search if there's a query
        if (searchInput.value.trim()) {
            performSearch();
        }
    });
});

// Search Function
async function performSearch() {
    const query = searchInput.value.trim();
    if (!query) return;

    currentQuery = query;

    // Show loading, hide results
    loading.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    aiAnswer.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}&mode=${currentMode}&limit=10`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        renderResults(data);

    } catch (error) {
        console.error('Search error:', error);
        resultsList.innerHTML = `
            <div class="result-item" style="text-align:center;color:#888;">
                <p>❌ Error: ${error.message}</p>
                <p style="font-size:12px;margin-top:8px;">Make sure the server is running at ${API_BASE}</p>
            </div>
        `;
        resultsSection.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
    }
}

// Render Results
function renderResults(data) {
    // Show results section
    resultsSection.classList.remove('hidden');

    // Update result count
    const total = data.total || (data.results ? data.results.length : 0);
    resultCount.textContent = `${total} results`;

    // Render AI answer if available
    if (data.answer) {
        renderAIAnswer(data);
    } else {
        aiAnswer.classList.add('hidden');
    }

    // Render search results
    renderSearchResults(data.results || []);
}

// Render AI Answer
function renderAIAnswer(data) {
    aiAnswer.classList.remove('hidden');
    
    // Format answer with citations
    let answerText = data.answer || 'No answer generated.';
    answerContent.innerHTML = formatAnswerWithCitations(answerText);

    // Render citations
    if (data.citations && data.citations.length > 0) {
        let citationsHTML = '<h4>📚 Sources</h4>';
        data.citations.forEach(c => {
            citationsHTML += `
                <div class="citation-item">
                    <span class="citation-id">[${c.id}]</span>
                    <div>
                        <div class="citation-title">${c.title || 'Untitled'}</div>
                        <div class="citation-url">${c.url || 'No URL'}</div>
                    </div>
                </div>
            `;
        });
        citations.innerHTML = citationsHTML;
    } else {
        citations.innerHTML = '';
    }
}

// Format Answer with Citations
function formatAnswerWithCitations(text) {
    // Convert [1], [2] to clickable spans
    return text.replace(/\[(\d+)\]/g, (match, num) => {
        return `<span class="citation" onclick="scrollToCitation(${num})">[${num}]</span>`;
    });
}

// Scroll to citation
function scrollToCitation(id) {
    const citationsEl = document.querySelector('.citations');
    if (citationsEl) {
        const citationItems = citationsEl.querySelectorAll('.citation-item');
        citationItems.forEach(item => {
            const idSpan = item.querySelector('.citation-id');
            if (idSpan && idSpan.textContent === `[${id}]`) {
                item.scrollIntoView({ behavior: 'smooth', block: 'center' });
                item.style.backgroundColor = '#1a1a2e';
                setTimeout(() => {
                    item.style.backgroundColor = '';
                }, 1500);
            }
        });
    }
}

// Render Search Results
function renderSearchResults(results) {
    if (!results || results.length === 0) {
        resultsList.innerHTML = `
            <div class="result-item" style="text-align:center;color:#888;">
                <p>No results found.</p>
            </div>
        `;
        return;
    }

    let html = '';
    results.forEach((result, index) => {
        const title = result.title || 'Untitled';
        const snippet = result.snippet || result.content || 'No description available.';
        const score = result.score || result.similarity || 0;
        const url = result.url || '#';

        // Highlight keywords in snippet
        const highlightedSnippet = highlightTerms(snippet, currentQuery);

        html += `
            <div class="result-item" data-index="${index}">
                <a href="${url}" target="_blank" class="result-title">${title}</a>
                <div class="result-url">${url}</div>
                <div class="result-snippet">${highlightedSnippet}</div>
                <div class="result-score">Relevance: ${(score * 100).toFixed(1)}%</div>
            </div>
        `;
    });

    resultsList.innerHTML = html;
}

// Highlight search terms in snippet
function highlightTerms(text, query) {
    if (!query) return text;
    const words = query.split(' ').filter(w => w.length > 1);
    let highlighted = text;
    words.forEach(word => {
        const regex = new RegExp(`(${word})`, 'gi');
        highlighted = highlighted.replace(regex, '<mark>$1</mark>');
    });
    return highlighted;
}

// Initialize - check server health
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            console.log('✅ Server is healthy');
        }
    } catch (error) {
        console.warn('⚠️ Server not reachable. Make sure it\'s running.');
    }
}

// Auto-focus search input
searchInput.focus();

// Check health on load
checkHealth();
// ============================================
// AUTOCOMPLETE
// ============================================

const autocompleteList = document.createElement('div');
autocompleteList.className = 'autocomplete-list';
autocompleteList.style.display = 'none';
searchInput.parentNode.appendChild(autocompleteList);

let autocompleteTimeout = null;

searchInput.addEventListener('input', async function() {
    const query = this.value.trim();
    
    clearTimeout(autocompleteTimeout);
    
    if (query.length < 2) {
        autocompleteList.style.display = 'none';
        return;
    }
    
    autocompleteTimeout = setTimeout(async () => {
        await fetchAutocomplete(query);
    }, 200);
});

async function fetchAutocomplete(prefix) {
    try {
        const response = await fetch(`${API_BASE}/autocomplete?q=${encodeURIComponent(prefix)}&limit=6`);
        
        if (!response.ok) {
            throw new Error('Autocomplete failed');
        }
        
        const data = await response.json();
        renderAutocomplete(data.suggestions);
        
    } catch (error) {
        console.warn('Autocomplete error:', error);
        autocompleteList.style.display = 'none';
    }
}

function renderAutocomplete(suggestions) {
    if (!suggestions || suggestions.length === 0) {
        autocompleteList.style.display = 'none';
        return;
    }
    
    let html = '';
    suggestions.forEach(suggestion => {
        html += `
            <div class="autocomplete-item" data-query="${suggestion.text}">
                <span class="autocomplete-icon">🔍</span>
                <span class="autocomplete-text">${suggestion.text}</span>
                <span class="autocomplete-frequency">${suggestion.frequency} searches</span>
            </div>
        `;
    });
    
    autocompleteList.innerHTML = html;
    autocompleteList.style.display = 'block';
    
    // Add click listeners
    document.querySelectorAll('.autocomplete-item').forEach(item => {
        item.addEventListener('click', () => {
            const query = item.dataset.query;
            searchInput.value = query;
            autocompleteList.style.display = 'none';
            performSearch();
        });
    });
}

// Close autocomplete on escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        autocompleteList.style.display = 'none';
    }
});

// Close autocomplete on click outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-box') && !e.target.closest('.autocomplete-list')) {
        autocompleteList.style.display = 'none';
    }
});// ============================================
// AUTOCOMPLETE
// ============================================

const autocompleteList = document.createElement('div');
autocompleteList.className = 'autocomplete-list';
autocompleteList.style.display = 'none';
searchInput.parentNode.appendChild(autocompleteList);

let autocompleteTimeout = null;

searchInput.addEventListener('input', async function() {
    const query = this.value.trim();
    
    clearTimeout(autocompleteTimeout);
    
    if (query.length < 2) {
        autocompleteList.style.display = 'none';
        return;
    }
    
    autocompleteTimeout = setTimeout(async () => {
        await fetchAutocomplete(query);
    }, 200);
});

async function fetchAutocomplete(prefix) {
    try {
        const response = await fetch(`${API_BASE}/autocomplete?q=${encodeURIComponent(prefix)}&limit=6`);
        
        if (!response.ok) {
            throw new Error('Autocomplete failed');
        }
        
        const data = await response.json();
        renderAutocomplete(data.suggestions);
        
    } catch (error) {
        console.warn('Autocomplete error:', error);
        autocompleteList.style.display = 'none';
    }
}

function renderAutocomplete(suggestions) {
    if (!suggestions || suggestions.length === 0) {
        autocompleteList.style.display = 'none';
        return;
    }
    
    let html = '';
    suggestions.forEach(suggestion => {
        html += `
            <div class="autocomplete-item" data-query="${suggestion.text}">
                <span class="autocomplete-icon">🔍</span>
                <span class="autocomplete-text">${suggestion.text}</span>
                <span class="autocomplete-frequency">${suggestion.frequency} searches</span>
            </div>
        `;
    });
    
    autocompleteList.innerHTML = html;
    autocompleteList.style.display = 'block';
    
    // Add click listeners
    document.querySelectorAll('.autocomplete-item').forEach(item => {
        item.addEventListener('click', () => {
            const query = item.dataset.query;
            searchInput.value = query;
            autocompleteList.style.display = 'none';
            performSearch();
        });
    });
}

// Close autocomplete on escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        autocompleteList.style.display = 'none';
    }
});

// Close autocomplete on click outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-box') && !e.target.closest('.autocomplete-list')) {
        autocompleteList.style.display = 'none';
    }
});