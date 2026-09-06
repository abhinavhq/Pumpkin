// AI Search Engine - Frontend Application



const API\_BASE = 'http://127.0.0.1:8000/api/v1';



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

&#x20;   if (e.key === 'Enter') performSearch();

});



modeButtons.forEach(btn => {

&#x20;   btn.addEventListener('click', () => {

&#x20;       modeButtons.forEach(b => b.classList.remove('active'));

&#x20;       btn.classList.add('active');

&#x20;       currentMode = btn.dataset.mode;

&#x20;       if (searchInput.value.trim()) {

&#x20;           performSearch();

&#x20;       }

&#x20;   });

});



// Search Function

async function performSearch() {

&#x20;   const query = searchInput.value.trim();

&#x20;   if (!query) return;



&#x20;   currentQuery = query;



&#x20;   loading.classList.remove('hidden');

&#x20;   resultsSection.classList.add('hidden');

&#x20;   aiAnswer.classList.add('hidden');



&#x20;   try {

&#x20;       const response = await fetch(`${API\_BASE}/search?q=${encodeURIComponent(query)}\&mode=${currentMode}\&limit=10`);

&#x20;       

&#x20;       if (!response.ok) {

&#x20;           throw new Error(`HTTP error! status: ${response.status}`);

&#x20;       }



&#x20;       const data = await response.json();

&#x20;       renderResults(data);



&#x20;   } catch (error) {

&#x20;       console.error('Search error:', error);

&#x20;       resultsList.innerHTML = `

&#x20;           <div class="result-item" style="text-align:center;color:#888;">

&#x20;               <p>❌ Error: ${error.message}</p>

&#x20;               <p style="font-size:12px;margin-top:8px;">Make sure the server is running at ${API\_BASE}</p>

&#x20;           </div>

&#x20;       `;

&#x20;       resultsSection.classList.remove('hidden');

&#x20;   } finally {

&#x20;       loading.classList.add('hidden');

&#x20;   }

}



// Render Results

function renderResults(data) {

&#x20;   resultsSection.classList.remove('hidden');



&#x20;   const total = data.total || (data.results ? data.results.length : 0);

&#x20;   resultCount.textContent = `${total} results`;



&#x20;   if (data.answer) {

&#x20;       renderAIAnswer(data);

&#x20;   } else {

&#x20;       aiAnswer.classList.add('hidden');

&#x20;   }



&#x20;   renderSearchResults(data.results || \[]);

&#x20;   

&#x20;   // Fetch related searches

&#x20;   fetchRelatedSearches(currentQuery);

}



// Render AI Answer

function renderAIAnswer(data) {

&#x20;   aiAnswer.classList.remove('hidden');

&#x20;   

&#x20;   let answerText = data.answer || 'No answer generated.';

&#x20;   answerContent.innerHTML = formatAnswerWithCitations(answerText);



&#x20;   if (data.citations \&\& data.citations.length > 0) {

&#x20;       let citationsHTML = '<h4>📚 Sources</h4>';

&#x20;       data.citations.forEach(c => {

&#x20;           citationsHTML += `

&#x20;               <div class="citation-item">

&#x20;                   <span class="citation-id">\[${c.id}]</span>

&#x20;                   <div>

&#x20;                       <div class="citation-title">${c.title || 'Untitled'}</div>

&#x20;                       <div class="citation-url">${c.url || 'No URL'}</div>

&#x20;                   </div>

&#x20;               </div>

&#x20;           `;

&#x20;       });

&#x20;       citations.innerHTML = citationsHTML;

&#x20;   } else {

&#x20;       citations.innerHTML = '';

&#x20;   }

}



// Format Answer with Citations

function formatAnswerWithCitations(text) {

&#x20;   return text.replace(/\\\[(\\d+)\\]/g, (match, num) => {

&#x20;       return `<span class="citation" onclick="scrollToCitation(${num})">\[${num}]</span>`;

&#x20;   });

}



// Scroll to citation

function scrollToCitation(id) {

&#x20;   const citationsEl = document.querySelector('.citations');

&#x20;   if (citationsEl) {

&#x20;       const citationItems = citationsEl.querySelectorAll('.citation-item');

&#x20;       citationItems.forEach(item => {

&#x20;           const idSpan = item.querySelector('.citation-id');

&#x20;           if (idSpan \&\& idSpan.textContent === `\[${id}]`) {

&#x20;               item.scrollIntoView({ behavior: 'smooth', block: 'center' });

&#x20;               item.style.backgroundColor = '#1a1a2e';

&#x20;               setTimeout(() => {

&#x20;                   item.style.backgroundColor = '';

&#x20;               }, 1500);

&#x20;           }

&#x20;       });

&#x20;   }

}



// Render Search Results

function renderSearchResults(results) {

&#x20;   if (!results || results.length === 0) {

&#x20;       resultsList.innerHTML = `

&#x20;           <div class="result-item" style="text-align:center;color:#888;">

&#x20;               <p>No results found.</p>

&#x20;           </div>

&#x20;       `;

&#x20;       return;

&#x20;   }



&#x20;   let html = '';

&#x20;   results.forEach((result, index) => {

&#x20;       const title = result.title || 'Untitled';

&#x20;       const snippet = result.snippet || result.content || 'No description available.';

&#x20;       const score = result.score || result.similarity || 0;

&#x20;       const url = result.url || '#';



&#x20;       const highlightedSnippet = highlightTerms(snippet, currentQuery);



&#x20;       html += `

&#x20;           <div class="result-item" data-index="${index}">

&#x20;               <a href="${url}" target="\_blank" class="result-title">${title}</a>

&#x20;               <div class="result-url">${url}</div>

&#x20;               <div class="result-snippet">${highlightedSnippet}</div>

&#x20;               <div class="result-score">Relevance: ${(score \* 100).toFixed(1)}%</div>

&#x20;           </div>

&#x20;       `;

&#x20;   });



&#x20;   resultsList.innerHTML = html;

}



// Highlight search terms in snippet

function highlightTerms(text, query) {

&#x20;   if (!query) return text;

&#x20;   const words = query.split(' ').filter(w => w.length > 1);

&#x20;   let highlighted = text;

&#x20;   words.forEach(word => {

&#x20;       const regex = new RegExp(`(${word})`, 'gi');

&#x20;       highlighted = highlighted.replace(regex, '<mark>$1</mark>');

&#x20;   });

&#x20;   return highlighted;

}



// ============================================

// RELATED SEARCHES

// ============================================



async function fetchRelatedSearches(query) {

&#x20;   try {

&#x20;       const response = await fetch(`${API\_BASE}/related?q=${encodeURIComponent(query)}\&limit=8`);

&#x20;       

&#x20;       if (!response.ok) {

&#x20;           throw new Error('Related searches failed');

&#x20;       }

&#x20;       

&#x20;       const data = await response.json();

&#x20;       const related = data.related\_searches || \[];

&#x20;       renderRelatedSearches(related);

&#x20;       

&#x20;   } catch (error) {

&#x20;       console.warn('Related searches error:', error);

&#x20;   }

}



function renderRelatedSearches(related) {

&#x20;   const container = document.getElementById('related-searches');

&#x20;   if (!container) return;

&#x20;   

&#x20;   if (!related || related.length === 0) {

&#x20;       container.innerHTML = '';

&#x20;       return;

&#x20;   }

&#x20;   

&#x20;   let html = '<div class="related-searches"><h4>🔗 Related Searches</h4><div class="related-tags">';

&#x20;   

&#x20;   related.forEach(term => {

&#x20;       html += `<span class="related-tag" data-query="${term}">${term}</span>`;

&#x20;   });

&#x20;   

&#x20;   html += '</div></div>';

&#x20;   container.innerHTML = html;

&#x20;   

&#x20;   document.querySelectorAll('.related-tag').forEach(tag => {

&#x20;       tag.addEventListener('click', () => {

&#x20;           searchInput.value = tag.dataset.query;

&#x20;           performSearch();

&#x20;       });

&#x20;   });

}



// ============================================

// AUTOCOMPLETE

// ============================================



const autocompleteList = document.createElement('div');

autocompleteList.className = 'autocomplete-list';

autocompleteList.style.display = 'none';

searchInput.parentNode.appendChild(autocompleteList);



let autocompleteTimeout = null;



searchInput.addEventListener('input', async function() {

&#x20;   const query = this.value.trim();

&#x20;   

&#x20;   clearTimeout(autocompleteTimeout);

&#x20;   

&#x20;   if (query.length < 2) {

&#x20;       autocompleteList.style.display = 'none';

&#x20;       return;

&#x20;   }

&#x20;   

&#x20;   autocompleteTimeout = setTimeout(async () => {

&#x20;       await fetchAutocomplete(query);

&#x20;   }, 200);

});



async function fetchAutocomplete(prefix) {

&#x20;   try {

&#x20;       const response = await fetch(`${API\_BASE}/autocomplete?q=${encodeURIComponent(prefix)}\&limit=6`);

&#x20;       

&#x20;       if (!response.ok) {

&#x20;           throw new Error('Autocomplete failed');

&#x20;       }

&#x20;       

&#x20;       const data = await response.json();

&#x20;       renderAutocomplete(data.suggestions);

&#x20;       

&#x20;   } catch (error) {

&#x20;       console.warn('Autocomplete error:', error);

&#x20;       autocompleteList.style.display = 'none';

&#x20;   }

}



function renderAutocomplete(suggestions) {

&#x20;   if (!suggestions || suggestions.length === 0) {

&#x20;       autocompleteList.style.display = 'none';

&#x20;       return;

&#x20;   }

&#x20;   

&#x20;   let html = '';

&#x20;   suggestions.forEach(suggestion => {

&#x20;       html += `

&#x20;           <div class="autocomplete-item" data-query="${suggestion.text}">

&#x20;               <span class="autocomplete-icon">🔍</span>

&#x20;               <span class="autocomplete-text">${suggestion.text}</span>

&#x20;               <span class="autocomplete-frequency">${suggestion.frequency} searches</span>

&#x20;           </div>

&#x20;       `;

&#x20;   });

&#x20;   

&#x20;   autocompleteList.innerHTML = html;

&#x20;   autocompleteList.style.display = 'block';

&#x20;   

&#x20;   document.querySelectorAll('.autocomplete-item').forEach(item => {

&#x20;       item.addEventListener('click', () => {

&#x20;           const query = item.dataset.query;

&#x20;           searchInput.value = query;

&#x20;           autocompleteList.style.display = 'none';

&#x20;           performSearch();

&#x20;       });

&#x20;   });

}



document.addEventListener('keydown', (e) => {

&#x20;   if (e.key === 'Escape') {

&#x20;       autocompleteList.style.display = 'none';

&#x20;   }

});



document.addEventListener('click', (e) => {

&#x20;   if (!e.target.closest('.search-box') \&\& !e.target.closest('.autocomplete-list')) {

&#x20;       autocompleteList.style.display = 'none';

&#x20;   }

});



// Initialize

searchInput.focus();

