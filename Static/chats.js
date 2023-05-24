function sendMessage(message) {
    event.preventDefault(); 

    var messageInput = document.getElementById('message-input');
    var message = messageInput.value;

    var sendingUserInput = document.getElementById('sending-user');
    var sendingUser = sendingUserInput.value;
    var receivingUserInput = document.getElementById('receiving-user');
    var receivingUser = receivingUserInput.value;

    $.ajax({
      url: `/send_message/${sendingUser}/${receivingUser}/`,
      type: 'POST',
      data: { 
        message: message,
        sendingUser: sendingUser,
        receivingUser: receivingUser},
        success: function(response) {
        console.log('Message sent successfully:', response);
        var chatMessagesContainer = document.getElementById('latest-messages-container');
        var newMessageHTML = '<div class="card">' +
          '<p>' + sendingUser + ': ' + message + '</p>' +
          '<p>' + response.message + '</p>' +
          '</div>';
        chatMessagesContainer.innerHTML += newMessageHTML;

      // Clear the message input
      messageInput.value = '';
      },
      error: function(xhr, status, error) {
        console.error('Error sending message:', error);
      }
    });
}

function receiveLatestMessage(sendingUser, receivingUser) {
  $.ajax({
    url: `/receive_latest_message/${sendingUser}/${receivingUser}/`,
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
      receiveLatestMessage(sendingUser, receivingUser);
    },
    error: function(xhr, status, error) {
      console.error('Error receiving latest message:', error);
    }
  });
}
receiveLatestMessage(sendingUser, receivingUser)

function isMessagePresent(messageHTML) {
    var containerHTML = $('#latest-messages-container').html();
    return containerHTML.includes(messageHTML);
}