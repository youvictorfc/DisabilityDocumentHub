// Form handling functionality

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
        
        // Hide navigation since all questions are shown at once
        updateNavigationForFullForm();
    }
    
    // Render the entire form at once
    function renderEntireForm() {
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
        setupAllInputListeners();
    }
    
    // Set up input event listeners for a single question
    function setupInputListeners(question) {
        const questionId = question.id;
        const fieldType = question.field_type || question.type || "text";
        
        switch (fieldType) {
            case 'radio':
                const radioInputs = document.querySelectorAll(`input[name="input-${questionId}"]`);
                radioInputs.forEach(input => {
                    input.addEventListener('change', function() {
                        answers[questionId] = this.value;
                    });
                });
                break;
                
            case 'checkbox':
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
                break;
                
            default:
                const input = document.getElementById(`input-${questionId}`);
                if (input) {
                    input.addEventListener('input', function() {
                        answers[questionId] = this.value;
                    });
                }
        }
    }
    
    // Set up input event listeners for all questions
    function setupAllInputListeners() {
        // Set up listeners for all text, number, email, date, and textarea inputs
        document.querySelectorAll('input[type="text"], input[type="number"], input[type="email"], input[type="date"], textarea, select').forEach(input => {
            if (input.dataset.questionId) {
                input.addEventListener('input', function() {
                    const questionId = this.dataset.questionId;
                    answers[questionId] = this.value;
                });
            }
        });
        
        // Set up listeners for all radio inputs
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
    
    // Update navigation buttons (for step-by-step navigation)
    function updateNavigation() {
        // Disable/enable previous button
        prevButton.disabled = currentQuestionIndex === 0;
        
        // Update next/submit button
        if (currentQuestionIndex >= questions.length - 1) {
            nextButton.style.display = 'none';
            submitButton.style.display = 'block';
        } else {
            nextButton.style.display = 'block';
            submitButton.style.display = 'none';
        }
    }
    
    // Update navigation for full form display
    function updateNavigationForFullForm() {
        // Hide previous and next buttons since all questions are displayed at once
        prevButton.style.display = 'none';
        nextButton.style.display = 'none';
        
        // Show the submit button
        submitButton.style.display = 'block';
    }
    
    // Show the completion screen
    function showCompletionScreen() {
        questionContainer.innerHTML = `
            <div class="text-center">
                <h3>Form Complete</h3>
                <p>Please review your answers before submitting.</p>
                <div class="mt-4">
                    <button id="review-button" class="btn btn-secondary">Review Answers</button>
                </div>
            </div>
        `;
        
        // Update progress
        progressBar.style.width = '100%';
        progressBar.setAttribute('aria-valuenow', 100);
        
        // Add review button listener
        document.getElementById('review-button').addEventListener('click', showReviewScreen);
        
        // Update navigation
        prevButton.disabled = false;
        nextButton.style.display = 'none';
        submitButton.style.display = 'block';
    }
    
    // Show the review screen
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
                            '<p>A copy of your completed form has been emailed to you.</p>' : 
                            '<p>Note: We were unable to email a copy of your form.</p>'}
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
    
    // Event listeners for navigation
    prevButton.addEventListener('click', function() {
        if (currentQuestionIndex > 0) {
            currentQuestionIndex--;
            renderQuestion();
            updateNavigation();
            saveProgress();
        }
    });
    
    nextButton.addEventListener('click', function() {
        const question = questions[currentQuestionIndex];
        const questionId = question.id;
        
        // Validate required field
        if (question.required) {
            const value = answers[questionId];
            
            if (!value || (Array.isArray(value) && value.length === 0)) {
                // Show validation message
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
                    
                    return;
                }
            }
        }
        
        if (currentQuestionIndex < questions.length) {
            currentQuestionIndex++;
            renderQuestion();
            updateNavigation();
            saveProgress();
        }
    });
    
    saveButton.addEventListener('click', saveProgress);
    
    submitButton.addEventListener('click', submitForm);
    
    // Auto-save every 30 seconds
    const autoSaveInterval = setInterval(saveProgress, 30000);
    
    // Clean up interval when leaving the page
    window.addEventListener('beforeunload', function() {
        clearInterval(autoSaveInterval);
    });
    
    // Initialize form
    initForm();
});
