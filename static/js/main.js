$( document ).ready(function(){
	$('.carousel').carousel();
	$(".button-collapse").sideNav();
	$('.carousel').carousel('next');
	$('.carousel').carousel('next', 3); // Move next n times.
	// Previous slide
	$('.carousel').carousel('prev');
	$('.carousel').carousel('prev', 4); // Move prev n times.
	// Set to nth slide
	$('.carousel').carousel('set', 4);
	$('.datepicker').pickadate({
    selectMonths: true, // Creates a dropdown to control month
    selectYears: 50 // Creates a dropdown of 15 years to control year
  });
	$(document).ready(function() {
    $('select').material_select();
  });
	
  $(document).ready(function(){
    // the "href" attribute of .modal-trigger must specify the modal ID that wants to be triggered
    $('.modal').modal();
  });
  $(document).ready(function() {
    Materialize.updateTextFields();
  });
})

