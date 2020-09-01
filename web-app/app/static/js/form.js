var count = 0;
var data = new Object();

var arr_image = [];

// set display dmension and format 
Webcam.set({
	width: 300,
	height: 300,
	image_format: 'jpeg',
	jpeg_quality: 120

	});

// set the display
Webcam.attach( '#webcam' );

function take_snapshot(){
	Webcam.snap(function(data_uri) {
		// $(".image-tag").val(data_uri);
		count ++;

		if(count == 1){
			$(".image-tag-one").val(data_uri);
			arr_image.push(data_uri);
		};
		if(count == 2){
			$(".image-tag-two").val(data_uri);
			arr_image.push(data_uri);		
		};
		if(count == 3){
			$(".image-tag-three").val(data_uri);
			arr_image.push(data_uri);		
		};
	});
	
	if (arr_image.length == 3){
		data.images = arr_image;

		return data;
	};
};

function getName(){
	var nama = $('#nama').val();
	data.name = nama;

	$.ajax({
			url:'https://0.0.0.0:5000/employees/encode',
			type:'POST',
			contentType: 'application/json',
			data:JSON.stringify(data)

		}).done(function(){
			console.log(data);

		});	
};