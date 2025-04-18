// Policy assistant functionality

document.addEventListener('DOMContentLoaded', function() {
    // Get policy assistant elements
    const chatContainer = document.getElementById('chat-container');
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const questionInput = document.getElementById('question-input');
    const rebuildButton = document.getElementById('rebuild-vector-db');
    const rebuildStatus = document.getElementById('rebuild-status');
    
    // Check if we're on the policy assistant page
    if (!chatContainer) return;
    
    // Initialize the rebuild vector database functionality if available
    if (rebuildButton) {
        rebuildButton.addEventListener('click', function() {
            if (!confirm('Are you sure you want to rebuild the vector database? This operation may take some time.')) {
                return;
            }
            
            rebuildButton.disabled = true;
            rebuildStatus.innerHTML = '<span class="text-warning">Rebuilding vector database... Please wait.</span>';
            
            fetch('/policies/assistant/rebuild-vector-db', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    rebuildStatus.innerHTML = '<span class="text-success">Vector database rebuilt successfully!</span>';
                    // Add a message to the chat
                    addMessage('assistant', 'The vector database has been rebuilt successfully. You can now search for policy information.');
                } else {
                    rebuildStatus.innerHTML = '<span class="text-danger">Error rebuilding vector database: ' + (data.message || 'Unknown error') + '</span>';
                }
                rebuildButton.disabled = false;
            })
            .catch(error => {
                console.error('Error rebuilding vector database:', error);
                rebuildStatus.innerHTML = '<span class="text-danger">Error connecting to server while rebuilding vector database.</span>';
                rebuildButton.disabled = false;
            });
        });
    }
    
    // Message history
    let messageHistory = [];
    
    // Initialize with a welcome message
    addMessage('assistant', 'Welcome to the Policy Assistant! I can help you find information in our policy and procedure documents. What would you like to know?');
    
    // Handle form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const question = questionInput.value.trim();
        
        if (!question) return;
        
        // Add user question to chat
        addMessage('user', question);
        
        // Clear input
        questionInput.value = '';
        
        // Show loading indicator
        const loadingId = addMessage('assistant', '<div class="loading-spinner"></div> Searching policies...');
        
        // Send question to API
        fetch('/policies/assistant/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: question }),
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading message
            document.getElementById(loadingId).remove();
            
            if (data.success) {
                // Format sources if available - deduplicate them by title
                let sourcesHtml = '';
                if (data.sources && data.sources.length > 0) {
                    // Create a deduplicated set of source titles
                    const uniqueSources = new Map();
                    data.sources.forEach(source => {
                        const sourceKey = `${source.document_title} (${source.document_type})`;
                        // Only keep the highest scoring instance of each source
                        if (!uniqueSources.has(sourceKey) || 
                            source.relevance_score > uniqueSources.get(sourceKey).relevance_score) {
                            uniqueSources.set(sourceKey, source);
                        }
                    });
                    
                    // Format the unique sources
                    sourcesHtml = '<div class="message-sources">Sources:<ul>';
                    uniqueSources.forEach((source, sourceKey) => {
                        sourcesHtml += `<li>${sourceKey}</li>`;
                    });
                    sourcesHtml += '</ul></div>';
                }
                
                // Format the answer for better readability
                let formattedAnswer = data.answer;
                
                // Replace any remaining asterisks with normal text (remove markdown)
                formattedAnswer = formattedAnswer.replace(/\*\*/g, '').replace(/\*/g, '');
                
                // Format paragraphs with proper spacing
                formattedAnswer = formattedAnswer.split('\n\n').map(para => 
                    `<p>${para.trim()}</p>`
                ).join('');
                
                // Format lists
                formattedAnswer = formattedAnswer.replace(/(\n[-*]\s+.*)+/g, function(match) {
                    const items = match.trim().split(/\n[-*]\s+/).filter(item => item);
                    return '<ul>' + items.map(item => `<li>${item}</li>`).join('') + '</ul>';
                });
                
                // Format numbered lists
                formattedAnswer = formattedAnswer.replace(/(\n\d+\.\s+.*)+/g, function(match) {
                    const items = match.trim().split(/\n\d+\.\s+/).filter(item => item);
                    return '<ol>' + items.map(item => `<li>${item}</li>`).join('') + '</ol>';
                });
                
                // Add answer with sources
                addMessage('assistant', formattedAnswer + sourcesHtml);
            } else {
                addMessage('assistant', 'Sorry, I encountered an error: ' + (data.message || 'Unknown error'));
            }
            
            // Scroll to bottom
            scrollToBottom();
        })
        .catch(error => {
            console.error('Error querying policy assistant:', error);
            
            // Remove loading message
            document.getElementById(loadingId).remove();
            
            addMessage('assistant', 'Sorry, there was a problem connecting to the server. Please try again.');
            
            // Scroll to bottom
            scrollToBottom();
        });
    });
    
    // Function to add a message to the chat
    function addMessage(sender, content) {
        const messageId = 'msg-' + Date.now();
        const messageElement = document.createElement('div');
        messageElement.id = messageId;
        messageElement.className = `message message-${sender} mb-3`;
        messageElement.innerHTML = content;
        
        chatMessages.appendChild(messageElement);
        
        // Store in history
        messageHistory.push({
            id: messageId,
            sender: sender,
            content: content
        });
        
        // Scroll to bottom
        scrollToBottom();
        
        return messageId;
    }
    
    // Function to scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
