var socket = io();
socket.on('connect', function() {
    socket.emit('connections', 'Connection successful');
    /*
       For debugging purposes this prints in python when someone connects
    */
});

socket.on('message', function(data) {
    /* Handles incoming message sent from server*/
    var message_list = document.getElementById('message_list');
    var li = document.createElement('li');
    li.className = 'list-group-item';
    var user = data['username']
    var msg = data['msg']
    var final = user + ": " + msg
    li.appendChild(document.createTextNode(final));
    message_list.appendChild(li);
});


