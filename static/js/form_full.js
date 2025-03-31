// Form handling functionality - Full form display version

document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    const formContainer = document.getElementById('form-container');
    const questionContainer = document.getElementById('question-container');
    const progressBar = document.getElementById('form-progress');
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    const saveButton = document.getElementById('save-button');
    const submitButton = document.getElementById('submit-button');
    
    // Check if we're on a form page
    if (!formContainer) return;
    
    // Get form data from the data attribute
    const formData = JSON.parse(formContainer.dataset.form || '{}');
    const responseId = formContainer.dataset.responseId;
    const initialAnswers = JSON.parse(formContainer.dataset.answers || '{}');
    
    // Form state
    let answers = {...initialAnswers};
    let questions = formData.questions || [];
    
    // Initialize the form
    function initForm() {
        if (questions.length === 0) {
            questionContainer.innerHTML = '<div class="alert alert-warning">No questions found in this form.</div>';
            return;
        }
        
        // Show all form questions at once
        renderEntireForm();
        
        // Update navigation
        updateNavigation();
    }
    
    // Render the entire form at once
    function renderEntireForm() {
        console.log("Rendering entire form with", questions.length, "questions");
        
        // Create a form that displays all questions at once
        let formHTML = '<div class="full-form">';
        
        // Add each question
        questions.forEach((question, index) => {
            const questionId = question.id;
            // Handle variations in field names from different form structures
            const questionText = question.question_text || question.question || question.label || "Question " + (index + 1);
            const isRequired = question.required === true;
            const fieldType = question.field_type || question.type || "text";
            
            formHTML += `
                <div class="form-group mb-4">
                    <div class="question-title">
                        ${questionText}
                        ${isRequired ? '<span class="required-indicator text-danger">*</span>' : ''}
                    </div>
            `;
            
            // Add field based on type
            switch (fieldType) {
                case 'text':
                    formHTML += `
                        <input type="text" class="form-control mt-2" id="input-${questionId}" 
                               data-question-id="${questionId}"
                               value="${answers[questionId] || ''}" 
                               ${isRequired ? 'required' : ''}>
                    `;
                    break;
                    
                case 'textarea':
                    formHTML += `
                        <textarea class="form-control mt-2" id="input-${questionId}" 
                                  data-question-id="${questionId}"
                                  rows="4" ${isRequired ? 'required' : ''}>${answers[questionId] || ''}</textarea>
                    `;
                    break;
                    
                case 'number':
                    formHTML += `
                        <input type="number" class="form-control mt-2" id="input-${questionId}" 
                               data-question-id="${questionId}"
                               value="${answers[questionId] || ''}" 
                               ${isRequired ? 'required' : ''}>
                    `;
                    break;
                    
                case 'date':
                    formHTML += `
                        <input type="date" class="form-control mt-2" id="input-${questionId}" 
                               data-question-id="${questionId}"
                               value="${answers[questionId] || ''}" 
                               ${isRequired ? 'required' : ''}>
                    `;
                    break;
                    
                case 'email':
                    formHTML += `
                        <input type="email" class="form-control mt-2" id="input-${questionId}" 
                               data-question-id="${questionId}"
                               value="${answers[questionId] || ''}" 
                               ${isRequired ? 'required' : ''}>
                    `;
                    break;
                    
                case 'radio':
                    formHTML += '<div class="mt-2">';
                    if (question.options) {
                        question.options.forEach((option, i) => {
                            formHTML += `
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="input-${questionId}" 
                                           data-question-id="${questionId}"
                                           id="option-${questionId}-${i}" value="${option}" 
                                           ${answers[questionId] === option ? 'checked' : ''}
                                           ${isRequired ? 'required' : ''}>
                                    <label class="form-check-label" for="option-${questionId}-${i}">
                                        ${option}
                                    </label>
                                </div>
                            `;
                        });
                    }
                    formHTML += '</div>';
                    break;
                    
                case 'checkbox':
                    formHTML += '<div class="mt-2">';
                    if (question.options) {
                        question.options.forEach((option, i) => {
                            const isChecked = Array.isArray(answers[questionId]) && answers[questionId].includes(option);
                            formHTML += `
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" name="input-${questionId}" 
                                           data-question-id="${questionId}"
                                           id="option-${questionId}-${i}" value="${option}" 
                                           ${isChecked ? 'checked' : ''}>
                                    <label class="form-check-label" for="option-${questionId}-${i}">
                                        ${option}
                                    </label>
                                </div>
                            `;
                        });
                    }
                    formHTML += '</div>';
                    break;
                    
                case 'select':
                    formHTML += `
                        <select class="form-select mt-2" id="input-${questionId}" 
                                data-question-id="${questionId}"
                                ${isRequired ? 'required' : ''}>
                            <option value="" ${!answers[questionId] ? 'selected' : ''}>Select an option</option>
                    `;
                    if (question.options) {
                        question.options.forEach(option => {
                            formHTML += `
                                <option value="${option}" ${answers[questionId] === option ? 'selected' : ''}>
                                    ${option}
                                </option>
                            `;
                        });
                    }
                    formHTML += '</select>';
                    break;
                    
                default:
                    formHTML += `
                        <input type="text" class="form-control mt-2" id="input-${questionId}" 
                               data-question-id="${questionId}"
                               value="${answers[questionId] || ''}" 
                               ${isRequired ? 'required' : ''}>
                    `;
            }
            
            formHTML += `</div>`;
        });
        
        formHTML += '</div>';
        
        // Update the DOM
        questionContainer.innerHTML = formHTML;
        
        // Update progress
        progressBar.style.width = '100%';
        progressBar.setAttribute('aria-valuenow', 100);
        
        // Add event listeners to all inputs
        setupInputListeners();
    }
    
    // Set up event listeners for all form inputs
    function setupInputListeners() {
        // Set up listeners for text inputs, textareas, selects
        document.querySelectorAll('input[type="text"], input[type="number"], input[type="email"], input[type="date"], textarea, select').forEach(input => {
            if (input.dataset.questionId) {
                input.addEventListener('input', function() {
                    const questionId = this.dataset.questionId;
                    answers[questionId] = this.value;
                });
            }
        });
        
        // Set up listeners for radio inputs
        questions.forEach(question => {
            const questionId = question.id;
            const fieldType = question.field_type || question.type || "text";
            
            if (fieldType === 'radio') {
                const radioInputs = document.querySelectorAll(`input[name="input-${questionId}"]`);
                radioInputs.forEach(input => {
                    input.addEventListener('change', function() {
                        answers[questionId] = this.value;
                    });
                });
            } else if (fieldType === 'checkbox') {
                const checkboxInputs = document.querySelectorAll(`input[name="input-${questionId}"]`);
                checkboxInputs.forEach(input => {
                    input.addEventListener('change', function() {
                        // Get all checked values
                        const checkedValues = Array.from(checkboxInputs)
                            .filter(cb => cb.checked)
                            .map(cb => cb.value);
                        
                        answers[questionId] = checkedValues;
                    });
                });
            }
        });
    }
    
    // Update navigation buttons for the full form display
    function updateNavigation() {
        // Hide previous and next buttons since we're showing all questions at once
        prevButton.style.display = 'none';
        nextButton.style.display = 'none';
        
        // Show the submit button immediately since all questions are displayed
        submitButton.style.display = 'block';
    }
    
    // Show the review screen with all answers
    function showReviewScreen() {
        let reviewHTML = `
            <div class="review-container">
                <h3>Review Your Answers</h3>
                <p>Please review your answers before submitting the form.</p>
                <div class="mt-4">
        `;
        
        questions.forEach(question => {
            const answer = answers[question.id];
            const questionText = question.question_text || question.question || question.label || "Question";
            const fieldType = question.field_type || question.type || "text";
            
            reviewHTML += `
                <div class="mb-4">
                    <div class="fw-bold">${questionText}</div>
                    <div class="mt-2">
            `;
            
            if (fieldType === 'checkbox' && Array.isArray(answer)) {
                if (answer.length === 0) {
                    reviewHTML += '<em>No options selected</em>';
                } else {
                    answer.forEach(option => {
                        reviewHTML += `<div>- ${option}</div>`;
                    });
                }
            } else if (answer) {
                reviewHTML += answer;
            } else {
                reviewHTML += '<em>No answer provided</em>';
            }
            
            reviewHTML += `
                    </div>
                </div>
            `;
        });
        
        reviewHTML += `
                </div>
                <div class="mt-4">
                    <button id="continue-editing-button" class="btn btn-secondary">Continue Editing</button>
                </div>
            </div>
        `;
        
        questionContainer.innerHTML = reviewHTML;
        
        // Add continue editing button listener
        document.getElementById('continue-editing-button').addEventListener('click', function() {
            renderEntireForm();
        });
    }
    
    // Save form progress
    function saveProgress() {
        const saveIndicator = document.getElementById('save-indicator');
        saveIndicator.innerHTML = '<span class="loading-spinner"></span> Saving...';
        
        fetch(`/forms/response/${responseId}/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                answers: answers
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                saveIndicator.innerHTML = '<i class="bi bi-check-circle"></i> Saved';
                
                // Clear the indicator after 3 seconds
                setTimeout(() => {
                    saveIndicator.innerHTML = '';
                }, 3000);
            } else {
                saveIndicator.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Save failed';
            }
        })
        .catch(error => {
            console.error('Error saving form:', error);
            saveIndicator.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Save failed';
        });
    }
    
    // Submit the completed form
    function submitForm() {
        // Validate all required fields
        const requiredFields = questions.filter(q => q.required);
        const missingFields = [];
        
        requiredFields.forEach(question => {
            const questionId = question.id;
            const value = answers[questionId];
            
            if (!value || (Array.isArray(value) && value.length === 0)) {
                missingFields.push(question);
                
                // Highlight the missing field
                const inputElement = document.getElementById(`input-${questionId}`);
                if (inputElement) {
                    inputElement.classList.add('is-invalid');
                    
                    // Add validation message if not exists
                    if (!document.getElementById(`validation-${questionId}`)) {
                        const validationDiv = document.createElement('div');
                        validationDiv.id = `validation-${questionId}`;
                        validationDiv.className = 'invalid-feedback';
                        validationDiv.textContent = 'This field is required.';
                        inputElement.parentNode.appendChild(validationDiv);
                    }
                }
            }
        });
        
        if (missingFields.length > 0) {
            // Scroll to the first missing field
            const firstMissingFieldId = missingFields[0].id;
            const firstMissingElement = document.getElementById(`input-${firstMissingFieldId}`);
            if (firstMissingElement) {
                firstMissingElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return;
        }
        
        // Show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';
        
        fetch(`/forms/response/${responseId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                answers: answers
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                formContainer.innerHTML = `
                    <div class="alert alert-success">
                        <h4>Form Submitted Successfully!</h4>
                        <p>Thank you for completing this form.</p>
                        ${data.email_sent ? 
                            '<p>A copy of your completed form has been emailed to you and Minto Disability Services.</p>' : 
                            `<p>Note: ${data.message || 'Your form has been saved but could not be emailed at this time.'}</p>`}
                        <div class="mt-4">
                            <a href="/forms" class="btn btn-primary">Return to Forms</a>
                        </div>
                    </div>
                `;
            } else {
                // Show error message
                let errorMessage = data.message || 'An error occurred during submission.';
                
                if (data.missing_fields && data.missing_fields.length > 0) {
                    errorMessage += '<ul>';
                    data.missing_fields.forEach(field => {
                        errorMessage += `<li>${field.question}</li>`;
                    });
                    errorMessage += '</ul>';
                }
                
                questionContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <h4>Submission Error</h4>
                        <p>${errorMessage}</p>
                    </div>
                `;
                
                submitButton.disabled = false;
                submitButton.innerHTML = 'Submit Form';
            }
        })
        .catch(error => {
            console.error('Error submitting form:', error);
            
            questionContainer.innerHTML = `
                <div class="alert alert-danger">
                    <h4>Submission Error</h4>
                    <p>An error occurred while submitting the form. Please try again.</p>
                </div>
            `;
            
            submitButton.disabled = false;
            submitButton.innerHTML = 'Submit Form';
        });
    }
    
    // Event listeners
    saveButton.addEventListener('click', saveProgress);
    submitButton.addEventListener('click', submitForm);
    
    // Auto-save every 30 seconds
    const autoSaveInterval = setInterval(saveProgress, 30000);
    
    // Clean up interval when leaving the page
    window.addEventListener('beforeunload', function() {
        clearInterval(autoSaveInterval);
    });
    
    // Initialize the form
    initForm();
});