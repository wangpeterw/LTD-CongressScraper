 /*
 * This is the Javascript file that makes requests to our controller.
 * We have prepared one API that makes requests in two unique ways
 * The filter option requests for data to be displayed and the download option 
 * requests for data to be in a downloadable form
 */

$('#filter-btn').click(function() {
	//Reload the page to display the new data.
	//You could optionally work with Ajax
	window.location.href="/query?surname=" + $("#surname").val() + "&firstname=" + $("#firstname").val() +
	"&district=" + $("#district").val() + "&state=" + $("#state").val() + "&party=" + $("#party").val() + "&type=" + $("#type").val() +
	"&month=" + $("#month").val() + "&day=" + $("#day").val() + "&year=" + $("#year").val()
});

$('#download-btn').click(function() {
	window.location.href="/query?format=csv&surname=" + $("#speaker").val() + "&year=" + $("#year").val()
});