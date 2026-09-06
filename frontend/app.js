// Pumpkin - AI Search Engine
const API_BASE = 'http://127.0.0.1:8000/api/v1';

let currentMode = 'web';
let currentQuery = '';

const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('results-section');
const resultsList = document.getElementById('results-list');
const resultCount = document.getElementById('result-count');
const aiAnswer = document.getElementById('ai-answer');
const answerContent = document.getElementById('answer-content');
const citations = document.getElementById('citations');

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
                <p style="font-size:12px;margin-top:8px;">Make sure the server is running</p>
            </div>
        `;
        resultsSection.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
    }
}

// Render Results
function renderResults(data) {
    resultsSection.classList.remove('hidden');

    const total = data.total || (data.results ? data.results.length : 0);
    resultCount.textContent = `${total} results`;

    if (data.answer) {
        renderAIAnswer(data);
    } else {
        aiAnswer.classList.add('hidden');
    }

    renderSearchResults(data.results || []);
    fetchRelatedSearches(currentQuery);
}

// Render AI Answer
function renderAIAnswer(data) {
    aiAnswer.classList.remove('hidden');
    let answerText = data.answer || 'No answer generated.';
    answerContent.innerHTML = answerText;

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

// Highlight search terms
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

// Related Searches
async function fetchRelatedSearches(query) {
    try {
        const response = await fetch(`${API_BASE}/related?q=${encodeURIComponent(query)}&limit=8`);
        if (!response.ok) return;
        const data = await response.json();
        const related = data.related_searches || [];
        
        const container = document.getElementById('related-searches');
        if (container && related.length > 0) {
            let html = '<div class="related-searches"><h4>🔗 Related Searches</h4><div class="related-tags">';
            related.forEach(term => {
                html += `<span class="related-tag" data-query="${term}">${term}</span>`;
            });
            html += '</div></div>';
            container.innerHTML = html;
            
            document.querySelectorAll('.related-tag').forEach(tag => {
                tag.addEventListener('click', () => {
                    searchInput.value = tag.dataset.query;
                    performSearch();
                });
            });
        }
    } catch (error) {
        console.warn('Related searches error:', error);
    }
}

// Initialize
searchInput.focus();