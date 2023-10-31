document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Add event for the send email form
  document.querySelector('#compose-form').addEventListener('submit', function(event) {
    // Send email to /emails route via POST with the email as a body in JSON
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
      })
    })
    .then(response => response.json())
    .then(result => {
      console.log(result);

      // Alert user in case of error or confirmation message
      if (result['message'] != undefined) {
        alert(`${result['message']}`)
      } else {
        alert(`${result['error']}`)
      }
    })

    // Load user's sent mailbox and prevent default from being executed
    event.preventDefault();

    // Load user's inbox with delay to update mailbox
    setTimeout(function(){ load_mailbox('sent'); }, 1000);
  });
  
  // By default, load the inbox
  load_mailbox('inbox');

});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Show all emails, send a GET request to /emails/<mailbox>
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Iterate through all emails
    emails.forEach(email => {
      // Create div element for emails
      div = document.createElement('div');
      div.setAttribute('id', 'email');
      div.setAttribute('class', `read-${email['read']}`);

      // Create p element for adding the emails content
      p = document.createElement('p');

      // Add to p's innerHTML the info received from emails/<mailbox>
      p.innerHTML = 
        `<button class="email-box" onclick="load_email(${email['id']})">
          <span class="sender">${email['sender']}</span>
          <span class="subject">${email['subject']}</span>
          <span class="timestamp">${email['timestamp']}</span>
        </button>`;

      // Append this <p> to <div>(emails)
      div.append(p);

      // Add div(emails) to div(emails-view)
      document.querySelector('#emails-view').append(div);

    });
  })

}

function load_email(email_id) {
  // Create and add all elements to the email-view
  const email_view = document.querySelector('#email-view');

  // Empty the contents in email_view first
  email_view.innerHTML = '';

  // Show the email and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Mark this email as read
  fetch(`emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  })

  // Fetch email from id
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {

    const sender = document.createElement('p');
    sender.innerHTML = `<span>From:</span> ${email['sender']}`;
    email_view.append(sender);

    const recipients = document.createElement('p');
    recipients.innerHTML = `<span>To:</span> ${email['recipients']}`;
    email_view.append(recipients);

    const subject = document.createElement('p');
    subject.innerHTML = `<span>Subject:</span> ${email['subject']}`;
    email_view.append(subject)

    const timestamp = document.createElement('p');
    timestamp.innerHTML = `<span>Timestamp:</span> ${email['timestamp']}`;
    email_view.append(timestamp)

    // Add event listener for when this button is clicked
    const reply = document.createElement('button');
    reply.setAttribute('class', 'btn btn-dark');
    reply.innerHTML = 'Reply';

    reply.addEventListener('click', () => {
      // Show compose view and hide other views
      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#email-view').style.display = 'none';
      document.querySelector('#compose-view').style.display = 'block';

      // pre-fill compose fields
      document.querySelector('#compose-recipients').value = `${email['sender']}`;
      document.querySelector('#compose-subject').value = `${email['subject']}`.startsWith('Re:') ? `${email['subject']}` : `Re: ${email['subject']}`;
      document.querySelector('#compose-body').value = `On ${email['timestamp']} ${email['sender']} wrote: ${email['body']}`;
    });

    email_view.append(reply)

    // Check if user is the same as the current user (compose-sender)
    // Only load the archive/unarchive button if that is
    // not part of the 'sent' inbox
    const user = document.querySelector('#compose-sender').value;

    // This will ensure the only emails with the archive button
    // are not those sent by the user themselves
    if (user !== `${email['sender']}`) {
      const archive = document.createElement('button');
      archive.setAttribute('class', 'btn btn-sm btn-outline-primary');
      archive.innerHTML = email['archived'] ? 'Unarchive' : 'Archive';

    // Add event for archive/unarchive button being clicked
    archive.addEventListener('click', function() {
      // If archived, unarchive and vice-versa
      fetch(`emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
          archived: email['archived'] ? false : true
        })
      })

      // Load user's inbox with delay to update mailbox
      setTimeout(function(){ load_mailbox('inbox'); }, 100);
    });

    email_view.append(archive);

    }
    

    hr = document.createElement('hr');
    email_view.append(hr);

    body = document.createElement('p');
    body.innerHTML = `${email['body']}`;
    email_view.append(body);

  });

}