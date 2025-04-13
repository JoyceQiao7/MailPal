async function analyzeDraft() {
    const draftId = document.getElementById('draft-id').value;
    const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft_id: draftId })
    });
    const data = await response.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    document.getElementById('subject').innerText = data.email_data.subject;
    document.getElementById('content').innerText = data.email_data.content;
    document.getElementById('intent').innerText = data.context_info.intent;
    document.getElementById('tone').innerText = data.context_info.tone;
    document.getElementById('context-section').style.display = 'block';
    window.emailData = data.email_data;
    window.contextInfo = data.context_info;
}

async function refineEmail() {
    const userInstruction = document.getElementById('user-instruction').value;
    const response = await fetch('/api/refine', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email_data: window.emailData,
            context_info: window.contextInfo,
            user_instruction: userInstruction
        })
    });
    const data = await response.json();

    document.getElementById('refined-text').innerText = data.refined_text;
    document.getElementById('refined-section').style.display = 'block';
}

async function submitFeedback() {
    const feedback = document.getElementById('feedback').value;
    await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback })
    });
    alert('Feedback submitted!');
}