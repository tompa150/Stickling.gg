function sendMessage(message) {
    $.ajax({
      url: `/send_message/${username}/${recieving_user}/`,
      type: 'POST',
      data: { 
        message: message,
        sendingUser: sendingUser,
        receivingUser: receivingUser},
      success: function(response) {
        console.log('Message sent successfully:', response);
      },
      error: function(xhr, status, error) {
        console.error('Error sending message:', error);
      }
    });
  }


function receiveLatestMessage() {
  $.ajax({
    url: `/receive_latest_message/${username}/${recieving_user}/`,
    type: 'GET',
    success: function(response) {
      var message = response;
      var messageHTML = '<div class="card">' +
        '<p>' + message.user + ': ' + message.message + '</p>' +
        '<p>' + message.timestamp + '</p>' +
        '</div>';

      // Check if the latest message is already present in the container
      if (!isMessagePresent(messageHTML)) {
        // Append the latest message to the container
        $('#latest-messages-container').html(messageHTML);
      }

      // Call the function again to continue receiving latest messages
      receiveLatestMessage();
    },
    error: function(xhr, status, error) {
      console.error('Error receiving latest message:', error);
    }
  });
}

function isMessagePresent(messageHTML) {
    var containerHTML = $('#latest-messages-container').html();
    return containerHTML.includes(messageHTML);
  }