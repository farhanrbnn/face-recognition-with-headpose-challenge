var socket = io('https://0.0.0.0:5000');

socket.on('connect', function(){
	console.log('connected', socket.connected);

});

socket.on('name', function(msg){
	$('#greetings').append(msg.oi);

});

socket.on('pose', function(msg){
	$('#pose').append(msg.pose);

});

socket.on('access', function(){
	$('#granted').show();

});

socket.on('reload', function(){
	location.reload();
});