document.addEventListener('DOMContentLoaded', function() {
  console.log("DOMContentLoaded triggered");

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => {
    console.log("Inbox button clicked");
    load_mailbox('inbox');
  });
  document.querySelector('#sent').addEventListener('click', () => {
    console.log("Sent button clicked");
    load_mailbox('sent');
  });
  document.querySelector('#archived').addEventListener('click', () => {
    console.log("Archive button clicked");
    load_mailbox('archive');
  });
  document.querySelector('#compose').addEventListener('click', () => {
    console.log("Compose button clicked");
    compose_email();
  });

  console.log("HELLO FROM inbox.js: I'm loaded!");
  document.addEventListener('DOMContentLoaded', function() {
    console.log("DOMContentLoaded triggered in inbox.js");
});

  // By default, load the inbox
  console.log("Loading inbox by default");
  load_mailbox('inbox');

  // MIN EGEN KODE
  document.querySelector("#compose-form").onsubmit = function(event) {
    event.preventDefault(); // Forhindrer siden i at genindlæses
    console.log("Submitting compose form");

    const recipients = document.querySelector("#compose-recipients").value;
    const subject = document.querySelector("#compose-subject").value;
    const body = document.querySelector("#compose-body").value;

    console.log(`Recipients: ${recipients}, Subject: ${subject}, Body: ${body}`);

    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          recipients: recipients,
          subject: subject,
          body: body
      })
    })
    .then(response => response.json())
    .then(result => {
        console.log("Result from POST /emails:", result);

        if (result.error) {
            alert(result.error);
        } else {
          console.log("Email sent successfully, loading 'sent' mailbox");
          load_mailbox('sent');
        }
    });

    // return false;  // Kan evt. bruges i stedet for event.preventDefault()
  };  
});

function compose_email() {
  console.log("compose_email() called");

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  console.log(`load_mailbox() called with mailbox: ${mailbox}`);

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  console.log(`Fetching /emails/${mailbox}`);
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    console.log("Response from GET /emails/", mailbox, ":", emails);

    if (emails.error) {
      alert(emails.error);
    } else {
      // Ryd op i #emails-view (husk at vi allerede har sat en <h3>)
      // men hvis du vil tilføje mere, kan du bruge += i stedet for at overskrive alt.
      emails.forEach(email => {
        // Vælg hvad du vil vise afhængigt af mailbox (Inbox, Sent, osv.)
        // Til Inbox giver det mening at vise FROM, i Sent giver det mening at vise TO osv.
        // Her viser vi bare alt for eksemplets skyld:
        document.querySelector('#emails-view').innerHTML += `
          <div style="border: 1px solid #ccc; padding: 10px; margin: 5px;">
            <strong>From:</strong> ${email.sender} <br>
            <strong>To:</strong> ${email.recipients} <br>
            <strong>Subject:</strong> ${email.subject} <br>
            <strong>Body:</strong> ${email.body} <br>
          </div>
        `;
      });
    }
  })
  .catch(error => {
    console.log("Error fetching mailbox:", error);
  });
}
