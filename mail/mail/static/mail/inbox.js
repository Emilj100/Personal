document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  // MIN EGEN KODE
  document.querySelector("#compose-form").onsubmit = function(event) {
  
    const recipients = document.querySelector("#compose-recipients").value;
    const subject = document.querySelector("#compose-subject").value;
    const body = document.querySelector("#compose-body").value;
  
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
        console.log(result);

        if(result.error) {
            alert(result.error);
        } else {
          load_mailbox('sent');
        }
    });

    return false;
  };  
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-detail').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-detail').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Print emails
    console.log(emails);

    if (emails.error) {
      alert(emails.error);
    } else {
      emails.forEach(email => {
        const element = document.createElement('div');
        element.innerHTML = `
          <div class="card mb-3">
            <div class="card-header">
              <strong>Subject:</strong> ${email.subject}
            </div>
            <div class="card-body" style="${email.read ? 'background-color: #f7f7f7;' : 'background-color: white;'}">
              <p class="card-text"><strong>To:</strong> ${email.recipients}</p>
              <p class="card-text"><strong>Body:</strong> ${email.body}</p>
            </div>
          </div>
        `;
        element.addEventListener('click', function() {
            email_detail(email.id, mailbox)
        });
        document.querySelector('#emails-view').append(element);
      });      
    }    
  });
}

function email_detail(email_id, mailbox) {
  // Skjul de andre views og vis email-detail
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-detail').style.display = 'block';

  // Ryd eventuelt tidligere indhold
  document.querySelector('#email-detail').innerHTML = '';

  fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
      console.log(email);
      let archiveText;
      if (email.archived) {
        archiveText = "Unarchive";
      } else {
        archiveText = "Archive";
      }
      let buttons;
      if (mailbox !== 'sent') {
        buttons = `
          <button class="btn btn-primary reply-btn">Reply</button>
          <button class="btn btn-primary archive-btn">${archiveText}</button>
        `;
      } else {
        buttons = `<button class="btn btn-primary reply-btn">Reply</button>`;
      }
            

      // Markér email som læst (husk at tilføje PUT-anmodningen)
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
          read: true
        })
      });

      const element = document.createElement('div');
      element.innerHTML = `
        <div class="card mb-3">
          <div class="card-header">
            <h4>${email.subject}</h4>
          </div>
          <div class="card-body">
            <p><strong>From:</strong> ${email.sender}</p>
            <p><strong>To:</strong> ${email.recipients}</p>
            <p><strong>Timestamp:</strong> ${email.timestamp}</p>
            <hr>
            <p>${email.body}</p>
          </div>
          <div class="card-footer">
            ${buttons}
          </div>
        </div>
      `;
      document.querySelector('#email-detail').append(element);
      element.querySelector('.reply-btn').addEventListener('click', () => {
        reply(email);
      });
      element.querySelector('.archive-btn').addEventListener('click', () => {
        archive(email.id, email.archived);
      });
    });
}

function archive(id, archivedStatus) {

  let status;
  if (archivedStatus) {
    status = false;
  } else {
    status = true;
  }
  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: status
    })
  })
  .then(() => {
    load_mailbox('inbox');
  });
}

function reply(email) {

  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-detail').style.display = 'none';

  let subject = email.subject;
  if (!subject.startsWith("Re:")) {
  subject = `Re: ${subject}`;
  }

  document.querySelector('#compose-recipients').value = email.sender;
  document.querySelector('#compose-subject').value = subject;
  document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;

}