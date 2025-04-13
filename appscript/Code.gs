function onGmailCompose(e) {
  var accessToken = e.gmail.accessToken;
  var draftId = e.gmail.draftId;

  // Call Flask backend to analyze draft
  var response = UrlFetchApp.fetch('https://your-flask-app.com/api/analyze', {
    method: 'POST',
    payload: JSON.stringify({ draft_id: draftId }),
    headers: { 'Authorization': 'Bearer ' + accessToken }
  });
  var data = JSON.parse(response.getContentText());

  // Build UI card
  var card = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle('Email Refiner'));

  var section = CardService.newCardSection()
    .addWidget(CardService.newTextParagraph().setText('Intent: ' + data.context_info.intent))
    .addWidget(CardService.newTextParagraph().setText('Tone: ' + data.context_info.tone))
    .addWidget(CardService.newTextInput().setFieldName('instruction').setTitle('Refine Tone'))
    .addWidget(CardService.newButtonSet()
      .addButton(CardService.newTextButton()
        .setText('Refine')
        .setOnClickAction(CardService.newAction()
          .setFunctionName('refineEmail'))));

  card.addSection(section);
  return card.build();
}

function refineEmail(e) {
  var instruction = e.formInput.instruction;
  var response = UrlFetchApp.fetch('https://your-flask-app.com/api/refine', {
    method: 'POST',
    payload: JSON.stringify({
      email_data: e.formInput.email_data,
      context_info: e.formInput.context_info,
      user_instruction: instruction
    })
  });
  var data = JSON.parse(response.getContentText());

  // Update card with refined text
  var card = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle('Email Refiner'))
    .addSection(CardService.newCardSection()
      .addWidget(CardService.newTextParagraph().setText(data.refined_text))
      .addWidget(CardService.newButtonSet()
        .addButton(CardService.newTextButton()
          .setText('Apply to Draft')
          .setOnClickAction(CardService.newAction()
            .setFunctionName('applyToDraft')))));
  return card.build();
}

function applyToDraft(e) {
  // Update Gmail draft via API (handled server-side)
}